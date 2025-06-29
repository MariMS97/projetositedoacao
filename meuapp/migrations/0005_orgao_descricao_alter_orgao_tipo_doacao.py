# Generated by Django 5.2.1 on 2025-06-21 18:46

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('meuapp', '0004_centrodistribuicao_orgao_alter_doador_estado_civil_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='orgao',
            name='descricao',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='orgao',
            name='tipo',
            field=models.CharField(max_length=50),
        ),
        migrations.CreateModel(
            name='Doacao',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('data_registro', models.DateTimeField(auto_now_add=True)),
                ('status', models.CharField(choices=[('PROCESSANDO', 'Em Processamento'), ('CONSULTA', 'Em Consulta'), ('CONCLUIDA', 'Concluída'), ('CANCELADA', 'Cancelada')], default='PROCESSANDO', max_length=20)),
                ('doador', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='meuapp.doador')),
                ('orgao', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='meuapp.orgao')),
                ('receptor', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='meuapp.receptor')),
            ],
        ),
    ]
