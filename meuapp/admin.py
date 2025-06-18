from django.contrib import admin
from .models import Doador, Receptor, Administrador, Orgao, CentroDistribuicao

@admin.register(Doador)
class DoadorAdmin(admin.ModelAdmin):
    list_display = ('nome', 'cpf', 'tipo_sanguineo', 'idade', 'cidade_residencia', 'estado_residencia', 'estado_civil')
    search_fields = ('nome', 'cpf')
    list_filter = ('tipo_sanguineo', 'estado_residencia', 'estado_civil')
    readonly_fields = ()
    ordering = ('nome',)
    list_per_page = 25

@admin.register(Receptor)
class ReceptorAdmin(admin.ModelAdmin):
    list_display = (
        'nome', 'cpf', 'tipo_sanguineo', 'orgao_necessario', 'gravidade_condicao',
        'posicao_lista_espera', 'cidade_residencia', 'estado_residencia', 'data_cadastro'
    )
    search_fields = ('nome', 'cpf')
    list_filter = ('tipo_sanguineo', 'orgao_necessario', 'gravidade_condicao')
    readonly_fields = ('data_cadastro', 'gravidade_condicao', 'posicao_lista_espera')
    ordering = ('-data_cadastro',)
    list_per_page = 25

from django.contrib import admin
from .models import Administrador

class AdministradorAdmin(admin.ModelAdmin):
    list_display = ('nome', 'email', 'user', 'is_staff', 'is_active')

    def email(self, obj):
        return obj.user.email

    def user(self, obj):
        return obj.user.username

    def is_staff(self, obj):
        return obj.user.is_staff

    def is_active(self, obj):
        return obj.user.is_active

admin.site.register(Administrador, AdministradorAdmin)

@admin.register(Orgao)
class OrgaoAdmin(admin.ModelAdmin):
    list_display = ('nome', 'tipo')


@admin.register(CentroDistribuicao)
class CentroDistribuicaoAdmin(admin.ModelAdmin):
    list_display = ('nome', 'cidade', 'estado', 'ativo')
    search_fields = ('nome', 'cidade')
    list_filter = ('estado', 'ativo')
    ordering = ('nome',)
    list_per_page = 25
