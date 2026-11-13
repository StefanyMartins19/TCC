from django.core.management.base import BaseCommand

from fontes.models import FonteDados
from indicadores.models import Indicador
from localidades.models import Localidade


FONTES = [
    {
        'nome': 'Sistema Gerenciador de Séries Temporais (SGS)',
        'instituicao': 'Banco Central do Brasil (BCB)',
        'descricao': 'Séries nacionais publicadas pelo BCData/SGS.',
        'url_origem': 'https://dadosabertos.bcb.gov.br/',
        'tipo_origem': 'API',
    },
    {
        'nome': 'Pesquisa Nacional por Amostra de Domicílios Contínua (PNAD Contínua)',
        'instituicao': 'Instituto Brasileiro de Geografia e Estatística (IBGE)',
        'descricao': 'Fonte oficial de estatísticas de trabalho e rendimento; valores ainda não importados.',
        'url_origem': 'https://sidra.ibge.gov.br/',
        'tipo_origem': 'API',
    },
    {
        'nome': 'Sistema Nacional de Índices de Preços ao Consumidor (SNIPC)',
        'instituicao': 'Instituto Brasileiro de Geografia e Estatística (IBGE)',
        'descricao': 'Fonte oficial de índices de preços; série e observações ainda não importadas.',
        'url_origem': 'https://sidra.ibge.gov.br/',
        'tipo_origem': 'API',
    },
    {
        'nome': 'Publicações agregadas da Serasa',
        'instituicao': 'Serasa',
        'descricao': 'Publicações sobre inadimplência; observações não foram importadas.',
        'url_origem': 'https://www.serasa.com.br/',
        'tipo_origem': 'MANUAL',
    },
    {
        'nome': 'Pesquisa de Endividamento e Inadimplência do Consumidor (Peic)',
        'instituicao': 'Confederação Nacional do Comércio (CNC)',
        'descricao': 'Publicação agregada; série e observações não foram importadas.',
        'url_origem': 'https://www.portaldocomercio.org.br/',
        'tipo_origem': 'MANUAL',
    },
]

INDICADORES = [
    {
        'nome': 'Inadimplência da carteira de crédito de pessoas físicas — BCB SGS 21084',
        'nome_curto': 'Inadimplência PF',
        'codigo_fonte': 'SGS 21084',
        'categoria': 'inadimplência',
        'unidade_medida': '%',
        'periodicidade': 'mensal',
        'abrangencia': 'Brasil',
        'descricao': 'Percentual da carteira de crédito de pessoas físicas com atraso superior a 90 dias.',
        'url_documentacao': 'https://dadosabertos.bcb.gov.br/dataset/21084-inadimplencia-da-carteira-de-credito---pessoas-fisicas---total',
        'fonte': 'Sistema Gerenciador de Séries Temporais (SGS)',
    },
    {
        'nome': 'Taxa média mensal de juros do crédito livre para pessoas físicas — BCB SGS 25462',
        'nome_curto': 'Juros crédito livre PF',
        'codigo_fonte': 'SGS 25462',
        'categoria': 'crédito',
        'unidade_medida': '% a.m.',
        'periodicidade': 'mensal',
        'abrangencia': 'Brasil',
        'descricao': 'Taxa média mensal de juros das novas operações de crédito livre para pessoas físicas.',
        'url_documentacao': 'https://dadosabertos.bcb.gov.br/dataset/25462-taxa-media-mensal-de-juros-das-operacoes-de-credito-com-recursos-livres---pessoas-fisicas---t',
        'fonte': 'Sistema Gerenciador de Séries Temporais (SGS)',
    },
    {
        'nome': 'Comprometimento da renda das famílias com serviço da dívida — BCB SGS 29265',
        'nome_curto': 'Comprometimento da renda',
        'codigo_fonte': 'SGS 29265',
        'categoria': 'endividamento',
        'unidade_medida': '%',
        'periodicidade': 'mensal',
        'abrangencia': 'Brasil',
        'descricao': 'Comprometimento da renda com o serviço da dívida, em média móvel trimestral.',
        'url_documentacao': 'https://dadosabertos.bcb.gov.br/dataset/29265-sgs',
        'fonte': 'Sistema Gerenciador de Séries Temporais (SGS)',
    },
    {
        'nome': 'Taxa de desocupação — PNAD Contínua',
        'nome_curto': 'Taxa de desocupação',
        'codigo_fonte': 'PNAD Contínua',
        'categoria': 'emprego/desemprego',
        'unidade_medida': '%',
        'periodicidade': 'trimestral',
        'abrangencia': 'Brasil e UFs, conforme a série oficial.',
        'descricao': 'Taxa de desocupação da população na força de trabalho; observações ainda não importadas.',
        'url_documentacao': 'https://sidra.ibge.gov.br/',
        'fonte': 'Pesquisa Nacional por Amostra de Domicílios Contínua (PNAD Contínua)',
    },
    {
        'nome': 'Rendimento médio do trabalho — PNAD Contínua',
        'nome_curto': 'Rendimento médio',
        'codigo_fonte': 'PNAD Contínua',
        'categoria': 'renda',
        'unidade_medida': 'R$',
        'periodicidade': 'trimestral',
        'abrangencia': 'Brasil e UFs, conforme a série oficial.',
        'descricao': 'Rendimento médio do trabalho; definição da série e observações ainda não importadas.',
        'url_documentacao': 'https://sidra.ibge.gov.br/',
        'fonte': 'Pesquisa Nacional por Amostra de Domicílios Contínua (PNAD Contínua)',
    },
    {
        'nome': 'Informalidade no trabalho — PNAD Contínua',
        'nome_curto': 'Informalidade',
        'codigo_fonte': 'PNAD Contínua',
        'categoria': 'emprego/desemprego',
        'unidade_medida': '%',
        'periodicidade': 'trimestral',
        'abrangencia': 'Brasil; recortes ainda não validados.',
        'descricao': 'Indicador previsto; tabela, série e observações ainda não validadas/importadas.',
        'url_documentacao': 'https://sidra.ibge.gov.br/',
        'fonte': 'Pesquisa Nacional por Amostra de Domicílios Contínua (PNAD Contínua)',
    },
    {
        'nome': 'Índice Nacional de Preços ao Consumidor Amplo (IPCA)',
        'nome_curto': 'IPCA',
        'codigo_fonte': 'SIDRA / SNIPC',
        'categoria': 'inflação',
        'unidade_medida': '%',
        'periodicidade': 'mensal',
        'abrangencia': 'Brasil; série específica ainda não selecionada.',
        'descricao': 'Indicador de preços complementar; série e observações ainda não importadas.',
        'url_documentacao': 'https://sidra.ibge.gov.br/',
        'fonte': 'Sistema Nacional de Índices de Preços ao Consumidor (SNIPC)',
    },
    {
        'nome': 'Consumidores inadimplentes — Serasa',
        'nome_curto': 'Consumidores inadimplentes',
        'codigo_fonte': 'Publicações Serasa',
        'categoria': 'inadimplência',
        'unidade_medida': 'consumidores',
        'periodicidade': 'mensal',
        'abrangencia': 'Brasil; recortes conforme publicação oficial.',
        'descricao': 'Conceito próprio da fonte, não equivalente à inadimplência da carteira de crédito do BCB.',
        'url_documentacao': 'https://www.serasa.com.br/',
        'fonte': 'Publicações agregadas da Serasa',
    },
    {
        'nome': 'Endividamento e inadimplência do consumidor — Peic',
        'nome_curto': 'Endividamento do consumidor',
        'codigo_fonte': 'Peic',
        'categoria': 'endividamento',
        'unidade_medida': '%',
        'periodicidade': '',
        'abrangencia': 'Conforme publicação oficial.',
        'descricao': 'Série a selecionar; observações não foram importadas.',
        'url_documentacao': 'https://www.portaldocomercio.org.br/',
        'fonte': 'Pesquisa de Endividamento e Inadimplência do Consumidor (Peic)',
    },
]

REGIOES = {
    'Norte': [('RO', 'Rondônia', '11'), ('AC', 'Acre', '12'), ('AM', 'Amazonas', '13'), ('RR', 'Roraima', '14'), ('PA', 'Pará', '15'), ('AP', 'Amapá', '16'), ('TO', 'Tocantins', '17')],
    'Nordeste': [('MA', 'Maranhão', '21'), ('PI', 'Piauí', '22'), ('CE', 'Ceará', '23'), ('RN', 'Rio Grande do Norte', '24'), ('PB', 'Paraíba', '25'), ('PE', 'Pernambuco', '26'), ('AL', 'Alagoas', '27'), ('SE', 'Sergipe', '28'), ('BA', 'Bahia', '29')],
    'Sudeste': [('MG', 'Minas Gerais', '31'), ('ES', 'Espírito Santo', '32'), ('RJ', 'Rio de Janeiro', '33'), ('SP', 'São Paulo', '35')],
    'Sul': [('PR', 'Paraná', '41'), ('SC', 'Santa Catarina', '42'), ('RS', 'Rio Grande do Sul', '43')],
    'Centro-Oeste': [('MS', 'Mato Grosso do Sul', '50'), ('MT', 'Mato Grosso', '51'), ('GO', 'Goiás', '52'), ('DF', 'Distrito Federal', '53')],
}


class Command(BaseCommand):
    help = 'Registra fontes, metadados e localidades sem criar observações.'

    def handle(self, *args, **options):
        fontes = {}
        for dados in FONTES:
            nome = dados['nome']
            defaults = {chave: valor for chave, valor in dados.items() if chave != 'nome'}
            fonte, _ = FonteDados.objects.update_or_create(nome=nome, defaults=defaults)
            fontes[nome] = fonte

        Localidade.objects.update_or_create(
            codigo_ibge='00',
            nome='Brasil',
            defaults={'tipo': 'Brasil', 'regiao': 'Brasil', 'pais': 'Brasil', 'uf': ''},
        )
        for codigo_regiao, (nome_regiao, unidades) in enumerate(REGIOES.items(), start=1):
            Localidade.objects.update_or_create(
                codigo_ibge=f'R-{codigo_regiao}',
                nome=nome_regiao,
                defaults={'tipo': 'Região', 'regiao': nome_regiao, 'pais': 'Brasil', 'uf': ''},
            )
            for uf, nome, codigo_ibge in unidades:
                localidade, created = Localidade.objects.get_or_create(
                    codigo_ibge=codigo_ibge,
                    nome=nome,
                    defaults={'tipo': 'Estado'},
                )
                if not created:
                    localidade.tipo = 'Estado'
                localidade.uf = uf
                localidade.regiao = nome_regiao
                localidade.pais = 'Brasil'
                localidade.save()

        for dados in INDICADORES:
            item = {**dados}
            fonte = fontes[item.pop('fonte')]
            nome = item.pop('nome')
            Indicador.objects.update_or_create(
                nome=nome,
                defaults={**item, 'fonte': fonte, 'ativo': True},
            )

        self.stdout.write(self.style.SUCCESS('Catálogo cadastrado; nenhuma observação foi criada.'))
