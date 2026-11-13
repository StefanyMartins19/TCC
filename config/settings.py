from pathlib import Path
import os
import sys

from django.core.exceptions import ImproperlyConfigured
from dotenv import load_dotenv

from config.settings_helpers import (
    database_config,
    get_secret_key,
    parse_bool,
    parse_allowed_hosts,
    parse_origins,
    validate_production_origins,
)

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / '.env')

APPS_DIR = BASE_DIR / 'apps'
if str(APPS_DIR) not in sys.path:
    sys.path.insert(0, str(APPS_DIR))

DEBUG = parse_bool(os.getenv('DEBUG'), default=True)
SECRET_KEY = get_secret_key(os.getenv('SECRET_KEY'), DEBUG)
ALLOWED_HOSTS = parse_allowed_hosts(
    os.getenv('ALLOWED_HOSTS', 'localhost,127.0.0.1,[::1]'),
)
CORS_ALLOWED_ORIGINS = parse_origins(
    os.getenv('CORS_ALLOWED_ORIGINS'),
    'CORS_ALLOWED_ORIGINS',
)
CSRF_TRUSTED_ORIGINS = parse_origins(
    os.getenv('CSRF_TRUSTED_ORIGINS'),
    'CSRF_TRUSTED_ORIGINS',
)
if not DEBUG and not ALLOWED_HOSTS:
    raise ImproperlyConfigured('Defina ALLOWED_HOSTS com os domínios do serviço em produção.')
if not DEBUG and (not CORS_ALLOWED_ORIGINS or not CSRF_TRUSTED_ORIGINS):
    raise ImproperlyConfigured(
        'Defina CORS_ALLOWED_ORIGINS e CSRF_TRUSTED_ORIGINS com as origens do frontend em produção.'
    )
validate_production_origins((
    *CORS_ALLOWED_ORIGINS,
    *CSRF_TRUSTED_ORIGINS,
), DEBUG)

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'corsheaders',
    'dashboard',
    'indicadores',
    'localidades',
    'fontes',
    'importacao',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'

DATABASE_URL = os.getenv('DATABASE_URL', f'sqlite:///{BASE_DIR / "db.sqlite3"}')
DATABASES = {
    'default': database_config(DATABASE_URL, BASE_DIR, DEBUG),
}

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

LANGUAGE_CODE = 'pt-br'
TIME_ZONE = 'America/Sao_Paulo'
USE_I18N = True
USE_TZ = True

STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'
STORAGES = {
    'default': {
        'BACKEND': 'django.core.files.storage.FileSystemStorage',
    },
    'staticfiles': {
        'BACKEND': (
            'django.contrib.staticfiles.storage.StaticFilesStorage'
            if DEBUG
            else 'whitenoise.storage.CompressedManifestStaticFilesStorage'
        ),
    },
}
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

EMAIL_BACKEND = os.getenv('EMAIL_BACKEND', 'django.core.mail.backends.console.EmailBackend')
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

if not DEBUG:
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
    SECURE_SSL_REDIRECT = parse_bool(os.getenv('SECURE_SSL_REDIRECT'), default=True)
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_HSTS_SECONDS = int(os.getenv('SECURE_HSTS_SECONDS', '3600'))
    SECURE_HSTS_INCLUDE_SUBDOMAINS = parse_bool(
        os.getenv('SECURE_HSTS_INCLUDE_SUBDOMAINS'),
        default=False,
    )
    SECURE_HSTS_PRELOAD = parse_bool(os.getenv('SECURE_HSTS_PRELOAD'), default=False)
    SECURE_CONTENT_TYPE_NOSNIFF = True
