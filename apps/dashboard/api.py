from datetime import date

from django.db.models import Count, Q
from django.http import JsonResponse
from django.views.decorators.http import require_GET

from fontes.models import FonteDados
from indicadores.models import Indicador, ValorIndicador
from localidades.models import Localidade


def _observacoes_oficiais():
    return ValorIndicador.objects.filter(metadados__simulado=False)


def _erro(mensagem):
    return JsonResponse({'error': mensagem}, status=400)


def _id_parametro(request, nome):
    valor = request.GET.get(nome)
    if valor in (None, ''):
        return None
    try:
        return int(valor)
    except ValueError:
        raise ValueError(f'O filtro "{nome}" deve ser um identificador numérico.')


def _data_parametro(request, nome):
    valor = request.GET.get(nome)
    if not valor:
        return None
    try:
        referencia = date.fromisoformat(valor)
    except ValueError:
        raise ValueError(f'O filtro "{nome}" deve usar o formato AAAA-MM-DD.')
    if referencia.isoformat() != valor:
        raise ValueError(f'O filtro "{nome}" deve usar o formato AAAA-MM-DD.')
    return referencia


def _indicador_json(indicador):
    valores = _observacoes_oficiais().filter(indicador=indicador)
    if indicador.fonte_id:
        valores = valores.filter(fonte_id=indicador.fonte_id)
    ordenados = valores.select_related('periodo').order_by('-periodo__data_referencia', '-pk')
    mais_recente = ordenados.first()
    anterior = ordenados[1] if mais_recente and valores.count() > 1 else None
    primeiro = valores.select_related('periodo').order_by('periodo__data_referencia', 'pk').first()
    return {
        'id': indicador.pk,
        'name': indicador.nome,
        'short_name': indicador.nome_curto or indicador.nome,
        'description': indicador.descricao,
        'category': indicador.categoria,
        'unit': indicador.unidade_medida,
        'periodicity': indicador.periodicidade,
        'code': indicador.codigo_fonte,
        'coverage': indicador.abrangencia,
        'documentation_url': indicador.url_documentacao,
        'source': _fonte_json(indicador.fonte) if indicador.fonte_id else None,
        'observation_count': valores.count(),
        'first_date': primeiro.periodo.data_referencia.isoformat() if primeiro else None,
        'latest': (
            {
                'value': str(mais_recente.valor),
                'date': mais_recente.periodo.data_referencia.isoformat(),
            }
            if mais_recente
            else None
        ),
        'previous': (
            {
                'value': str(anterior.valor),
                'date': anterior.periodo.data_referencia.isoformat(),
            }
            if anterior
            else None
        ),
    }


def _fonte_json(fonte):
    indicadores = list(fonte.indicadores.filter(ativo=True).order_by('nome'))
    valores = _observacoes_oficiais().filter(fonte=fonte)
    ultima = valores.select_related('periodo').order_by('-periodo__data_referencia').first()
    return {
        'id': fonte.pk,
        'name': fonte.nome,
        'institution': fonte.instituicao,
        'description': fonte.descricao,
        'url': fonte.url_origem,
        'type': fonte.tipo_origem,
        'indicators': [item.nome for item in indicadores],
        'observation_count': valores.count(),
        'latest_date': ultima.periodo.data_referencia.isoformat() if ultima else None,
        'has_data': valores.exists(),
    }


@require_GET
def api_indicadores(request):
    indicadores = Indicador.objects.filter(ativo=True).select_related('fonte')
    busca = request.GET.get('q', '').strip()
    categoria = request.GET.get('categoria', '').strip()
    periodicidade = request.GET.get('periodicidade', '').strip()
    try:
        fonte_id = _id_parametro(request, 'fonte')
    except ValueError as exc:
        return _erro(str(exc))
    if busca:
        indicadores = indicadores.filter(
            Q(nome__icontains=busca)
            | Q(descricao__icontains=busca)
            | Q(codigo_fonte__icontains=busca)
            | Q(fonte__instituicao__icontains=busca)
        )
    if categoria and categoria.casefold() != 'todas':
        indicadores = indicadores.filter(categoria__iexact=categoria)
    if periodicidade and periodicidade.casefold() != 'todas':
        indicadores = indicadores.filter(periodicidade__iexact=periodicidade)
    if fonte_id is not None:
        indicadores = indicadores.filter(fonte_id=fonte_id)
    return JsonResponse({'results': [_indicador_json(item) for item in indicadores]})


@require_GET
def api_fontes(request):
    fontes = FonteDados.objects.filter(ativo=True).order_by('nome')
    return JsonResponse({'results': [_fonte_json(item) for item in fontes]})


@require_GET
def api_localidades(request):
    localidades = Localidade.objects.all().order_by('tipo', 'nome')
    tipo = request.GET.get('tipo', '').strip()
    if tipo:
        localidades = localidades.filter(tipo__iexact=tipo)
    observacoes = _observacoes_oficiais()
    contagens = dict(
        observacoes.values('localidade_id')
        .annotate(total=Count('pk'))
        .values_list('localidade_id', 'total')
    )
    return JsonResponse({
        'results': [
            {
                'id': item.pk,
                'name': item.nome,
                'code': item.codigo_ibge,
                'type': item.tipo,
                'uf': item.uf,
                'region': item.regiao,
                'observation_count': contagens.get(item.pk, 0),
                'has_data': item.pk in contagens,
            }
            for item in localidades
        ]
    })


@require_GET
def api_observacoes(request):
    try:
        indicador_ids = []
        for valor in request.GET.getlist('indicador'):
            try:
                indicador_ids.append(int(valor))
            except ValueError as exc:
                raise ValueError('O filtro "indicador" deve conter identificadores numéricos.') from exc
        fonte_id = _id_parametro(request, 'fonte')
        localidade_id = _id_parametro(request, 'localidade')
        data_inicio = _data_parametro(request, 'data_inicio')
        data_fim = _data_parametro(request, 'data_fim')
    except ValueError as exc:
        return _erro(str(exc))

    if data_inicio and data_fim and data_inicio > data_fim:
        return _erro('"data_inicio" não pode ser posterior a "data_fim".')

    observacoes = _observacoes_oficiais().select_related(
        'indicador', 'fonte', 'localidade', 'periodo'
    )
    if indicador_ids:
        observacoes = observacoes.filter(indicador_id__in=indicador_ids)
    if fonte_id is not None:
        observacoes = observacoes.filter(fonte_id=fonte_id)
    if localidade_id is not None:
        observacoes = observacoes.filter(localidade_id=localidade_id)
    if data_inicio:
        observacoes = observacoes.filter(periodo__data_referencia__gte=data_inicio)
    if data_fim:
        observacoes = observacoes.filter(periodo__data_referencia__lte=data_fim)

    return JsonResponse({
        'count': observacoes.count(),
        'results': [
            {
                'id': item.pk,
                'indicator_id': item.indicador_id,
                'indicator': item.indicador.nome,
                'indicator_short_name': item.indicador.nome_curto or item.indicador.nome,
                'category': item.indicador.categoria,
                'unit': item.unidade_original or item.indicador.unidade_medida,
                'periodicity': item.indicador.periodicidade,
                'code': item.indicador.codigo_fonte,
                'source_id': item.fonte_id,
                'source': item.fonte.nome,
                'institution': item.fonte.instituicao,
                'locality_id': item.localidade_id,
                'locality': item.localidade.nome,
                'locality_type': item.localidade.tipo,
                'uf': item.localidade.uf,
                'region': item.localidade.regiao,
                'year': item.periodo.ano,
                'month': item.periodo.mes,
                'quarter': item.periodo.trimestre,
                'date': item.periodo.data_referencia.isoformat(),
                'value': str(item.valor),
                'note': item.observacao,
                'metadata': item.metadados,
            }
            for item in observacoes.order_by('periodo__data_referencia', 'indicador__nome')
        ],
    })
