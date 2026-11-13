from pathlib import Path
from urllib.parse import parse_qs, unquote, urlparse

from django.core.exceptions import ImproperlyConfigured


def parse_bool(value, default=False):
    if value is None:
        return default
    return value.strip().lower() in {'1', 'true', 'yes', 'on'}


def parse_csv(value, name):
    values = [item.strip() for item in (value or '').split(',') if item.strip()]
    if any('*' in item for item in values):
        raise ImproperlyConfigured(f'{name} não pode conter curingas.')
    return values


def parse_allowed_hosts(value):
    hosts = parse_csv(value, 'ALLOWED_HOSTS')
    if any(
        '://' in host
        or '/' in host
        or '?' in host
        or '#' in host
        or any(char.isspace() for char in host)
        for host in hosts
    ):
        raise ImproperlyConfigured('ALLOWED_HOSTS deve conter nomes de host, sem esquema ou caminho.')
    return hosts


def parse_origins(value, name):
    origins = parse_csv(value, name)
    for origin in origins:
        parsed = urlparse(origin)
        try:
            valid = (
                parsed.scheme in {'http', 'https'}
                and parsed.hostname is not None
                and parsed.username is None
                and parsed.password is None
                and parsed.path in {'', '/'}
                and not parsed.params
                and not parsed.query
                and not parsed.fragment
            )
            parsed.port
        except ValueError:
            valid = False
        if not valid:
            raise ImproperlyConfigured(
                f'{name} deve conter origens completas, como https://app.exemplo.com.'
            )
    return origins


def validate_production_origins(origins, debug):
    if not debug and any(not origin.startswith('https://') for origin in origins):
        raise ImproperlyConfigured('Origens externas de produção devem usar HTTPS.')


def get_secret_key(value, debug):
    value = value.strip() if value else ''
    if debug:
        return value or 'django-insecure-dev-key'

    known_placeholders = {
        'django-insecure-dev-key',
        'chave-apenas-para-desenvolvimento-local',
        'troque-esta-chave-por-uma-segura',
        'change-me',
        'your-secret-key',
    }
    if (
        not value
        or value.lower() in known_placeholders
        or value.lower().startswith('django-insecure-')
    ):
        raise ImproperlyConfigured('SECRET_KEY deve ser exclusiva e segura quando DEBUG=False.')
    return value


def database_config(database_url, base_dir, debug):
    parsed = urlparse(database_url)
    if parsed.scheme in {'postgres', 'postgresql'}:
        database_name = unquote(parsed.path.lstrip('/'))
        if not database_name or not parsed.hostname:
            raise ImproperlyConfigured('DATABASE_URL precisa incluir banco e host PostgreSQL.')
        query = parse_qs(parsed.query)
        sslmode = query.get('sslmode', [None])[-1]
        if not sslmode:
            sslmode = 'prefer' if debug else 'require'
        if not debug and sslmode not in {'require', 'verify-ca', 'verify-full'}:
            raise ImproperlyConfigured(
                'DATABASE_URL deve usar sslmode=require, verify-ca ou verify-full em produção.'
            )
        supported_query_parameters = {
            'sslmode',
            'sslrootcert',
            'sslcert',
            'sslkey',
            'sslpassword',
            'sslcrl',
            'sslcrldir',
            'connect_timeout',
            'application_name',
        }
        unsupported_parameters = set(query) - supported_query_parameters
        if unsupported_parameters:
            raise ImproperlyConfigured(
                'Parâmetros não suportados em DATABASE_URL: '
                + ', '.join(sorted(unsupported_parameters))
                + '.'
            )
        duplicated_parameters = [
            key for key, values in query.items() if len(values) != 1
        ]
        if duplicated_parameters:
            raise ImproperlyConfigured(
                'Parâmetros repetidos em DATABASE_URL: '
                + ', '.join(sorted(duplicated_parameters))
                + '.'
            )
        config = {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': database_name,
            'USER': unquote(parsed.username or ''),
            'PASSWORD': unquote(parsed.password or ''),
            'HOST': parsed.hostname,
            'PORT': str(parsed.port or 5432),
            'OPTIONS': {'sslmode': sslmode},
        }
        for key in supported_query_parameters - {'sslmode'}:
            if key in query:
                config['OPTIONS'][key] = query[key][-1]
        return config

    if parsed.scheme == 'sqlite':
        if not debug:
            raise ImproperlyConfigured('Produção deve usar PostgreSQL em DATABASE_URL.')
        path = unquote(parsed.path)
        if path in {'', '/:memory:'}:
            database_name = ':memory:'
        elif path.startswith('//'):
            database_name = path[1:]
        else:
            database_name = path.lstrip('/')
            if not Path(database_name).is_absolute():
                database_name = str(base_dir / database_name)
        return {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': database_name,
        }

    raise ImproperlyConfigured('DATABASE_URL deve usar postgresql:// ou sqlite://.')
