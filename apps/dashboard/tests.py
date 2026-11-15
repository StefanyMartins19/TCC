import json
from io import StringIO
from unittest.mock import Mock, patch

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.core.management import call_command
from django.core.management.base import CommandError
from django.db.backends.postgresql.base import DatabaseWrapper
from django.test import TestCase
from django.urls import reverse

from dashboard.api import _observacoes_oficiais
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
            nome='Sistema Gerenciador de Séries Temporais (SGS)',
            instituicao='Banco Central do Brasil (BCB)',
            tipo_origem='API',
            url_origem='https://dadosabertos.bcb.gov.br/',
        )
        self.indicador = Indicador.objects.create(
            nome='Inadimplência da carteira de crédito de pessoas físicas — BCB SGS 21084',
            nome_curto='Inadimplência PF',
            descricao='Série oficial do BCB.',
            categoria='inadimplência',
            unidade_medida='%',
            periodicidade='mensal',
            codigo_fonte='SGS 21084',
            abrangencia='Brasil',
            fonte=self.fonte,
        )
        self.brasil = Localidade.objects.create(codigo_ibge='00', nome='Brasil', tipo='Brasil')
        self.saopaulo = Localidade.objects.create(
            codigo_ibge='35',
            nome='São Paulo',
            tipo='Estado',
            uf='SP',
        )
        self.periodo = Periodo.objects.create(ano=2024, mes=2, data_referencia='2024-02-01')
        self.valor = ValorIndicador.objects.create(
            indicador=self.indicador,
            fonte=self.fonte,
            localidade=self.brasil,
            periodo=self.periodo,
            valor='8.500000',
            unidade_original='%',
            metadados={
                'simulado': False,
                'origem': 'Banco Central do Brasil — BCData/SGS',
                'codigo_sgs': 21084,
                'url_fonte': (
                    'https://dadosabertos.bcb.gov.br/dataset/'
                    '21084-inadimplencia-da-carteira-de-credito---pessoas-fisicas---total'
                ),
                'url_consulta': (
                    'https://api.bcb.gov.br/dados/serie/bcdata.sgs.21084/dados'
                    '?formato=json&dataInicial=01%2F02%2F2024&dataFinal=29%2F02%2F2024'
                ),
                'data_consulta': '2024-03-01T00:00:00+00:00',
                'data_referencia': '2024-02-01',
                'periodicidade': 'mensal',
                'unidade_medida': '%',
                'abrangencia_geografica': 'Brasil',
            },
        )

    def test_indicator_catalog_exposes_metadata_and_latest_official_value(self):
        response = self.client.get(reverse('api_indicadores'))

        self.assertEqual(response.status_code, 200)
        item = response.json()['results'][0]
        self.assertEqual(item['code'], 'SGS 21084')
        self.assertEqual(item['source']['institution'], 'Banco Central do Brasil (BCB)')
        self.assertEqual(item['latest'], {'value': '8.500000', 'date': '2024-02-01'})
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
        self.assertEqual(row['value'], '8.500000')
        self.assertEqual(row['locality'], 'Brasil')
        self.assertEqual(row['metadata']['codigo_sgs'], 21084)

        filtered = self.client.get(url, {'data_inicio': '2024-03-01'})
        self.assertEqual(filtered.json()['count'], 0)

    def test_api_rejects_simulated_and_unverified_observations(self):
        self.valor.metadados = {'simulado': False}
        self.valor.save(update_fields=['metadados'])
        response = self.client.get(reverse('api_observacoes'))
        self.assertEqual(response.json()['count'], 0)

    def test_national_bcb_observation_is_available_for_brazil_but_not_uf(self):
        response = self.client.get(
            reverse('api_observacoes'),
            {'indicador': self.indicador.pk, 'localidade': self.brasil.pk},
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['count'], 1)
        self.assertEqual(response.json()['results'][0]['locality'], 'Brasil')

        response = self.client.get(reverse('api_observacoes'), {'uf': 'sp'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['count'], 0)

        invalid = self.client.get(reverse('api_observacoes'), {'uf': 'São'})
        self.assertEqual(invalid.status_code, 400)

    def test_all_public_endpoints_include_only_verified_national_bcb_series(self):
        for codigo, unidade in ((25462, '% a.m.'), (29265, '%')):
            indicador = Indicador.objects.create(
                nome=f'Série BCB SGS {codigo}',
                categoria='inadimplência',
                unidade_medida=unidade,
                periodicidade='mensal',
                codigo_fonte=f'SGS {codigo}',
                abrangencia='Brasil',
                fonte=self.fonte,
            )
            ValorIndicador.objects.create(
                indicador=indicador,
                fonte=self.fonte,
                localidade=self.brasil,
                periodo=self.periodo,
                valor='1.250000',
                unidade_original=unidade,
                metadados={
                    'simulado': False,
                    'origem': 'Banco Central do Brasil — BCData/SGS',
                    'codigo_sgs': codigo,
                    'url_fonte': f'https://dadosabertos.bcb.gov.br/dataset/{codigo}',
                    'url_consulta': (
                        f'https://api.bcb.gov.br/dados/serie/bcdata.sgs.{codigo}/dados'
                        '?formato=json'
                    ),
                    'unidade_medida': unidade,
                    'abrangencia_geografica': 'Brasil',
                },
            )

        periodo_simulado = Periodo.objects.create(
            ano=2024,
            mes=3,
            data_referencia='2024-03-01',
        )
        serie_bcb_25462 = ValorIndicador.objects.get(indicador__codigo_fonte='SGS 25462')
        metadados_simulados = serie_bcb_25462.metadados.copy()
        metadados_simulados['simulado'] = True
        ValorIndicador.objects.create(
            indicador=serie_bcb_25462.indicador,
            fonte=self.fonte,
            localidade=self.brasil,
            periodo=periodo_simulado,
            valor='99.000000',
            unidade_original=serie_bcb_25462.unidade_original,
            metadados=metadados_simulados,
        )

        responses = {
            'indicadores': self.client.get(reverse('api_indicadores')),
            'localidades': self.client.get(reverse('api_localidades')),
            'fontes': self.client.get(reverse('api_fontes')),
            'observacoes': self.client.get(reverse('api_observacoes')),
        }
        for nome, response in responses.items():
            with self.subTest(endpoint=nome):
                self.assertEqual(response.status_code, 200)

        indicadores = responses['indicadores'].json()['results']
        self.assertEqual(
            {item['code'] for item in indicadores if item['observation_count']},
            {'SGS 21084', 'SGS 25462', 'SGS 29265'},
        )
        fonte = responses['fontes'].json()['results'][0]
        self.assertEqual(fonte['observation_count'], 3)
        brasil = next(
            item
            for item in responses['localidades'].json()['results']
            if item['type'] == 'Brasil'
        )
        self.assertEqual(brasil['observation_count'], 3)
        observacoes = responses['observacoes'].json()
        self.assertEqual(observacoes['count'], 3)
        self.assertEqual(
            {item['code'] for item in observacoes['results']},
            {'SGS 21084', 'SGS 25462', 'SGS 29265'},
        )
        sem_correspondencias = self.client.get(
            reverse('api_observacoes'),
            {'indicador': 999999},
        )
        self.assertEqual(sem_correspondencias.status_code, 200)
        self.assertEqual(sem_correspondencias.json()['count'], 0)

    def test_official_observation_query_compiles_json_locality_as_postgresql_text(self):
        connection = DatabaseWrapper(
            {
                'ENGINE': 'django.db.backends.postgresql',
                'NAME': 'copilot_json_api_test_only',
                'USER': 'test_only',
                'PASSWORD': 'test_only',
                'HOST': '127.0.0.1',
                'PORT': '1',
                'OPTIONS': {},
                'TIME_ZONE': None,
                'CONN_MAX_AGE': 0,
                'CONN_HEALTH_CHECKS': False,
                'AUTOCOMMIT': True,
                'ATOMIC_REQUESTS': False,
            },
            alias='disposable_sql_compile_only',
        )
        try:
            sql, _ = _observacoes_oficiais().query.get_compiler(
                connection=connection,
            ).as_sql()
        finally:
            connection.close()

        self.assertIn(
            '"metadados" ->> %s) = ("localidades_localidade"."codigo_ibge")',
            sql,
        )

    def test_approved_state_observation_is_limited_to_its_uf_and_period(self):
        fonte = FonteDados.objects.create(
            nome='Pesquisa Nacional por Amostra de Domicílios Contínua (PNAD Contínua)',
            instituicao='Instituto Brasileiro de Geografia e Estatística (IBGE)',
            tipo_origem='API',
            url_origem='https://sidra.ibge.gov.br/',
        )
        indicador = Indicador.objects.create(
            nome='Taxa de desocupação — PNAD Contínua',
            categoria='emprego/desemprego',
            unidade_medida='%',
            periodicidade='trimestral',
            codigo_fonte='PNAD Contínua',
            abrangencia='Brasil e UFs, conforme a série oficial.',
            fonte=fonte,
        )
        periodo = Periodo.objects.create(
            ano=2024,
            trimestre=1,
            data_referencia='2024-03-31',
        )
        ValorIndicador.objects.create(
            indicador=indicador,
            fonte=fonte,
            localidade=self.saopaulo,
            periodo=periodo,
            valor='7.500000',
            unidade_original='%',
            metadados={
                'simulado': False,
                'origem': 'IBGE/SIDRA',
                'codigo_tabela': 'TESTE',
                'codigo_variavel': 'TESTE',
                'codigo_localidade': 35,
                'url_fonte': 'https://sidra.ibge.gov.br/tabela/TESTE',
                'url_consulta': 'https://apisidra.ibge.gov.br/values/t/TESTE',
                'data_consulta': '2024-04-01T00:00:00+00:00',
                'periodicidade': 'trimestral',
                'unidade_medida': '%',
                'abrangencia_geografica': 'Brasil e UFs',
            },
        )

        url = reverse('api_observacoes')
        filtros_validos = {
            'indicador': indicador.pk,
            'uf': 'SP',
            'data_inicio': '2024-01-01',
            'data_fim': '2024-03-31',
        }
        response = self.client.get(url, filtros_validos)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['count'], 1)
        self.assertEqual(response.json()['results'][0]['uf'], 'SP')

        response_outra_uf = self.client.get(url, {**filtros_validos, 'uf': 'RJ'})
        self.assertEqual(response_outra_uf.json()['count'], 0)
        response_outro_periodo = self.client.get(
            url,
            {**filtros_validos, 'data_fim': '2024-03-30'},
        )
        self.assertEqual(response_outro_periodo.json()['count'], 0)

    def test_simulated_bcb_observation_is_excluded_despite_matching_provenance(self):
        self.valor.metadados['simulado'] = True
        self.valor.save(update_fields=['metadados'])

        response = self.client.get(
            reverse('api_observacoes'),
            {'indicador': self.indicador.pk, 'localidade': self.brasil.pk},
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['count'], 0)

    def test_api_rejects_invalid_date_range(self):
        invalid = self.client.get(
            reverse('api_observacoes'),
            {'data_inicio': '2024-03-01', 'data_fim': '2024-02-01'},
        )
        self.assertEqual(invalid.status_code, 400)
