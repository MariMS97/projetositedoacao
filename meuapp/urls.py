from django.urls import path
from . import views

urlpatterns = [
    # PÁGINA INICIAL
    path('', views.home, name='home'),
    path('pagina-do-doador/', views.pagina_do_doador, name='pagina_do_doador'),
    path('pagina-do-receptor/', views.pagina_do_receptor, name='pagina_do_receptor'),
    path('', views.index, name='index'),

    # DOADORES
    path('doadores/importar/', views.importar_doadores, name='importar_doadores'),
    path('doadores/cadastrar/', views.cadastrar_doador, name='cadastrar_doador'),
    path('doadores/listar', views.listar_doadores, name='listar_doadores'),
    path('doadores/editar/<int:pk>/', views.editar_doador, name='editar_doador'),
    path('doadores/deletar/<int:pk>/', views.deletar_doador, name='deletar_doador'),

    # RECEPTORES
    path('receptores/importar/', views.importar_receptores, name='importar_receptores'),
    path('receptores/cadastrar/', views.cadastrar_receptor, name='cadastrar_receptor'),
    path('receptores/', views.listar_receptores, name='listar_receptores'),
    path('receptores/editar/<int:pk>/', views.editar_receptor, name='editar_receptor'),
    path('receptores/deletar/<int:pk>/', views.deletar_receptor, name='deletar_receptor'),
]
