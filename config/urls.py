from django.contrib import admin
from django.urls import include, path

from dashboard.api import api_fontes, api_indicadores, api_localidades, api_observacoes

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/indicadores/', api_indicadores, name='api_indicadores'),
    path('api/fontes/', api_fontes, name='api_fontes'),
    path('api/localidades/', api_localidades, name='api_localidades'),
    path('api/observacoes/', api_observacoes, name='api_observacoes'),
    path('', include('dashboard.urls')),
]
