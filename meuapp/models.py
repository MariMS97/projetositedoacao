# models.py (limpo, corrigido e pronto para uso)
from django.db import models
from datetime import date
from django.contrib.auth.models import User

# --- Choices ---
SEXO_CHOICES = [
    ('M', 'Masculino'),
    ('F', 'Feminino')
]

TIPO_SANGUINEO_CHOICES = [
    ('A+', 'A+'), ('A-', 'A-'),
    ('B+', 'B+'), ('B-', 'B-'),
    ('AB+', 'AB+'), ('AB-', 'AB-'),
    ('O+', 'O+'), ('O-', 'O-')
]

ESTADO_CIVIL_CHOICES = [
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

# --- Modelo Abstrato Pessoa ---
class Pessoa(models.Model):
    cpf = models.CharField(max_length=11, unique=True)
    nome = models.CharField(max_length=100)
    tipo_sanguineo = models.CharField(max_length=3, choices=TIPO_SANGUINEO_CHOICES)
    data_nascimento = models.DateField()
    sexo = models.CharField(max_length=1, choices=SEXO_CHOICES)
    profissao = models.CharField(max_length=100)
    estado_natal = models.CharField(max_length=2)
    cidade_natal = models.CharField(max_length=100)
    estado_residencia = models.CharField(max_length=2)
    cidade_residencia = models.CharField(max_length=100)
    estado_civil = models.CharField(max_length=20, choices=ESTADO_CIVIL_CHOICES)
    contato_emergencia = models.CharField(max_length=15)

    class Meta:
        abstract = True

    @property
    def idade(self):
        hoje = date.today()
        if self.data_nascimento:
            return hoje.year - self.data_nascimento.year - ((hoje.month, hoje.day) < (self.data_nascimento.month, self.data_nascimento.day))
        return None

# --- Modelos concretos ---
class Doador(Pessoa):
    intencao_doar = models.JSONField(null=True, blank=True)

    def __str__(self):
        return f"{self.nome} ({self.cpf})"

class Receptor(Pessoa):
    orgao_necessario = models.CharField(max_length=50)
    gravidade_condicao = models.CharField(max_length=50)
    centro_transplante = models.CharField(max_length=100)
    posicao_lista_espera = models.CharField(max_length=1000)
    data_cadastro = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"{self.nome} ({self.cpf})"

class Administrador(Pessoa):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.nome

class Orgao(models.Model):
    nome = models.CharField(max_length=100)
    tipo = models.CharField(max_length=50, choices=[
        ('Orgão', 'Orgão'),
        ('Tecido', 'Tecido'),
        ('Sangue', 'Sangue'),
    ])

    def __str__(self):
        return self.nome


class CentroDistribuicao(models.Model):
    
    nome = models.CharField(max_length=100)
    ativo = models.BooleanField(default=True)
    endereço = models.CharField(max_length=100)  # Podemos usar o endereço como nome do centro
    cidade = models.CharField(max_length=100)
    estado = models.CharField(max_length=2)
    telefone = models.CharField(max_length=20, blank=True, null=True)
    estoque = models.JSONField(null=True, blank=True)  # Para armazenar o estoque dos órgãos

    def __str__(self):
        return f"{self.nome} - {self.cidade}/{self.estado}"

