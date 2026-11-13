import json
from io import StringIO
from unittest.mock import Mock, patch

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.core.management import call_command
from django.core.management.base import CommandError
from django.test import TestCase
from django.urls import reverse

from fontes.models import FonteDados
from indicadores.models import Indicador, Periodo, ValorIndicador
from localidades.models import Localidade
from config.settings_helpers import (
    database_config,
    get_secret_key,
    parse_allowed_hosts,
    parse_origins,
    validate_production_origins,
)


class ProductionSettingsTests(TestCase):
    def test_local_defaults_keep_sqlite_and_static_files_configuration(self):
        self.assertEqual(settings.DATABASES['default']['ENGINE'], 'django.db.backends.sqlite3')
        self.assertIn('whitenoise.middleware.WhiteNoiseMiddleware', settings.MIDDLEWARE)
        self.assertEqual(
            settings.STORAGES['staticfiles']['BACKEND'],
            'django.contrib.staticfiles.storage.StaticFilesStorage',
        )
        self.assertTrue(settings.STATIC_ROOT.name == 'staticfiles')

    def test_postgres_url_decodes_credentials_and_requires_tls_in_production(self):
        config = database_config(
            'postgresql://user%40render:p%40ss@db.example.internal:5433/observatorio'
            '?connect_timeout=10',
            settings.BASE_DIR,
            debug=False,
        )

        self.assertEqual(config['ENGINE'], 'django.db.backends.postgresql')
        self.assertEqual(config['USER'], 'user@render')
        self.assertEqual(config['PASSWORD'], 'p@ss')
        self.assertEqual(config['PORT'], '5433')
        self.assertEqual(config['OPTIONS'], {'sslmode': 'require', 'connect_timeout': '10'})

    def test_postgres_url_respects_explicit_ssl_mode_and_sqlite_url(self):
        postgres = database_config(
            'postgres://user:secret@localhost/app?sslmode=verify-full'
            '&sslrootcert=%2Fetc%2Fssl%2Froot.crt&sslcert=%2Fetc%2Fssl%2Fclient.crt',
            settings.BASE_DIR,
            debug=False,
        )
        sqlite = database_config('sqlite:///local.sqlite3', settings.BASE_DIR, debug=True)

        self.assertEqual(
            postgres['OPTIONS'],
            {
                'sslmode': 'verify-full',
                'sslrootcert': '/etc/ssl/root.crt',
                'sslcert': '/etc/ssl/client.crt',
            },
        )
        self.assertEqual(sqlite['NAME'], str(settings.BASE_DIR / 'local.sqlite3'))
        with self.assertRaises(ImproperlyConfigured):
            database_config(
                'postgres://user:secret@localhost/app?sslmode=prefer',
                settings.BASE_DIR,
                debug=False,
            )
        with self.assertRaises(ImproperlyConfigured):
            database_config('sqlite:///production.sqlite3', settings.BASE_DIR, debug=False)
        with self.assertRaises(ImproperlyConfigured):
            database_config(
                'postgres://user:secret@localhost/app?unknown_option=value',
                settings.BASE_DIR,
                debug=False,
            )

    def test_production_secret_and_origins_are_validated(self):
        self.assertEqual(get_secret_key(None, debug=True), 'django-insecure-dev-key')
        with self.assertRaises(ImproperlyConfigured):
            get_secret_key(None, debug=False)
        self.assertEqual(
            get_secret_key('a-secure-production-secret', debug=False),
            'a-secure-production-secret',
        )
        for placeholder in (
            'django-insecure-custom-key',
            'chave-apenas-para-desenvolvimento-local',
            'troque-esta-chave-por-uma-segura',
            'change-me',
        ):
            with self.subTest(placeholder=placeholder), self.assertRaises(ImproperlyConfigured):
                get_secret_key(placeholder, debug=False)

        hosts = parse_allowed_hosts('api.example.com,localhost')
        self.assertEqual(hosts, ['api.example.com', 'localhost'])
        with self.assertRaises(ImproperlyConfigured):
            parse_allowed_hosts('*')

        origins = parse_origins('https://app.example.com', 'CORS_ALLOWED_ORIGINS')
        validate_production_origins(origins, debug=False)
        with self.assertRaises(ImproperlyConfigured):
            parse_origins('https://*.example.com', 'CORS_ALLOWED_ORIGINS')
        with self.assertRaises(ImproperlyConfigured):
            validate_production_origins(['http://app.example.com'], debug=False)


class DashboardViewsTests(TestCase):
    def setUp(self):
        fonte = FonteDados.objects.create(
            nome='Teste de fonte',
            instituicao='Instituição de Teste',
            tipo_origem='CSV',
            url_origem='https://example.com',
        )
        localidade = Localidade.objects.create(codigo_ibge='3550308', nome='São Paulo', tipo='Estado', uf='SP', regiao='Sudeste')
        indicador = Indicador.objects.create(
            nome='Taxa de inadimplência',
            categoria='inadimplência',
            unidade_medida='%',
            periodicidade='mensal',
        )
        periodo = Periodo.objects.create(ano=2025, mes=3, data_referencia='2025-03-01')
        ValorIndicador.objects.create(indicador=indicador, fonte=fonte, localidade=localidade, periodo=periodo, valor='8.5', unidade_original='%')

    def test_home_page_renders(self):
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Observatório Brasileiro da Inadimplência')

    def test_seed_demo_data_command(self):
        call_command('seed_demo_data')
        self.assertTrue(Indicador.objects.exists())
        self.assertTrue(FonteDados.objects.exists())
        self.assertTrue(ValorIndicador.objects.exists())


class PublicApiTests(TestCase):
    def setUp(self):
        self.fonte = FonteDados.objects.create(
            nome='Fonte pública',
            instituicao='Instituição pública',
            tipo_origem='API',
            url_origem='https://example.com',
        )
        self.indicador = Indicador.objects.create(
            nome='Indicador de teste',
            nome_curto='Teste',
            descricao='Série oficial de teste.',
            categoria='renda',
            unidade_medida='R$',
            periodicidade='mensal',
            codigo_fonte='Teste 1',
            abrangencia='Brasil',
            fonte=self.fonte,
        )
        self.brasil = Localidade.objects.create(codigo_ibge='00', nome='Brasil', tipo='Brasil')
        self.periodo = Periodo.objects.create(ano=2024, mes=2, data_referencia='2024-02-01')
        self.valor = ValorIndicador.objects.create(
            indicador=self.indicador,
            fonte=self.fonte,
            localidade=self.brasil,
            periodo=self.periodo,
            valor='1234.560000',
            unidade_original='R$',
            metadados={'simulado': False, 'codigo_externo': 'Teste 1'},
        )

    def test_indicator_catalog_exposes_metadata_and_latest_official_value(self):
        response = self.client.get(reverse('api_indicadores'))

        self.assertEqual(response.status_code, 200)
        item = response.json()['results'][0]
        self.assertEqual(item['code'], 'Teste 1')
        self.assertEqual(item['source']['institution'], 'Instituição pública')
        self.assertEqual(item['latest'], {'value': '1234.560000', 'date': '2024-02-01'})
        self.assertEqual(item['observation_count'], 1)

    def test_observations_support_combined_indicator_source_locality_and_date_filters(self):
        url = reverse('api_observacoes')
        response = self.client.get(
            url,
            {
                'indicador': self.indicador.pk,
                'fonte': self.fonte.pk,
                'localidade': self.brasil.pk,
                'data_inicio': '2024-01-01',
                'data_fim': '2024-02-29',
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['count'], 1)
        row = response.json()['results'][0]
        self.assertEqual(row['value'], '1234.560000')
        self.assertEqual(row['locality'], 'Brasil')
        self.assertEqual(row['metadata']['codigo_externo'], 'Teste 1')

        filtered = self.client.get(url, {'data_inicio': '2024-03-01'})
        self.assertEqual(filtered.json()['count'], 0)

    def test_api_excludes_simulated_observations_and_rejects_invalid_date_range(self):
        self.valor.metadados = {'simulado': True}
        self.valor.save(update_fields=['metadados'])
        response = self.client.get(reverse('api_observacoes'))
        self.assertEqual(response.json()['count'], 0)

        invalid = self.client.get(
            reverse('api_observacoes'),
            {'data_inicio': '2024-03-01', 'data_fim': '2024-02-01'},
        )
        self.assertEqual(invalid.status_code, 400)
