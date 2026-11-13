from django.db import models

from fontes.models import FonteDados
from localidades.models import Localidade


class Indicador(models.Model):
    CATEGORIA_CHOICES = [
        ('inadimplência', 'inadimplência'),
        ('renda', 'renda'),
        ('emprego/desemprego', 'emprego/desemprego'),
        ('inflação', 'inflação'),
        ('população', 'população'),
        ('crédito', 'crédito'),
        ('endividamento', 'endividamento'),
        ('outros', 'outros'),
    ]

    nome = models.CharField(max_length=200)
    nome_curto = models.CharField(max_length=120, blank=True)
    descricao = models.TextField(blank=True)
    categoria = models.CharField(max_length=40, choices=CATEGORIA_CHOICES, default='outros')
    unidade_medida = models.CharField(max_length=50)
    periodicidade = models.CharField(max_length=50, blank=True)
    codigo_fonte = models.CharField(max_length=100, blank=True)
    abrangencia = models.CharField(max_length=200, blank=True)
    url_documentacao = models.URLField(blank=True)
    fonte = models.ForeignKey(
        FonteDados,
        on_delete=models.PROTECT,
        related_name='indicadores',
        blank=True,
        null=True,
    )
    ativo = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['nome']
        verbose_name = 'Indicador'
        verbose_name_plural = 'Indicadores'

    def __str__(self):
        return self.nome


class Periodo(models.Model):
    ano = models.IntegerField()
    mes = models.PositiveSmallIntegerField(null=True, blank=True)
    trimestre = models.PositiveSmallIntegerField(null=True, blank=True)
    data_referencia = models.DateField()

    class Meta:
        ordering = ['data_referencia']
        verbose_name = 'Período'
        verbose_name_plural = 'Períodos'
        constraints = [
            models.CheckConstraint(
                condition=models.Q(mes__isnull=True) | models.Q(trimestre__isnull=True),
                name='periodo_mes_ou_trimestre',
            ),
            models.CheckConstraint(
                condition=models.Q(mes__isnull=True) | models.Q(mes__gte=1, mes__lte=12),
                name='periodo_mes_valido',
            ),
            models.CheckConstraint(
                condition=models.Q(trimestre__isnull=True) | models.Q(trimestre__gte=1, trimestre__lte=4),
                name='periodo_trimestre_valido',
            ),
            models.UniqueConstraint(
                fields=['ano', 'mes'],
                condition=models.Q(mes__isnull=False),
                name='uniq_periodo_ano_mes',
            ),
            models.UniqueConstraint(
                fields=['ano', 'trimestre'],
                condition=models.Q(trimestre__isnull=False),
                name='uniq_periodo_ano_trim',
            ),
            models.UniqueConstraint(
                fields=['ano'],
                condition=models.Q(mes__isnull=True, trimestre__isnull=True),
                name='uniq_periodo_ano_anual',
            ),
        ]

    def __str__(self):
        if self.mes:
            return f'{self.ano}-{self.mes:02d}'
        if self.trimestre:
            return f'{self.ano}-T{self.trimestre}'
        return str(self.ano)


class ValorIndicador(models.Model):
    indicador = models.ForeignKey(Indicador, on_delete=models.CASCADE, related_name='valores')
    fonte = models.ForeignKey(FonteDados, on_delete=models.PROTECT, related_name='valores')
    localidade = models.ForeignKey(Localidade, on_delete=models.CASCADE, related_name='valores')
    periodo = models.ForeignKey(Periodo, on_delete=models.CASCADE, related_name='valores')
    valor = models.DecimalField(max_digits=18, decimal_places=6)
    unidade_original = models.CharField(max_length=50, blank=True)
    observacao = models.TextField(blank=True)
    metadados = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['indicador', 'fonte', 'localidade', 'periodo'],
                name='unique_valor_indicador_fonte_localidade_periodo'
            )
        ]
        ordering = ['periodo__data_referencia', 'localidade__nome']
        verbose_name = 'Valor do indicador'
        verbose_name_plural = 'Valores dos indicadores'

    def __str__(self):
        return f'{self.indicador} - {self.localidade} - {self.periodo}'
