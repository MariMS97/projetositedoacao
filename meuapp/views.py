from django.shortcuts import render
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .forms import (
    ImportarDoadoresForm, CadastrarDoadorForm,
    ImportarReceptoresForm, CadastrarReceptorForm
)
from .models import Doador, Receptor
import json

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
                    Doador.objects.create(**dados)
                messages.success(request, "Doadores importados com sucesso.")
                return redirect('listar_doadores')
            except Exception as e:
                messages.error(request, f"Erro ao importar: {str(e)}")
    else:
        form = ImportarDoadoresForm()
    return render(request, 'doadores/importar.html', {'form': form})


def cadastrar_doador(request):
    if request.method == 'POST':
        form = CadastrarDoadorForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Doador cadastrado com sucesso.")
            return redirect('listar_doadores')
    else:
        form = CadastrarDoadorForm()
    return render(request, 'doadores/cadastrar.html', {'form': form})


def listar_doadores(request):
    doadores = Doador.objects.all()
    return render(request, 'doadores/listar.html', {'doadores': doadores})


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
    return render(request, 'doadores/editar.html', {'form': form})


def deletar_doador(request, pk):
    doador = get_object_or_404(Doador, pk=pk)
    if request.method == 'POST':
        doador.delete()
        messages.success(request, "Doador excluído com sucesso.")
        return redirect('listar_doadores')
    return render(request, 'doadores/deletar.html', {'doador': doador})


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
                    Receptor.objects.create(**dados)
                messages.success(request, "Receptores importados com sucesso.")
                return redirect('listar_receptores')
            except Exception as e:
                messages.error(request, f"Erro ao importar: {str(e)}")
    else:
        form = ImportarReceptoresForm()
    return render(request, 'receptores/importar.html', {'form': form})


def cadastrar_receptor(request):
    if request.method == 'POST':
        form = CadastrarReceptorForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Receptor cadastrado com sucesso.")
            return redirect('listar_receptores')
    else:
        form = CadastrarReceptorForm()
    return render(request, 'receptores/cadastrar.html', {'form': form})


def listar_receptores(request):
    receptores = Receptor.objects.all()
    return render(request, 'receptores/listar.html', {'receptores': receptores})


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
    return render(request, 'receptores/editar.html', {'form': form})


def deletar_receptor(request, pk):
    receptor = get_object_or_404(Receptor, pk=pk)
    if request.method == 'POST':
        receptor.delete()
        messages.success(request, "Receptor excluído com sucesso.")
        return redirect('listar_receptores')
    return render(request, 'receptores/deletar.html', {'receptor': receptor})
