import json
from io import StringIO
from unittest.mock import Mock, patch

from django.core.management import call_command
from django.core.management.base import CommandError
from django.test import TestCase
from django.urls import reverse

from fontes.models import FonteDados
from indicadores.models import Indicador, Periodo, ValorIndicador
from localidades.models import Localidade


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
