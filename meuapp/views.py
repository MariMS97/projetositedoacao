from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from datetime import datetime
import json
from .models import Doador, Receptor, Administrador, Orgao, CentroDistribuicao
from .forms import (
    ImportarDoadoresForm, CadastrarDoadorForm,
    ImportarReceptoresForm, CadastrarReceptorForm,
    CadastrarAdministradorForm,
    ImportarAdministradoresForm, ImportarCentrosForm,
    OrgaoForm, CentroDistribuicaoForm
)
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render

# --- Página Inicial ---
def home(request):
    return render(request, 'home.html')

def pagina_do_doador(request):
    return render(request, 'pagina_do_doador.html')

def pagina_do_receptor(request):
    return render(request, 'pagina_do_receptor.html')

def pagina_do_administrador(request):
    return render(request, 'pagina_do_administrador.html')

def index(request):
    return render(request, 'index.html')

# --- DOADOR ---

def importar_doadores(request):
    if request.method == 'POST':
        form = ImportarDoadoresForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                json_file = form.cleaned_data['json_file']
                data = json.load(json_file)

                for item in data:
                    dados = item['dados']
                    dados.pop('id', None)  # Remove ID

                    # Converte a data
                    nascimento_str = dados.get('data_nascimento')
                    if nascimento_str:
                        dados['data_nascimento'] = datetime.strptime(nascimento_str, '%Y/%m/%d').date()

                    # Calcula idade
                    nascimento = dados['data_nascimento']
                    hoje = datetime.today().date()
                    idade = hoje.year - nascimento.year - ((hoje.month, hoje.day) < (nascimento.month, nascimento.day))

                    # Cria doador
                    Doador.objects.create(**dados)

                messages.success(request, "Doadores importados com sucesso.")
                return redirect('listar_doadores')
            except Exception as e:
                messages.error(request, f"Erro ao importar: {str(e)}")
    else:
        form = ImportarDoadoresForm()
    return render(request, 'importar_doador.html', {'form': form})

@login_required
def cadastrar_doador(request):
    if request.method == 'POST':
        form = CadastrarDoadorForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Doador cadastrado com sucesso.")
            return redirect('listar_doadores')
    else:
        form = CadastrarDoadorForm()
    return render(request, 'cadastrar_doador.html', {'form': form})


from django.core.paginator import Paginator

def listar_doadores(request):
    cpf = request.GET.get('cpf')
    doadores = Doador.objects.all()

    if cpf:
        doadores = doadores.filter(cpf__icontains=cpf)

    paginator = Paginator(doadores, 10)  # 10 doadores por página
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'listar_doador.html', {'page_obj': page_obj, 'cpf': cpf})



def editar_doador(request, pk):
    doador = get_object_or_404(Doador, pk=pk)
    if request.method == 'POST':
        form = CadastrarDoadorForm(request.POST, instance=doador)
        if form.is_valid():
            form.save()
            messages.success(request, "Doador atualizado com sucesso.")
            return redirect('listar_doadores')
    else:
        form = CadastrarDoadorForm(instance=doador)
    return render(request, 'editar_doador.html', {'form': form})


def deletar_doador(request, pk):
    doador = get_object_or_404(Doador, pk=pk)
    if request.method == 'POST':
        doador.delete()
        messages.success(request, "Doador excluído com sucesso.")
        return redirect('listar_doadores')
    return render(request, 'deletar_doador.html', {'doador': doador})

# --- RECEPTOR ---
def importar_receptores(request):
    if request.method == 'POST':
        form = ImportarReceptoresForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                json_file = form.cleaned_data['json_file']
                data = json.load(json_file)

                for item in data:
                    dados = item['dados']
                    dados.pop('id', None)

                    # Converte data
                    nascimento_str = dados.get('data_nascimento')
                    if nascimento_str:
                        dados['data_nascimento'] = datetime.strptime(nascimento_str, '%Y/%m/%d').date()

                    # Força campos que devem ser string
                    campos_char = [
                        'cidade_natal', 'estado_natal',
                        'cidade_residencia', 'estado_residencia',
                        'posicao_lista_espera', 'orgao_necessario',
                        'gravidade_condicao', 'centro_transplante',
                        'estado_civil', 'profissao', 'sexo', 'tipo_sanguineo',
                        'contato_emergencia'
                    ]
                    for campo in campos_char:
                        if campo in dados and dados[campo] is not None:
                            dados[campo] = str(dados[campo]).strip()

                    Receptor.objects.create(**dados)

                messages.success(request, "Receptores importados com sucesso.")
                return redirect('listar_receptores')

            except Exception as e:
                messages.error(request, f"Erro ao importar: {str(e)}")
    else:
        form = ImportarReceptoresForm()
    return render(request, 'importar_receptores.html', {'form': form})

@login_required
def cadastrar_receptor(request):
    if request.method == 'POST':
        form = CadastrarReceptorForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Receptor cadastrado com sucesso.")
            return redirect('listar_receptores')
    else:
        form = CadastrarReceptorForm()
    return render(request, 'cadastrar_receptores.html', {'form': form})




def listar_receptores(request):
    cpf = request.GET.get('cpf')
    receptores = Receptor.objects.all()

    if cpf:
        receptores = receptores.filter(cpf__icontains=cpf)

    paginator = Paginator(receptores, 10)  # Mostra 10 por página
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'listar_receptores.html', {
        'page_obj': page_obj,
        'cpf': cpf,
    })



def editar_receptor(request, pk):
    receptor = get_object_or_404(Receptor, pk=pk)
    if request.method == 'POST':
        form = CadastrarReceptorForm(request.POST, instance=receptor)
        if form.is_valid():
            form.save()
            messages.success(request, "Receptor atualizado com sucesso.")
            return redirect('listar_receptores')
    else:
        form = CadastrarReceptorForm(instance=receptor)
    return render(request, 'editar_receptores.html', {'form': form})


def deletar_receptor(request, pk):
    receptor = get_object_or_404(Receptor, pk=pk)
    if request.method == 'POST':
        receptor.delete()
        messages.success(request, "Receptor excluído com sucesso.")
        return redirect('listar_receptores')
    return render(request, 'deletar_receptores.html', {'receptor': receptor})

# --- ADMINISTRADOR ---

def cadastrar_administrador(request):
    if request.method == 'POST':
        form = CadastrarAdministradorForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Administrador cadastrado com sucesso.")
            return redirect('listar_administradores')
    else:
        form = CadastrarAdministradorForm()
    return render(request, 'cadastrar_administrador.html', {'form': form})

def listar_administradores(request):
    administradores = Administrador.objects.all()
    return render(request, 'listar_administradores.html', {'administradores': administradores})

def login_administrador(request):
    if request.method == 'POST':
        user = request.POST.get('username')
        senha = request.POST.get('password')
        user = authenticate(request, username=user, password=senha)

        if user is not None and user.is_staff:
            login(request, user)
            return redirect('painel_admin')
        else:
            messages.error(request, "Credenciais inválidas ou sem permissão.")
    return render(request, 'login_administrador.html')

@login_required
def logout_administrador(request):
    logout(request)
    return redirect('index')

def buscar_administrador(request, pk):
    administrador = get_object_or_404(Administrador, pk=pk)
    return render(request, 'detalhes_administrador.html', {'administrador': administrador})

def editar_administrador(request, pk):
    administrador = get_object_or_404(Administrador, pk=pk)
    if request.method == 'POST':
        form = CadastrarAdministradorForm(request.POST, instance=administrador)
        if form.is_valid():
            form.save()
            messages.success(request, "Administrador atualizado com sucesso.")
            return redirect('listar_administradores')
    else:
        form = CadastrarAdministradorForm(instance=administrador)
    return render(request, 'editar_administrador.html', {'form': form})

def excluir_administrador(request, pk):
    administrador = get_object_or_404(Administrador, pk=pk)
    if request.method == 'POST':
        administrador.delete()
        messages.success(request, "Administrador excluído com sucesso.")
        return redirect('listar_administradores')
    return render(request, 'excluir_administrador.html', {'administrador': administrador})

# --- ÓRGÃOS ---
@login_required
def listar_orgaos(request):
    orgaos = Orgao.objects.all()
    return render(request, 'listar_orgaos.html', {'orgaos': orgaos})

@login_required
def cadastrar_orgao(request):
    form = OrgaoForm(request.POST or None)
    if form.is_valid():
        form.save()
        messages.success(request, "Órgão cadastrado com sucesso.")
        return redirect('listar_orgaos')
    return render(request, 'cadastrar_orgao.html', {'form': form, 'title': 'Cadastrar'})

@login_required
def editar_orgao(request, pk):
    orgao = get_object_or_404(Orgao, pk=pk)
    form = OrgaoForm(request.POST or None, instance=orgao)
    if form.is_valid():
        form.save()
        messages.success(request, "Órgão atualizado com sucesso.")
        return redirect('listar_orgaos')
    return render(request, 'cadastrar_orgao.html', {'form': form, 'title': 'Editar'})

@login_required
def excluir_orgao(request, pk):
    orgao = get_object_or_404(Orgao, pk=pk)
    if request.method == 'POST':
        orgao.delete()
        messages.success(request, "Órgão excluído com sucesso.")
        return redirect('listar_orgaos')
    return render(request, 'excluir_orgao.html', {'orgao': orgao})

# --- CENTROS DE DISTRIBUIÇÃO ---
@login_required
def listar_centros(request):
    centros = CentroDistribuicao.objects.all()
    return render(request, 'listar_centros.html', {'centros': centros})

@login_required
def editar_centro(request, pk):
    centro = get_object_or_404(CentroDistribuicao, pk=pk)
    form = CentroDistribuicaoForm(request.POST or None, instance=centro)
    if form.is_valid():
        form.save()
        messages.success(request, "Centro atualizado com sucesso.")
        return redirect('listar_centros')
    return render(request, 'editar_centro.html', {'form': form})

def importar_administradores(request):
    if request.method == 'POST':
        form = ImportarAdministradoresForm(request.POST, request.FILES)
        if form.is_valid():
            arquivo_json = form.cleaned_data['json_file']
            dados_json = json.load(arquivo_json)

            # Se o JSON for uma lista de objetos assim:
            # [ { "dados": {...}, "acesso": {...} }, {...} ]
            # Caso contrário, adapte conforme seu JSON real.

            # Aqui verificamos se é uma lista ou só um dict:
            registros = dados_json
            if isinstance(dados_json, dict) and 'dados' in dados_json:
                registros = [dados_json]  # só um registro

            for registro in registros:
                dados = registro['dados']
                acesso = registro['acesso']

                # Converter data de nascimento para datetime.date
                data_nasc = datetime.strptime(dados['data_nascimento'], "%d/%m/%Y").date()

                # Criar ou atualizar User Django
                user, criado = User.objects.get_or_create(username=acesso['nome_usuario'])
                if criado:
                    user.password = make_password(acesso['senha'])
                    user.is_staff = True  # permite acesso ao admin
                    user.save()

                # Criar ou atualizar Administrador
                administrador, criado = Administrador.objects.update_or_create(
                    cpf=dados['cpf'],
                    defaults={
                        'user': user,
                        'nome': dados['nome'],
                        'tipo_sanguineo': dados['tipo_sanguineo'],
                        'data_nascimento': data_nasc,
                        'sexo': dados['sexo'],
                        'profissao': dados['profissao'],
                        'estado_natal': dados['estado_natal'],
                        'cidade_natal': dados['cidade_natal'],
                        'estado_residencia': dados['estado_residencia'],
                        'cidade_residencia': dados['cidade_residencia'],
                        'estado_civil': dados['estado_civil'],
                        'contato_emergencia': dados['contato_emergencia'],
                    }
                )
            messages.success(request, "Administradores importados com sucesso!")
            return redirect('painel_admin')

    else:
        form = ImportarAdministradoresForm()
    return render(request, 'importar_administradores.html', {'form': form})

@login_required
def importar_centros(request):
    if request.method == 'POST':
        form = ImportarCentrosForm(request.POST, request.FILES)
        if form.is_valid():
            json_file = form.cleaned_data['json_file']
            dados = json.load(json_file)

            # Se o JSON for uma lista de centros, iterar
            for item in dados:
                nome = item.get('_endereco') or item.get('_cidade') or 'Centro sem nome'
                estado = item.get('_estado')

                CentroDistribuicao.objects.update_or_create(
                    nome=nome,
                    estado=estado,
                    defaults={'estoque': item.get('_estoque')}
                )

            messages.success(request, "Centros de distribuição importados com sucesso!")
            return redirect('listar_centros')
    else:
        form = ImportarCentrosForm()
    return render(request, 'importar_centros.html', {'form': form})

@login_required
@user_passes_test(lambda u: u.is_superuser)
def painel_administrador(request):
    return render(request, 'meuapp/painel_administrador.html')