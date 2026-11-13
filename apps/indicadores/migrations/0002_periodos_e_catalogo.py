from django.db import migrations, models
import django.db.models.deletion


def validar_periodos(apps, schema_editor):
    Periodo = apps.get_model('indicadores', 'Periodo')
    alias = schema_editor.connection.alias
    periodos = Periodo.objects.using(alias)

    for periodo in periodos.iterator():
        if periodo.mes is not None and not 1 <= periodo.mes <= 12:
            raise RuntimeError(
                f'Período {periodo.pk} possui mês inválido ({periodo.mes}); '
                'corrija o registro antes de migrar.'
            )
        if periodo.trimestre is not None and not 1 <= periodo.trimestre <= 4:
            raise RuntimeError(
                f'Período {periodo.pk} possui trimestre inválido ({periodo.trimestre}); '
                'corrija o registro antes de migrar.'
            )
        if periodo.mes is not None and periodo.trimestre is not None:
            trimestre_esperado = ((periodo.mes - 1) // 3) + 1
            raise RuntimeError(
                f'Período {periodo.pk} combina mês {periodo.mes} e trimestre '
                f'{periodo.trimestre} (trimestre esperado: {trimestre_esperado}); '
                'corrija a referência ambígua antes de migrar.'
            )

    for field in ('mes', 'trimestre'):
        duplicados = (
            periodos.filter(**{f'{field}__isnull': False})
            .values('ano', field)
            .annotate(total=models.Count('pk'))
            .filter(total__gt=1)
            .order_by('ano', field)
            .first()
        )
        if duplicados:
            raise RuntimeError(
                f'Existem períodos duplicados para ano {duplicados["ano"]} e '
                f'{field} {duplicados[field]}; resolva a ambiguidade antes de migrar.'
            )

    duplicado_anual = (
        periodos.filter(mes__isnull=True, trimestre__isnull=True)
        .values('ano')
        .annotate(total=models.Count('pk'))
        .filter(total__gt=1)
        .order_by('ano')
        .first()
    )
    if duplicado_anual:
        raise RuntimeError(
            f'Existem períodos anuais duplicados para {duplicado_anual["ano"]}; '
            'resolva a ambiguidade antes de migrar.'
        )


class Migration(migrations.Migration):

    dependencies = [
        ('fontes', '0001_initial'),
        ('indicadores', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(validar_periodos, migrations.RunPython.noop),
        migrations.AlterUniqueTogether(
            name='periodo',
            unique_together=set(),
        ),
        migrations.AddConstraint(
            model_name='periodo',
            constraint=models.CheckConstraint(
                condition=models.Q(mes__isnull=True) | models.Q(trimestre__isnull=True),
                name='periodo_mes_ou_trimestre',
            ),
        ),
        migrations.AddConstraint(
            model_name='periodo',
            constraint=models.CheckConstraint(
                condition=models.Q(mes__isnull=True) | models.Q(mes__gte=1, mes__lte=12),
                name='periodo_mes_valido',
            ),
        ),
        migrations.AddConstraint(
            model_name='periodo',
            constraint=models.CheckConstraint(
                condition=models.Q(trimestre__isnull=True) | models.Q(trimestre__gte=1, trimestre__lte=4),
                name='periodo_trimestre_valido',
            ),
        ),
        migrations.AddConstraint(
            model_name='periodo',
            constraint=models.UniqueConstraint(
                condition=models.Q(mes__isnull=False),
                fields=('ano', 'mes'),
                name='uniq_periodo_ano_mes',
            ),
        ),
        migrations.AddConstraint(
            model_name='periodo',
            constraint=models.UniqueConstraint(
                condition=models.Q(trimestre__isnull=False),
                fields=('ano', 'trimestre'),
                name='uniq_periodo_ano_trim',
            ),
        ),
        migrations.AddConstraint(
            model_name='periodo',
            constraint=models.UniqueConstraint(
                condition=models.Q(mes__isnull=True, trimestre__isnull=True),
                fields=('ano',),
                name='uniq_periodo_ano_anual',
            ),
        ),
        migrations.AddField(
            model_name='indicador',
            name='nome_curto',
            field=models.CharField(blank=True, max_length=120),
        ),
        migrations.AddField(
            model_name='indicador',
            name='codigo_fonte',
            field=models.CharField(blank=True, max_length=100),
        ),
        migrations.AddField(
            model_name='indicador',
            name='abrangencia',
            field=models.CharField(blank=True, max_length=200),
        ),
        migrations.AddField(
            model_name='indicador',
            name='url_documentacao',
            field=models.URLField(blank=True),
        ),
        migrations.AddField(
            model_name='indicador',
            name='fonte',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name='indicadores',
                to='fontes.fontedados',
            ),
        ),
    ]
