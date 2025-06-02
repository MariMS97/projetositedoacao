from django.contrib import admin
from .models import Doador, Receptor

@admin.register(Doador)
class DoadorAdmin(admin.ModelAdmin):
    list_display = ('nome', 'cpf', 'tipo_sanguineo', 'idade', 'cidade_residencia', 'estado_residencia')
    search_fields = ('nome', 'cpf')
    list_filter = ('tipo_sanguineo', 'estado_residencia', 'estado_civil')
    readonly_fields = ('idade',)


@admin.register(Receptor)
class ReceptorAdmin(admin.ModelAdmin):
    list_display = (
        'nome', 'cpf', 'tipo_sanguineo', 'orgao_necessario', 'gravidade_condicao',
        'posicao_lista_espera', 'cidade_residencia', 'data_cadastro'
    )
    search_fields = ('nome', 'cpf')
    list_filter = ('tipo_sanguineo', 'orgao_necessario', 'gravidade_condicao')
    readonly_fields = ('idade', 'data_cadastro', 'gravidade_condicao', 'posicao_lista_espera')

