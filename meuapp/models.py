from django.db import models
from datetime import date

SEXO_CHOICES = [
    ('M', 'Masculino'),
    ('F', 'Feminino'),
    ('O', 'Outro'),
]

TIPO_SANGUINEO_CHOICES = [
    ('A+', 'A+'), ('A-', 'A-'),
    ('B+', 'B+'), ('B-', 'B-'),
    ('AB+', 'AB+'), ('AB-', 'AB-'),
    ('O+', 'O+'), ('O-', 'O-')
]

ESTADO_CIVIL_CHOICES = [
    ('Solteiro', 'Solteiro'),
    ('Casado', 'Casado'),
    ('Divorciado', 'Divorciado'),
    ('Viuvo', 'Viúvo'),
    ('União Estável', 'União Estável')
]

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


class Doador(Pessoa):
    intencao_doar = models.JSONField(null=True, blank=True)  # {"deseja_doar": True, "orgaos": ["Coração", "Rins"]}

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
