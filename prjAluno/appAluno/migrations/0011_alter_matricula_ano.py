# Generated by Django 4.2.3 on 2024-02-02 23:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('appAluno', '0010_matricula_aluno_matricula_ano_matricula_classe_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='matricula',
            name='ano',
            field=models.IntegerField(default=0),
        ),
    ]