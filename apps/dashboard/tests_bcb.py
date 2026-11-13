import json
from datetime import date
from io import StringIO
from unittest.mock import Mock, patch

from django.core.management import call_command
from django.core.management.base import CommandError
from django.test import TestCase

from fontes.models import FonteDados
from importacao.models import ErroImportacao, ImportacaoDados
from indicadores.models import Indicador, ValorIndicador
from localidades.models import Localidade

from dashboard.management.commands.importar_dados_bcb import obter_serie_bcb


class BcbImportTests(TestCase):
    @staticmethod
    def api_response(observations):
        response = Mock()
        response.status = 200
        response.read.return_value = json.dumps(observations).encode('utf-8')
        response.__enter__ = Mock(return_value=response)
        response.__exit__ = Mock(return_value=False)
        return response

    def test_parser_rejects_duplicate_dates_and_invalid_payloads(self):
        duplicated = [
            {'data': '01/01/2024', 'valor': '4.11'},
            {'data': '01/01/2024', 'valor': '4.12'},
        ]
        with patch(
            'dashboard.management.commands.importar_dados_bcb.urlopen',
            return_value=self.api_response(duplicated),
        ):
            with self.assertRaises(CommandError):
                obter_serie_bcb(21084, date(2024, 1, 1), date(2024, 1, 31))

        invalid = [{'data': '01/01/2024', 'valor': 'NaN'}]
        with patch(
            'dashboard.management.commands.importar_dados_bcb.urlopen',
            return_value=self.api_response(invalid),
        ):
            with self.assertRaises(CommandError):
                obter_serie_bcb(21084, date(2024, 1, 1), date(2024, 1, 31))

    @patch('dashboard.management.commands.importar_dados_bcb.urlopen')
    def test_import_is_idempotent_and_preserves_official_provenance(self, urlopen):
        first = [{'data': '01/01/2024', 'valor': '4.11'}]
        urlopen.side_effect = [self.api_response(first)] * 3
        call_command(
            'importar_dados_bcb',
            data_inicial=date(2024, 1, 1),
            data_final=date(2024, 1, 31),
            stdout=StringIO(),
        )

        urlopen.side_effect = [
            self.api_response([{'data': '01/01/2024', 'valor': '4.21'}]),
            self.api_response([{'data': '01/01/2024', 'valor': '3.74'}]),
            self.api_response([{'data': '01/01/2024', 'valor': '27.18'}]),
        ]
        call_command(
            'importar_dados_bcb',
            data_inicial=date(2024, 1, 1),
            data_final=date(2024, 1, 31),
            stdout=StringIO(),
        )

        self.assertEqual(ValorIndicador.objects.count(), 3)
        indicador = Indicador.objects.get(codigo_fonte='SGS 21084')
        valor = ValorIndicador.objects.get(indicador=indicador)
        self.assertEqual(str(valor.valor), '4.210000')
        self.assertEqual(valor.localidade.nome, 'Brasil')
        self.assertEqual(valor.metadados['simulado'], False)
        self.assertEqual(valor.metadados['codigo_sgs'], 21084)
        self.assertEqual(valor.unidade_original, '%')
        self.assertEqual(ImportacaoDados.objects.filter(status='CONCLUIDO').count(), 6)

    @patch('dashboard.management.commands.importar_dados_bcb.urlopen')
    def test_failed_series_are_recorded_and_reported_without_success_status(self, urlopen):
        failed = Mock()
        failed.status = 503
        failed.read.return_value = b'{}'
        failed.__enter__ = Mock(return_value=failed)
        failed.__exit__ = Mock(return_value=False)
        good = self.api_response([{'data': '01/01/2024', 'valor': '4.11'}])
        urlopen.side_effect = [failed, good, good]

        with self.assertRaises(CommandError):
            call_command(
                'importar_dados_bcb',
                data_inicial=date(2024, 1, 1),
                data_final=date(2024, 1, 31),
                stdout=StringIO(),
            )

        erro = ImportacaoDados.objects.get(fonte__nome='Sistema Gerenciador de Séries Temporais (SGS)', status='ERRO')
        self.assertIn('21084', erro.mensagem_erro)
        self.assertEqual(erro.quantidade_importada, 0)
        self.assertEqual(ErroImportacao.objects.get(importacao=erro).campo, 'SGS 21084')
        self.assertEqual(ValorIndicador.objects.count(), 2)
