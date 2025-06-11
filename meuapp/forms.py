from django import forms
from .models import Doador, Receptor
from datetime import date

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

    class Meta:
        model = Doador
        fields = [
            'cpf', 'nome', 'tipo_sanguineo', 'data_nascimento', 'sexo',
            'profissao', 'estado_natal', 'cidade_natal', 'estado_residencia',
            'cidade_residencia', 'estado_civil', 'contato_emergencia'
        ]
        widgets = {
            'data_nascimento': forms.DateInput(format='%Y/%m/%d', attrs={'type': 'date'}),
        }
        input_formats = {'data_nascimento': ['%Y/%m/%d', '%Y-%m-%d']}

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
