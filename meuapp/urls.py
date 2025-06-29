from django.urls import path
from django.contrib.auth.views import LogoutView
from . import views

urlpatterns = [
    # PÁGINA INICIAL
    path('', views.home, name='home'),
    path('pagina-do-doador/', views.pagina_do_doador, name='pagina_do_doador'),
    path('pagina-do-receptor/', views.pagina_do_receptor, name='pagina_do_receptor'),
    path('pagina-do-administrador/', views.pagina_do_administrador, name='pagina_do_administrador'),
    path('painel/', views.painel_admin, name='painel_admin'),
    

    # DOADORES
    path('doadores/importar/', views.importar_doadores, name='importar_doadores'),
    path('doadores/cadastrar/', views.cadastrar_doador, name='cadastrar_doador'),
    path('doadores/listar/', views.listar_doadores, name='listar_doadores'),
    path('doadores/editar/<int:pk>/', views.editar_doador, name='editar_doador'),
    path('doadores/deletar/<int:pk>/', views.deletar_doador, name='deletar_doador'),

    # RECEPTORES
    path('receptores/importar/', views.importar_receptores, name='importar_receptores'),
    path('receptores/cadastrar/', views.cadastrar_receptor, name='cadastrar_receptor'),
    path('receptores/', views.listar_receptores, name='listar_receptores'),
    path('receptores/editar/<int:pk>/', views.editar_receptor, name='editar_receptor'),
    path('receptores/deletar/<int:pk>/', views.deletar_receptor, name='deletar_receptor'),

    # ADMINISTRADORES
    path('login/', views.login_administrador, name='login_administrador'),
    path('logout/', LogoutView.as_view(next_page='home'), name='logout'),
    path('administradores/', views.listar_administradores, name='listar_administradores'),
    path('administrador/cadastrar/', views.cadastrar_administrador, name='cadastrar_administrador'),
    path('administradores/<int:pk>/', views.buscar_administrador, name='detalhes_administrador'),
    path('administradores/editar/<int:pk>/', views.editar_administrador, name='editar_administrador'),
    path('administradores/excluir/<int:pk>/', views.excluir_administrador, name='excluir_administrador'),
    path('administradores/importar/', views.importar_administradores, name='importar_administradores'),
    
    # Órgãos
    path('orgaos/', views.listar_orgaos, name='listar_orgaos'),
    path('orgaos/cadastrar/', views.cadastrar_orgao, name='cadastrar_orgao'),
    path('orgaos/editar/<int:pk>/', views.editar_orgao, name='editar_orgao'),
    path('orgaos/excluir/<int:pk>/', views.excluir_orgao, name='excluir_orgao'),

    # Centros
    path('centros/', views.listar_centros, name='listar_centros'),
    path('centros/editar/<int:pk>/', views.editar_centro, name='editar_centro'),
    path('centros/importar/', views.importar_centros, name='importar_centros'),
    
    # Doações
    path('doacoes/registrar/', views.registrar_doacao, name='registrar_doacao'),
    path('doacoes/buscar/<int:receptor_id>/', views.buscar_doadores_compatíveis, name='buscar_doadores'),
    path('doacoes/historico/', views.historico_doacoes, name='historico_doacoes'),
    path('doacoes/concluir/<int:doacao_id>/', views.concluir_doacao, name='concluir_doacao'),
    path('doacoes/cancelar/<int:doacao_id>/', views.cancelar_doacao, name='cancelar_doacao'),


]
