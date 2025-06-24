from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import user_passes_test
from datetime import datetime
import json
from .models import Doador, Receptor, Administrador, Orgao, CentroDistribuicao, Doacao
from .forms import (
    ImportarDoadoresForm, CadastrarDoadorForm,
    ImportarReceptoresForm, CadastrarReceptorForm,
    CadastrarAdministradorForm,
    ImportarAdministradoresForm, ImportarCentrosForm,
    OrgaoForm, CentroDistribuicaoForm,
    RegistrarDoacaoForm
)
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
from django.core.paginator import Paginator
from django.views.decorators.http import require_POST

# --- Verificação de administrador ---
def is_admin(user):
    return user.is_authenticated and (user.is_staff or user.is_superuser)

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
@user_passes_test(is_admin)
def importar_doadores(request):
    if request.method == 'POST':
        form = ImportarDoadoresForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                json_file = form.cleaned_data['json_file']
                data = json.load(json_file)

                for item in data:
                    dados = item.get('dados', {})
                    intencao = item.get('intencao', {})

                    dados.pop('id', None)
                    dados.pop('idade', None)

                    nascimento_str = dados.get('data_nascimento')
                    if nascimento_str:
                        dados['data_nascimento'] = datetime.strptime(nascimento_str, '%Y/%m/%d').date()

                    status_intencao_raw = intencao.get('status', False)
                    if isinstance(status_intencao_raw, str):
                        intencao_doar = status_intencao_raw.lower() in ['s', 'sim', 'true']
                    else:
                        intencao_doar = bool(status_intencao_raw)

                    doador, created = Doador.objects.update_or_create(
                        cpf=dados.get('cpf'),
                        defaults={**dados, 'intencao_doar': intencao_doar}
                    )

                    orgaos_nomes = intencao.get('orgaos_nomes', [])
                    if orgaos_nomes:
                        orgaos = Orgao.objects.filter(nome__in=orgaos_nomes)
                        doador.orgaos_que_deseja_doar.set(orgaos)
                    else:
                        doador.orgaos_que_deseja_doar.clear()

                messages.success(request, "Doadores importados com sucesso.")
                return redirect('listar_doadores')
            except Exception as e:
                messages.error(request, f"Erro ao importar: {str(e)}")
    else:
        form = ImportarDoadoresForm()

    return render(request, 'importar_doador.html', {'form': form})

@user_passes_test(is_admin)
def cadastrar_doador(request):
    if request.method == 'POST':
        form = CadastrarDoadorForm(request.POST)
        if form.is_valid():
            doador = form.save(commit=False)  # salva os campos normais
            doador.save()
            form.save_m2m()  # salva os muitos-para-muitos (orgaos_que_deseja_doar)

            messages.success(request, 'Doador cadastrado com sucesso.')
            return redirect('pagina_do_doador')
        else:
            messages.error(request, 'Erro ao cadastrar doador. Verifique os campos.')
    else:
        form = CadastrarDoadorForm()

    return render(request, 'cadastrar_doador.html', {'form': form})

@user_passes_test(is_admin)
def listar_doadores(request):
    cpf = request.GET.get('cpf')
    doadores = Doador.objects.all().order_by('nome')
    if cpf:
        doadores = doadores.filter(cpf__icontains=cpf)
    paginator = Paginator(doadores, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'listar_doador.html', {'page_obj': page_obj, 'cpf': cpf})

@user_passes_test(is_admin)
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

@user_passes_test(is_admin)
def deletar_doador(request, pk):
    doador = get_object_or_404(Doador, pk=pk)
    if request.method == 'POST':
        doador.delete()
        messages.success(request, "Doador excluído com sucesso.")
        return redirect('listar_doadores')
    return render(request, 'deletar_doador.html', {'doador': doador})

# --- RECEPTOR ---
@user_passes_test(is_admin)
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
                    nascimento_str = dados.get('data_nascimento')
                    if nascimento_str:
                        dados['data_nascimento'] = datetime.strptime(nascimento_str, '%Y/%m/%d').date()
                    campos_char = ['cidade_natal', 'estado_natal', 'cidade_residencia', 'estado_residencia',
                                'posicao_lista_espera', 'orgao_necessario', 'gravidade_condicao',
                                'centro_transplante', 'estado_civil', 'profissao', 'sexo',
                                'tipo_sanguineo', 'contato_emergencia']
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

@user_passes_test(is_admin)
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

@user_passes_test(is_admin)
def listar_receptores(request):
    cpf = request.GET.get('cpf')
    receptores = Receptor.objects.all()
    if cpf:
        receptores = receptores.filter(cpf__icontains=cpf)
    paginator = Paginator(receptores, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'listar_receptores.html', {'page_obj': page_obj, 'cpf': cpf})

@user_passes_test(is_admin)
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

@user_passes_test(is_admin)
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
            return redirect('login_administrador')
    else:
        form = CadastrarAdministradorForm()
    return render(request, 'cadastrar_administrador.html', {'form': form})

@user_passes_test(is_admin)
def listar_administradores(request):
    administradores = Administrador.objects.all()
    return render(request, 'listar_administradores.html', {'administradores': administradores})

def login_administrador(request):
    mostrar_cadastro = True

    if request.method == 'POST':
        username = request.POST.get('username')
        senha = request.POST.get('password')
        user = authenticate(request, username=username, password=senha)

        if user is not None and user.is_staff:
            login(request, user)
            next_url = request.POST.get('next') or request.GET.get('next')
            return redirect(next_url or 'painel_admin') 
        else:
            messages.error(request, "Credenciais inválidas ou sem permissão.")
    
    return render(request, 'login_administrador.html', {'mostrar_cadastro': mostrar_cadastro})

@user_passes_test(is_admin)
def logout_administrador(request):
    logout(request)
    return redirect('index')

@user_passes_test(is_admin)
def buscar_administrador(request, pk):
    administrador = get_object_or_404(Administrador, pk=pk)
    return render(request, 'detalhes_administrador.html', {'administrador': administrador})

@user_passes_test(is_admin)
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

@user_passes_test(is_admin)
def excluir_administrador(request, pk):
    administrador = get_object_or_404(Administrador, pk=pk)
    if request.method == 'POST':
        administrador.delete()
        messages.success(request, "Administrador excluído com sucesso.")
        return redirect('listar_administradores')
    return render(request, 'excluir_administrador.html', {'administrador': administrador})

# --- ÓRGÃOS ---
@user_passes_test(is_admin)
def listar_orgaos(request):
    orgaos = Orgao.objects.all()
    return render(request, 'listar_orgaos.html', {'orgaos': orgaos})

@user_passes_test(is_admin)
def cadastrar_orgao(request):
    form = OrgaoForm(request.POST or None)
    if form.is_valid():
        form.save()
        messages.success(request, "Órgão cadastrado com sucesso.")
        return redirect('listar_orgaos')
    return render(request, 'cadastrar_orgao.html', {'form': form, 'title': 'Cadastrar'})

@user_passes_test(is_admin)
def editar_orgao(request, pk):
    orgao = get_object_or_404(Orgao, pk=pk)
    form = OrgaoForm(request.POST or None, instance=orgao)
    if form.is_valid():
        form.save()
        messages.success(request, "Órgão atualizado com sucesso.")
        return redirect('listar_orgaos')
    return render(request, 'cadastrar_orgao.html', {'form': form, 'title': 'Editar'})

@user_passes_test(is_admin)
def excluir_orgao(request, pk):
    orgao = get_object_or_404(Orgao, pk=pk)
    if request.method == 'POST':
        orgao.delete()
        messages.success(request, "Órgão excluído com sucesso.")
        return redirect('listar_orgaos')
    return render(request, 'excluir_orgao.html', {'orgao': orgao})

# --- CENTROS DE DISTRIBUIÇÃO ---
@user_passes_test(is_admin)
def listar_centros(request):
    centros = CentroDistribuicao.objects.all()
    return render(request, 'listar_centros.html', {'centros': centros})

@user_passes_test(is_admin)
def editar_centro(request, pk):
    centro = get_object_or_404(CentroDistribuicao, pk=pk)
    form = CentroDistribuicaoForm(request.POST or None, instance=centro)
    if form.is_valid():
        form.save()
        messages.success(request, "Centro atualizado com sucesso.")
        return redirect('listar_centros')
    return render(request, 'editar_centro.html', {'form': form})

@user_passes_test(is_admin)
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
                user, criado = User.objects.get_or_create(username=acesso['user'])
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
    return render(request, 'importar_admin.html', {'form': form})

@user_passes_test(is_admin)
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

@user_passes_test(is_admin)
def painel_admin(request):
    return render(request, 'painel_admin.html')

def tipos_sanguineos_compatíveis(tipo_receptor):
    compatibilidade = {
        'A+': ['A+', 'A-', 'O+', 'O-'],
        'A-': ['A-', 'O-'],
        'B+': ['B+', 'B-', 'O+', 'O-'],
        'B-': ['B-', 'O-'],
        'AB+': ['A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-'],
        'AB-': ['A-', 'B-', 'AB-', 'O-'],
        'O+': ['O+', 'O-'],
        'O-': ['O-']
    }
    return compatibilidade.get(tipo_receptor, [])

def registrar_doacao(request):
    doador_id = request.GET.get('doador')

    if request.method == 'POST':
        form = RegistrarDoacaoForm(request.POST)
        if form.is_valid():
            doacao = form.save(commit=False)
            doador = doacao.doador
            receptor = doacao.receptor
            orgao = doacao.orgao

            compat_sang = doador.tipo_sanguineo in tipos_sanguineos_compatíveis(receptor.tipo_sanguineo)
            compat_orgao = orgao in doador.orgaos_que_deseja_doar.all()

            print("Intenção:", doador.intencao_doar)
            print("Órgão compatível:", compat_orgao)
            print("Sangue compatível:", compat_sang)

            if compat_sang and compat_orgao and doador.intencao_doar:
                doacao.status = 'PROCESSANDO'
                messages.success(request, 'Doação registrada com status: Em Processamento.')
            else:
                doacao.status = 'CONSULTA'
                messages.info(request, 'Doação registrada com status: Em Consulta (aguardando confirmação).')

            doacao.save()
            return redirect('historico_doacoes')
        else:
            messages.error(request, "Erro ao registrar doação. Verifique os dados.")
    else:
        form = RegistrarDoacaoForm()
        if doador_id:
            try:
                doador = Doador.objects.get(pk=doador_id)
                form.fields['orgao'].queryset = doador.orgaos_que_deseja_doar.all()
                tipos_compat = tipos_sanguineos_compatíveis(doador.tipo_sanguineo)
                form.fields['receptor'].queryset = Receptor.objects.filter(tipo_sanguineo__in=tipos_compat)
            except Doador.DoesNotExist:
                form.fields['orgao'].queryset = Orgao.objects.none()
                form.fields['receptor'].queryset = Receptor.objects.none()
        else:
            form.fields['orgao'].queryset = Orgao.objects.none()
            form.fields['receptor'].queryset = Receptor.objects.none()

    return render(request, 'registrar_doacao.html', {'form': form})


# Buscar doadores e receptores compatíveis
def buscar_doadores_compatíveis(request, receptor_id):
    receptor = get_object_or_404(Receptor, id=receptor_id)
    compatíveis = []

    for doador in Doador.objects.all():
        if (
            doador.tipo_sanguineo in tipos_sanguineos_compatíveis(receptor.tipo_sanguineo) and
            receptor.orgao_necessario in doador.orgaos_desejados.all()
        ):
            compatíveis.append(doador)

    return render(request, 'doadores_compatíveis.html', {
        'receptor': receptor,
        'doadores': compatíveis
    })

def historico_doacoes(request):
    status = request.GET.get('status')
    doacoes = Doacao.objects.all().order_by('-data_registro')
    
    if status:
        doacoes = doacoes.filter(status=status)

    return render(request, 'historico_doacoes.html', {
        'doacoes': doacoes,
        'status_selecionado': status
    })


def concluir_doacao(request, doacao_id):
    doacao = get_object_or_404(Doacao, id=doacao_id)
    if doacao.status == 'PROCESSANDO':
        doacao.status = 'CONCLUIDA'
        doacao.save()
    return redirect('historico_doacoes')


def cancelar_doacao(request, doacao_id):
    doacao = get_object_or_404(Doacao, id=doacao_id)
    if doacao.status in ['PROCESSANDO', 'CONSULTA']:
        doacao.status = 'CANCELADA'
        doacao.save()
    return redirect('historico_doacoes')

