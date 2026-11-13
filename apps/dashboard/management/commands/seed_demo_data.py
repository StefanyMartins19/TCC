from django.core.management.base import BaseCommand
from django.utils import timezone

from fontes.models import FonteDados
from indicadores.models import Indicador, Periodo, ValorIndicador
from localidades.models import Localidade


class Command(BaseCommand):
    help = 'Seeds demo data for local development and testing.'

    def handle(self, *args, **options):
        fonte, _ = FonteDados.objects.get_or_create(
            nome='Dados simulados para desenvolvimento',
            defaults={
                'instituicao': 'Observatório Brasileiro da Inadimplência',
                'descricao': 'Dados fictícios utilizados apenas para desenvolvimento e testes do sistema.',
                'url_origem': 'https://exemplo.local/dados-simulados',
                'tipo_origem': 'JSON',
                'data_atualizacao': timezone.now().date(),
                'ativo': True,
            }
        )

        brasil, _ = Localidade.objects.get_or_create(
            codigo_ibge='00',
            nome='Brasil',
            defaults={'tipo': 'Brasil', 'uf': '', 'regiao': 'Brasil', 'pais': 'Brasil'}
        )

        regiao_sudeste, _ = Localidade.objects.get_or_create(
            codigo_ibge='29',
            nome='Sudeste',
            defaults={'tipo': 'Região', 'uf': '', 'regiao': 'Sudeste', 'pais': 'Brasil'}
        )

        for uf, regiao in [('SP', 'Sudeste'), ('RJ', 'Sudeste'), ('MG', 'Sudeste'), ('RS', 'Sul')]:
            Localidade.objects.get_or_create(
                codigo_ibge=f'35{uf == "SP" and "1" or uf == "RJ" and "2" or uf == "MG" and "3" or "4"}',
                nome=uf,
                defaults={'tipo': 'Estado', 'uf': uf, 'regiao': regiao, 'pais': 'Brasil'}
            )

        indicadores = {
            'Taxa de inadimplência': {
                'categoria': 'inadimplência',
                'unidade_medida': '%',
                'periodicidade': 'mensal',
                'descricao': 'Percentual de pessoas em atraso em instituições financeiras.'
            },
            'Taxa de desemprego': {
                'categoria': 'emprego/desemprego',
                'unidade_medida': '%',
                'periodicidade': 'mensal',
                'descricao': 'Participação da população desocupada na força de trabalho.'
            },
            'Renda média': {
                'categoria': 'renda',
                'unidade_medida': 'R$',
                'periodicidade': 'mensal',
                'descricao': 'Valor médio de renda familiar em reais.'
            },
            'Inflação': {
                'categoria': 'inflação',
                'unidade_medida': '%',
                'periodicidade': 'mensal',
                'descricao': 'Taxa de variação de preços em relação ao período anterior.'
            },
        }

        created_indicadores = {}
        for nome, meta in indicadores.items():
            indicador, _ = Indicador.objects.get_or_create(
                nome=nome,
                defaults={
                    'descricao': meta['descricao'],
                    'categoria': meta['categoria'],
                    'unidade_medida': meta['unidade_medida'],
                    'periodicidade': meta['periodicidade'],
                    'ativo': True,
                }
            )
            created_indicadores[nome] = indicador

        periodos = []
        for ano, mes in [(2023, 12), (2024, 3), (2024, 6), (2024, 9), (2025, 3)]:
            periodo, _ = Periodo.objects.get_or_create(
                ano=ano,
                mes=mes,
                defaults={'data_referencia': timezone.datetime(ano, mes, 1).date()}
            )
            periodos.append(periodo)

        localidades = Localidade.objects.filter(tipo__in=['Brasil', 'Região', 'Estado'])
        valores = {
            'Taxa de inadimplência': [7.5, 8.1, 8.6, 9.0, 9.4],
            'Taxa de desemprego': [9.1, 8.8, 8.5, 8.2, 7.9],
            'Renda média': [2900, 3080, 3150, 3220, 3350],
            'Inflação': [4.3, 3.8, 3.5, 3.2, 3.1],
        }

        for indicador_nome, series in valores.items():
            indicador = created_indicadores[indicador_nome]
            for periodo, valor in zip(periodos, series):
                for localidade in localidades[:3]:
                    ValorIndicador.objects.get_or_create(
                        indicador=indicador,
                        fonte=fonte,
                        localidade=localidade,
                        periodo=periodo,
                        defaults={
                            'valor': valor,
                            'unidade_original': indicador.unidade_medida,
                            'observacao': 'DADOS SIMULADOS PARA DESENVOLVIMENTO.',
                            'metadados': {'simulado': True, 'fonte': 'Demo'},
                        }
                    )

        self.stdout.write(self.style.SUCCESS('Dados fictícios criados com sucesso.'))
