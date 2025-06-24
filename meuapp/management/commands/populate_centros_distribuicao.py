from django.core.management.base import BaseCommand
from meuapp.models import CentroDistribuicao

CAPITAIS_BRASIL = [
    ("Rio Branco", "AC"), ("Maceió", "AL"), ("Macapá", "AP"), ("Manaus", "AM"),
    ("Salvador", "BA"), ("Fortaleza", "CE"), ("Brasília", "DF"), ("Vitória", "ES"),
    ("Goiânia", "GO"), ("São Luís", "MA"), ("Cuiabá", "MT"), ("Campo Grande", "MS"),
    ("Belo Horizonte", "MG"), ("Belém", "PA"), ("João Pessoa", "PB"), ("Curitiba", "PR"),
    ("Recife", "PE"), ("Teresina", "PI"), ("Rio de Janeiro", "RJ"), ("Natal", "RN"),
    ("Porto Alegre", "RS"), ("Porto Velho", "RO"), ("Boa Vista", "RR"), ("Florianópolis", "SC"),
    ("São Paulo", "SP"), ("Aracaju", "SE"), ("Palmas", "TO")
]

class Command(BaseCommand):
    help = "Popula o banco de dados com os centros de distribuição nas capitais do Brasil."

    def handle(self, *args, **kwargs):
        criados = 0
        for cidade, estado in CAPITAIS_BRASIL:
            _, criado = CentroDistribuicao.objects.get_or_create(
                nome=cidade,
                estado=estado,
                defaults={"estoque": 0}
            )
            if criado:
                criados += 1
        self.stdout.write(self.style.SUCCESS(f'{criados} centros de distribuição criados com sucesso.'))
