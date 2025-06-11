from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .forms import (
    ImportarDoadoresForm, CadastrarDoadorForm,
    ImportarReceptoresForm, CadastrarReceptorForm
)
from .models import Doador, Receptor
from datetime import datetime
import json

# --- Página Inicial ---
def home(request):
    return render(request, 'home.html')

def pagina_do_doador(request):
    return render(request, 'pagina_do_doador.html')

def pagina_do_receptor(request):
    return render(request, 'pagina_do_receptor.html')

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


from django.core.paginator import Paginator

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
