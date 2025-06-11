from django.test import TestCase
from .models import Doador, Receptor
from datetime import date

class DoadorModelTest(TestCase):
    def test_criar_doador(self):
        doador = Doador.objects.create(
            cpf="12345678900",
            nome="João da Silva",
            tipo_sanguineo="O+",
            data_nascimento=date(1990, 5, 10),
            idade=34,
            sexo="M",
            profissao="Engenheiro",
            estado_natal="SP",
            cidade_natal="São Paulo",
            estado_residencia="SP",
            cidade_residencia="São Paulo",
            estado_civil="Solteiro",
            contato_emergencia="11999999999",
            intencao_doar={"deseja_doar": True, "orgaos": ["Rins", "Coração"]}
        )
        self.assertEqual(doador.nome, "João da Silva")
        self.assertEqual(doador.intencao_doar["deseja_doar"], True)

class ReceptorModelTest(TestCase):
    def test_criar_receptor(self):
        receptor = Receptor.objects.create(
            cpf="98765432100",
            nome="Maria Oliveira",
            tipo_sanguineo="A-",
            data_nascimento=date(1985, 3, 22),
            idade=39,
            sexo="F",
            profissao="Médica",
            estado_natal="RJ",
            cidade_natal="Rio de Janeiro",
            estado_residencia="RJ",
            cidade_residencia="Rio de Janeiro",
            estado_civil="Casado",
            contato_emergencia="21999999999",
            orgao_necessario="Fígado",
            gravidade_condicao="Alta",
            centro_transplante_vinculado="Hospital Central",
            posicao_lista_espera="5"
        )
        self.assertEqual(receptor.orgao_necessario, "Fígado")
        self.assertEqual(receptor.posicao_lista_espera, "5")
