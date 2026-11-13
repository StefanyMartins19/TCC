import json
from datetime import date, datetime
from decimal import Decimal, InvalidOperation
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from django.core.management.base import BaseCommand, CommandError
from django.db import DatabaseError, transaction
from django.core.management import call_command
from django.utils import timezone

from fontes.models import FonteDados
from indicadores.models import Indicador, Periodo, ValorIndicador
from localidades.models import Localidade
from importacao.models import ErroImportacao, ImportacaoDados


BCB_DATA_URL = 'https://api.bcb.gov.br/dados/serie/bcdata.sgs.{codigo}/dados'
DATA_INICIAL_PADRAO = date(2000, 1, 1)

SERIES_BCB = (
    {
        'codigo': 21084,
        'indicador': 'Inadimplência da carteira de crédito de pessoas físicas — BCB SGS 21084',
        'unidade': '%',
        'descricao': 'Inadimplência da carteira de crédito de pessoas físicas com atraso superior a 90 dias.',
        'url': 'https://dadosabertos.bcb.gov.br/dataset/21084-inadimplencia-da-carteira-de-credito---pessoas-fisicas---total',
    },
    {
        'codigo': 25462,
        'indicador': 'Taxa média mensal de juros do crédito livre para pessoas físicas — BCB SGS 25462',
        'unidade': '% a.m.',
        'descricao': 'Taxa média mensal de juros das novas operações de crédito livre para pessoas físicas.',
        'url': 'https://dadosabertos.bcb.gov.br/dataset/25462-taxa-media-mensal-de-juros-das-operacoes-de-credito-com-recursos-livres---pessoas-fisicas---t',
    },
    {
        'codigo': 29265,
        'indicador': 'Comprometimento da renda das famílias com serviço da dívida — BCB SGS 29265',
        'unidade': '%',
        'descricao': 'Comprometimento da renda com o serviço da dívida em média móvel trimestral.',
        'url': 'https://dadosabertos.bcb.gov.br/dataset/29265-sgs',
    },
)


def obter_serie_bcb(codigo, data_inicial, data_final):
    parametros = urlencode({
        'formato': 'json',
        'dataInicial': data_inicial.strftime('%d/%m/%Y'),
        'dataFinal': data_final.strftime('%d/%m/%Y'),
    })
    url = f'{BCB_DATA_URL.format(codigo=codigo)}?{parametros}'
    requisicao = Request(
        url,
        headers={
            'Accept': 'application/json',
            'User-Agent': 'ObservatorioBrasileiroInadimplencia/1.0',
        },
    )
    try:
        with urlopen(requisicao, timeout=30) as resposta:
            if resposta.status != 200:
                raise CommandError(f'BCB SGS {codigo} respondeu HTTP {resposta.status}.')
            dados = json.loads(resposta.read().decode('utf-8'))
    except HTTPError as exc:
        raise CommandError(f'BCB SGS {codigo} respondeu HTTP {exc.code}: {exc.reason}.') from exc
    except (URLError, TimeoutError, OSError) as exc:
        raise CommandError(f'Não foi possível consultar BCB SGS {codigo}: {exc}.') from exc
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise CommandError(f'BCB SGS {codigo} retornou JSON inválido: {exc}.') from exc

    if not isinstance(dados, list):
        raise CommandError(f'BCB SGS {codigo} não retornou uma lista de observações.')

    observacoes = []
    datas_vistas = set()
    for posicao, item in enumerate(dados, start=1):
        if not isinstance(item, dict) or not isinstance(item.get('data'), str):
            raise CommandError(f'Observação {posicao} inválida na resposta do BCB SGS {codigo}.')
        try:
            referencia = datetime.strptime(item['data'], '%d/%m/%Y').date()
            valor = Decimal(str(item.get('valor', '')).strip().replace(',', '.'))
        except (TypeError, ValueError, InvalidOperation) as exc:
            raise CommandError(
                f'Observação {posicao} inválida na resposta do BCB SGS {codigo}: {exc}.'
            ) from exc
        if (
            not valor.is_finite()
            or len(valor.as_tuple().digits) > 18
            or (valor and valor.adjusted() + 1 > 12)
        ):
            raise CommandError(f'Observação {posicao} contém valor inválido no BCB SGS {codigo}.')
        if max(-valor.as_tuple().exponent, 0) > 6:
            raise CommandError(f'Observação {posicao} excede a precisão suportada no BCB SGS {codigo}.')
        if not data_inicial <= referencia <= data_final:
            raise CommandError(
                f'Observação fora do intervalo solicitado no BCB SGS {codigo}: {referencia}.'
            )
        if referencia in datas_vistas:
            raise CommandError(f'Observação duplicada para {referencia} no BCB SGS {codigo}.')
        datas_vistas.add(referencia)
        observacoes.append((referencia, valor))

    if not observacoes:
        raise CommandError(f'BCB SGS {codigo} não retornou observações no intervalo solicitado.')
    return url, sorted(observacoes)


class Command(BaseCommand):
    help = 'Importa séries mensais oficiais do Banco Central via BCData/SGS.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--data-inicial',
            type=date.fromisoformat,
            default=DATA_INICIAL_PADRAO,
            help='Data inicial em AAAA-MM-DD (padrão: 2000-01-01).',
        )
        parser.add_argument(
            '--data-final',
            type=date.fromisoformat,
            default=timezone.localdate(),
            help='Data final em AAAA-MM-DD (padrão: hoje).',
        )

    def handle(self, *args, **options):
        data_inicial = options['data_inicial']
        data_final = options['data_final']
        if data_inicial > data_final:
            raise CommandError('A data inicial não pode ser posterior à data final.')
        if data_final > timezone.localdate():
            raise CommandError('A data final não pode estar no futuro.')

        call_command('seed_catalogo', verbosity=0)
        fonte = FonteDados.objects.get(
            nome='Sistema Gerenciador de Séries Temporais (SGS)',
            instituicao='Banco Central do Brasil (BCB)',
            ativo=True,
        )
        brasil = Localidade.objects.get(codigo_ibge='00', tipo='Brasil')
        falhas = []

        for serie in SERIES_BCB:
            importacao = ImportacaoDados.objects.create(fonte=fonte, status='PROCESSANDO')
            try:
                url_consulta, observacoes = obter_serie_bcb(
                    serie['codigo'],
                    data_inicial,
                    data_final,
                )
                indicador = Indicador.objects.get(nome=serie['indicador'], ativo=True)
                if indicador.fonte_id != fonte.pk or indicador.unidade_medida != serie['unidade']:
                    raise CommandError(
                        f'Metadados divergentes no catálogo para BCB SGS {serie["codigo"]}.'
                    )

                consultado_em = timezone.now()
                with transaction.atomic():
                    for referencia, valor in observacoes:
                        periodo, _ = Periodo.objects.get_or_create(
                            ano=referencia.year,
                            mes=referencia.month,
                            trimestre=None,
                            defaults={'data_referencia': referencia.replace(day=1)},
                        )
                        ValorIndicador.objects.update_or_create(
                            indicador=indicador,
                            fonte=fonte,
                            localidade=brasil,
                            periodo=periodo,
                            defaults={
                                'valor': valor,
                                'unidade_original': serie['unidade'],
                                'observacao': serie['descricao'],
                                'metadados': {
                                    'origem': 'Banco Central do Brasil — BCData/SGS',
                                    'codigo_sgs': serie['codigo'],
                                    'url_fonte': serie['url'],
                                    'url_consulta': url_consulta,
                                    'data_consulta': consultado_em.isoformat(),
                                    'data_referencia': referencia.isoformat(),
                                    'periodicidade': 'mensal',
                                    'unidade_medida': serie['unidade'],
                                    'abrangencia_geografica': 'Brasil',
                                    'simulado': False,
                                },
                            },
                        )

                importacao.quantidade_lida = len(observacoes)
                importacao.quantidade_importada = len(observacoes)
                importacao.data_fim = timezone.now()
                importacao.status = 'CONCLUIDO'
                importacao.save(
                    update_fields=[
                        'quantidade_lida',
                        'quantidade_importada',
                        'data_fim',
                        'status',
                    ]
                )
                fonte.data_atualizacao = consultado_em.date()
                fonte.save(update_fields=['data_atualizacao', 'updated_at'])
                self.stdout.write(self.style.SUCCESS(
                    f'SGS {serie["codigo"]}: {len(observacoes)} observações oficiais; '
                    f'última referência {observacoes[-1][0].isoformat()}.'
                ))
            except (
                CommandError,
                DatabaseError,
                Indicador.DoesNotExist,
                Indicador.MultipleObjectsReturned,
                ValueError,
            ) as exc:
                mensagem = f'SGS {serie["codigo"]}: {exc}'
                importacao.status = 'ERRO'
                importacao.data_fim = timezone.now()
                importacao.mensagem_erro = mensagem
                importacao.save(update_fields=['status', 'data_fim', 'mensagem_erro'])
                ErroImportacao.objects.create(
                    importacao=importacao,
                    campo=f'SGS {serie["codigo"]}',
                    valor_original=str(serie['codigo']),
                    motivo=mensagem,
                )
                falhas.append(mensagem)

        if falhas:
            raise CommandError('Falha ao importar séries oficiais: ' + ' | '.join(falhas))
