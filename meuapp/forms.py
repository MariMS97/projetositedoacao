from django import forms
from django.core.exceptions import ValidationError
from django.contrib.auth.hashers import make_password
from .models import Doador, Receptor, Administrador, CentroDistribuicao, Orgao, Doacao
import re

# Estados e cidades do Brasil
BRAZILIAN_STATES_AND_CITIES = {
    "AC": ["Rio Branco", "Cruzeiro do Sul"],
    "AL": ["Maceió", "Arapiraca"],
    "AM": ["Manaus", "Parintins"],
    "AP": ["Macapá", "Santana"],
    "BA": ["Salvador", "Feira de Santana"],
    "CE": ["Fortaleza", "Caucaia"],
    "DF": ["Brasília"],
    "ES": ["Vitória", "Vila Velha"],
    "GO": ["Goiânia", "Aparecida de Goiânia", "Anápolis"],
    "MA": ["São Luís", "Imperatriz"],
    "MG": ["Belo Horizonte", "Uberlândia", "Contagem"],
    "MS": ["Campo Grande", "Dourados"],
    "MT": ["Cuiabá", "Várzea Grande"],
    "PA": ["Belém", "Ananindeua"],
    "PB": ["João Pessoa", "Campina Grande"],
    "PE": ["Recife", "Jaboatão dos Guararapes"],
    "PI": ["Teresina", "Parnaíba"],
    "PR": ["Curitiba", "Londrina", "Maringá"],
    "RJ": ["Rio de Janeiro", "Niterói", "Duque de Caxias"],
    "RN": ["Natal", "Mossoró"],
    "RO": ["Porto Velho", "Ji-Paraná"],
    "RR": ["Boa Vista"],
    "RS": ["Porto Alegre", "Caxias do Sul", "Canoas"],
    "SC": ["Florianópolis", "Joinville", "Blumenau"],
    "SE": ["Aracaju", "Nossa Senhora do Socorro"],
    "SP": ["São Paulo", "Campinas", "Guarulhos", "São Bernardo do Campo"],
    "TO": ["Palmas", "Araguaína"]
}

STATE_CHOICES = [('', 'Selecione o Estado')] + [(uf, uf) for uf in sorted(BRAZILIAN_STATES_AND_CITIES.keys())]

SEXO_CHOICES = [
    ('', 'Selecione'),
    ('M', 'Masculino'),
    ('F', 'Feminino')
]

TIPO_SANGUINEO_CHOICES = [
    ('', 'Selecione'),
    ('A+', 'A+'), ('A-', 'A-'),
    ('B+', 'B+'), ('B-', 'B-'),
    ('AB+', 'AB+'), ('AB-', 'AB-'),
    ('O+', 'O+'), ('O-', 'O-')
]

PROFISSAO_CHOICES = [
    ('', 'Selecione'),
    ('Engenheiro', 'Engenheiro'),
    ('Médico', 'Médico'),
    ('Professor', 'Professor'),
    ('Estudante', 'Estudante'),
    ('Aposentado', 'Aposentado'),
    ('Outra', 'Outra')
]

ESTADO_CIVIL_CHOICES = [
    ('', 'Selecione'),
    ('Solteiro', 'Solteiro'),
    ('Solteira', 'Solteira'),
    ('Casado', 'Casado'),
    ('Casada', 'Casada'),
    ('Divorciado', 'Divorciado'),
    ('Divorciada', 'Divorciada'),
    ('Viúvo', 'Viúvo'),
    ('Viúva', 'Viúva'),
    ('União Estável', 'União Estável')
]

class ImportarDoadoresForm(forms.Form):
    json_file = forms.FileField(
        label='Arquivo JSON',
        widget=forms.FileInput(attrs={'accept': '.json'})
    )

class CadastrarDoadorForm(forms.ModelForm):
    estado_natal = forms.ChoiceField(choices=STATE_CHOICES, label="Estado Natal")
    estado_residencia = forms.ChoiceField(choices=STATE_CHOICES, label="Estado de Residência")
    cidade_natal = forms.CharField(max_length=100, required=False, label="Cidade Natal")
    cidade_residencia = forms.CharField(max_length=100, required=False, label="Cidade de Residência")
    outra_profissao = forms.CharField(max_length=100, required=False)
    sexo = forms.ChoiceField(choices=SEXO_CHOICES, label="Sexo")
    tipo_sanguineo = forms.ChoiceField(choices=TIPO_SANGUINEO_CHOICES, label="Tipo Sanguíneo")
    profissao = forms.ChoiceField(choices=PROFISSAO_CHOICES, label="Profissão")
    estado_civil = forms.ChoiceField(choices=ESTADO_CIVIL_CHOICES, label="Estado Civil")
    
    intencao_doar = forms.BooleanField(
    required=False,
    label="Possui intenção de doar?",
    help_text="Marque se o doador tiver expressado intenção de doar."
    )

    orgaos_que_deseja_doar = forms.ModelMultipleChoiceField(
        queryset=Orgao.objects.all(),
        widget=forms.CheckboxSelectMultiple,  # ou SelectMultiple para dropdown múltiplo
        required=False,
        label="Órgãos que deseja doar"
    )
    class Meta:
        model = Doador
        fields = [
            'cpf', 'nome', 'tipo_sanguineo', 'data_nascimento', 'sexo',
            'profissao', 'estado_natal', 'cidade_natal', 'estado_residencia',
            'cidade_residencia', 'estado_civil', 'contato_emergencia','intencao_doar', 'orgaos_que_deseja_doar'
        ]
        widgets = {
            'data_nascimento': forms.DateInput(format='%Y/%m/%d', attrs={'type': 'date'}),
        }
        input_formats = {'data_nascimento': ['%Y/%m/%d', '%Y-%m-%d']}
    
    def clean_cpf(self):
        cpf = self.cleaned_data.get('cpf')

        # Valida formato com pontos e traço
        if not re.fullmatch(r'\d{3}\.\d{3}\.\d{3}-\d{2}', cpf or ''):
            raise ValidationError('CPF deve estar no formato 000.000.000-00.')

        # Remove pontuação apenas para armazenar
        cpf_numeros = cpf.replace('.', '').replace('-', '')

        if Doador.objects.filter(cpf=cpf_numeros).exists():
            raise ValidationError('Este CPF já está cadastrado como doador.')

        if Receptor.objects.filter(cpf=cpf_numeros).exists():
            raise ValidationError('Este CPF já está cadastrado como receptor.')

        return cpf_numeros
    
    def clean(self):
        dados_validados = super().clean()
        profissao = dados_validados.get('profissao')
        outra_profissao = dados_validados.get('outra_profissao')
        sexo = dados_validados.get('sexo')
        estado_civil = dados_validados.get('estado_civil')

        if profissao == 'Outra' and not outra_profissao:
            self.add_error('outra_profissao', 'Por favor, especifique a outra profissão.')
        elif profissao == 'Outra' and outra_profissao:
            dados_validados['profissao'] = outra_profissao

        if dados_validados.get('estado_natal') and not dados_validados.get('cidade_natal'):
            self.add_error('cidade_natal', 'Cidade natal é obrigatória quando o estado é selecionado.')

        if dados_validados.get('estado_residencia') and not dados_validados.get('cidade_residencia'):
            self.add_error('cidade_residencia', 'Cidade de residência é obrigatória quando o estado é selecionado.')

        masculino_estados = ['Solteiro', 'Casado', 'Divorciado', 'Viúvo']
        feminino_estados = ['Solteira', 'Casada', 'Divorciada', 'Viúva']
        if sexo == 'M' and estado_civil in feminino_estados:
            self.add_error('estado_civil', 'Estado civil selecionado não corresponde ao sexo masculino.')
        elif sexo == 'F' and estado_civil in masculino_estados:
            self.add_error('estado_civil', 'Estado civil selecionado não corresponde ao sexo feminino.')

        return dados_validados


class ImportarReceptoresForm(forms.Form):
    json_file = forms.FileField(
        label='Arquivo JSON',
        widget=forms.FileInput(attrs={'accept': '.json'})
    )

class CadastrarReceptorForm(forms.ModelForm):
    estado_natal = forms.ChoiceField(choices=STATE_CHOICES, label="Estado Natal")
    estado_residencia = forms.ChoiceField(choices=STATE_CHOICES, label="Estado de Residência")
    cidade_natal = forms.CharField(max_length=100, required=False, label="Cidade Natal")
    cidade_residencia = forms.CharField(max_length=100, required=False, label="Cidade de Residência")
    outra_profissao = forms.CharField(max_length=100, required=False)
    sexo = forms.ChoiceField(choices=SEXO_CHOICES, label="Sexo")
    tipo_sanguineo = forms.ChoiceField(choices=TIPO_SANGUINEO_CHOICES, label="Tipo Sanguíneo")
    profissao = forms.ChoiceField(choices=PROFISSAO_CHOICES, label="Profissão")
    estado_civil = forms.ChoiceField(choices=ESTADO_CIVIL_CHOICES, label="Estado Civil")
    
    class Meta:
        model = Receptor
        fields = [
            'cpf', 'nome', 'tipo_sanguineo', 'data_nascimento', 'sexo',
            'profissao', 'estado_natal', 'cidade_natal', 'estado_residencia',
            'cidade_residencia', 'estado_civil', 'contato_emergencia',
            'orgao_necessario', 'gravidade_condicao', 'centro_transplante', 'posicao_lista_espera'
        ]
        widgets = {
            'data_nascimento': forms.DateInput(format='%Y/%m/%d', attrs={'type': 'date'}),
        }
        input_formats = {'data_nascimento': ['%Y/%m/%d', '%Y-%m-%d']}
    
    def clean_cpf(self):
        cpf = self.cleaned_data.get('cpf')

        # Valida formato com pontos e traço
        if not re.fullmatch(r'\d{3}\.\d{3}\.\d{3}-\d{2}', cpf or ''):
            raise ValidationError('CPF deve estar no formato 000.000.000-00.')

        # Remove pontuação apenas para armazenar
        cpf_numeros = cpf.replace('.', '').replace('-', '')

        if Doador.objects.filter(cpf=cpf_numeros).exists():
            raise ValidationError('Este CPF já está cadastrado como doador.')

        if Receptor.objects.filter(cpf=cpf_numeros).exists():
            raise ValidationError('Este CPF já está cadastrado como receptor.')

        return cpf_numeros
    
    def clean(self):
        dados_validados = super().clean()
        profissao = dados_validados.get('profissao')
        outra_profissao = dados_validados.get('outra_profissao')
        sexo = dados_validados.get('sexo')
        estado_civil = dados_validados.get('estado_civil')

        if profissao == 'Outra' and not outra_profissao:
            self.add_error('outra_profissao', 'Por favor, especifique a outra profissão.')
        elif profissao == 'Outra' and outra_profissao:
            dados_validados['profissao'] = outra_profissao

        if dados_validados.get('estado_natal') and not dados_validados.get('cidade_natal'):
            self.add_error('cidade_natal', 'Cidade natal é obrigatória quando o estado é selecionado.')

        if dados_validados.get('estado_residencia') and not dados_validados.get('cidade_residencia'):
            self.add_error('cidade_residencia', 'Cidade de residência é obrigatória quando o estado é selecionado.')

        masculino_estados = ['Solteiro', 'Casado', 'Divorciado', 'Viúvo']
        feminino_estados = ['Solteira', 'Casada', 'Divorciada', 'Viúva']
        if sexo == 'M' and estado_civil in feminino_estados:
            self.add_error('estado_civil', 'Estado civil selecionado não corresponde ao sexo masculino.')
        elif sexo == 'F' and estado_civil in masculino_estados:
            self.add_error('estado_civil', 'Estado civil selecionado não corresponde ao sexo feminino.')

        return dados_validados

from django import forms
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.contrib.auth.hashers import make_password
from .models import Administrador, Doador, Receptor
import re

class CadastrarAdministradorForm(forms.ModelForm):
    # Renomeado: user → username (para não conflitar com o model User)
    username = forms.CharField(label='Nome de Usuário')
    email = forms.EmailField(label='E-mail')
    senha = forms.CharField(widget=forms.PasswordInput(), label="Senha")
    confirmar_senha = forms.CharField(widget=forms.PasswordInput(), label="Confirmar Senha")

    # Campos adicionais
    estado_natal = forms.ChoiceField(choices=STATE_CHOICES, label="Estado Natal")
    estado_residencia = forms.ChoiceField(choices=STATE_CHOICES, label="Estado de Residência")
    cidade_natal = forms.CharField(max_length=100, required=False, label="Cidade Natal")
    cidade_residencia = forms.CharField(max_length=100, required=False, label="Cidade de Residência")
    outra_profissao = forms.CharField(max_length=100, required=False)
    sexo = forms.ChoiceField(choices=SEXO_CHOICES, label="Sexo")
    tipo_sanguineo = forms.ChoiceField(choices=TIPO_SANGUINEO_CHOICES, label="Tipo Sanguíneo")
    profissao = forms.ChoiceField(choices=PROFISSAO_CHOICES, label="Profissão")
    estado_civil = forms.ChoiceField(choices=ESTADO_CIVIL_CHOICES, label="Estado Civil")

    class Meta:
        model = Administrador
        exclude = ['user']  # O user é criado no save()

        widgets = {
            'data_nascimento': forms.DateInput(format='%Y/%m/%d', attrs={'type': 'date'}),
        }

        input_formats = {
            'data_nascimento': ['%Y/%m/%d', '%Y-%m-%d']
        }

    def clean_cpf(self):
        cpf = self.cleaned_data.get('cpf')

        if not re.fullmatch(r'\d{3}\.\d{3}\.\d{3}-\d{2}', cpf or ''):
            raise ValidationError('CPF deve estar no formato 000.000.000-00.')

        cpf_numeros = cpf.replace('.', '').replace('-', '')

        if Doador.objects.filter(cpf=cpf_numeros).exists():
            raise ValidationError('Este CPF já está cadastrado como doador.')

        if Receptor.objects.filter(cpf=cpf_numeros).exists():
            raise ValidationError('Este CPF já está cadastrado como receptor.')

        return cpf_numeros

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exists():
            raise ValidationError('Este nome de usuário já está em uso.')
        return username

    def clean(self):
        dados = super().clean()
        profissao = dados.get('profissao')
        outra_profissao = dados.get('outra_profissao')
        sexo = dados.get('sexo')
        estado_civil = dados.get('estado_civil')
        senha = dados.get('senha')
        confirmar = dados.get('confirmar_senha')

        if profissao == 'Outra' and not outra_profissao:
            self.add_error('outra_profissao', 'Por favor, especifique a outra profissão.')
        elif profissao == 'Outra':
            dados['profissao'] = outra_profissao

        if dados.get('estado_natal') and not dados.get('cidade_natal'):
            self.add_error('cidade_natal', 'Cidade natal é obrigatória quando o estado é selecionado.')

        if dados.get('estado_residencia') and not dados.get('cidade_residencia'):
            self.add_error('cidade_residencia', 'Cidade de residência é obrigatória quando o estado é selecionado.')

        masculino = ['Solteiro', 'Casado', 'Divorciado', 'Viúvo']
        feminino = ['Solteira', 'Casada', 'Divorciada', 'Viúva']

        if sexo == 'M' and estado_civil in feminino:
            self.add_error('estado_civil', 'Estado civil selecionado não corresponde ao sexo masculino.')
        elif sexo == 'F' and estado_civil in masculino:
            self.add_error('estado_civil', 'Estado civil selecionado não corresponde ao sexo feminino.')

        if senha and confirmar and senha != confirmar:
            self.add_error('confirmar_senha', 'As senhas não coincidem.')

        return dados

    def save(self, commit=True):
        dados = self.cleaned_data

        # Cria o User do Django
        username = dados.get('username')
        email = dados.get('email')
        senha = dados.get('senha')

        user = User.objects.create_user(username=username, email=email, password=senha)
        user.is_staff = True
        user.save()

        # Cria o Administrador associado ao User
        admin = super().save(commit=False)
        admin.user = user
        if commit:
            admin.save()
        return admin


class ImportarAdministradoresForm(forms.Form):
    json_file = forms.FileField(
        label='Arquivo JSON',
        widget=forms.FileInput(attrs={'accept': '.json'})
    )

class ImportarCentrosForm(forms.Form):
    json_file = forms.FileField(
        label='Arquivo JSON',
        widget=forms.FileInput(attrs={'accept': '.json'})
    )

class OrgaoForm(forms.ModelForm):
    class Meta:
        model = Orgao
        fields = ['nome', 'tipo']

class CentroDistribuicaoForm(forms.ModelForm):
    class Meta:
        model = CentroDistribuicao
        fields = ['nome', 'estado', 'cidade', 'ativo']

def obter_compatibilidade(tipo_sanguineo):
    compatibilidade = {
        'O-': ['O-'],
        'O+': ['O-', 'O+'],
        'A-': ['O-', 'A-'],
        'A+': ['O-', 'O+', 'A-', 'A+'],
        'B-': ['O-', 'B-'],
        'B+': ['O-', 'O+', 'B-', 'B+'],
        'AB-': ['O-', 'A-', 'B-', 'AB-'],
        'AB+': ['O-', 'O+', 'A-', 'A+', 'B-', 'B+', 'AB-', 'AB+'],
    }
    return compatibilidade.get(tipo_sanguineo, [])


class RegistrarDoacaoForm(forms.ModelForm):
    class Meta:
        model = Doacao
        fields = ['doador', 'orgao', 'receptor']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Garante que o campo doador apareça corretamente
        self.fields['doador'].queryset = Doador.objects.all()

        doador_id = None

        if 'doador' in self.data:
            doador_id = self.data.get('doador')
        elif self.instance and self.instance.pk:
            doador_id = self.instance.doador.pk

        if doador_id:
            try:
                doador = Doador.objects.get(pk=int(doador_id))
                self.fields['orgao'].queryset = doador.orgaos_que_deseja_doar.all()

                
                tipos_compat = obter_compatibilidade(doador.tipo_sanguineo)
                self.fields['receptor'].queryset = Receptor.objects.filter(tipo_sanguineo__in=tipos_compat)
            except (ValueError, Doador.DoesNotExist):
                self.fields['orgao'].queryset = Orgao.objects.none()
                self.fields['receptor'].queryset = Receptor.objects.none()
        else:
            self.fields['orgao'].queryset = Orgao.objects.none()
            self.fields['receptor'].queryset = Receptor.objects.none()

INTENCAO_DOAR_CHOICES = [
    ('s', 'Sim'),
    ('n', 'Não')
]

intencao_doar = forms.ChoiceField(
    choices=INTENCAO_DOAR_CHOICES,
    label="Tem intenção de doar?",
    required=True,
    widget=forms.RadioSelect  # ou forms.Select para dropdown
)