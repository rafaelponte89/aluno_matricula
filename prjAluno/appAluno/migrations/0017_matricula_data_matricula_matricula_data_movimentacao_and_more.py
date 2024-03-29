# Generated by Django 4.2.3 on 2024-02-09 12:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('appAluno', '0016_alter_aluno_rm'),
    ]

    operations = [
        migrations.AddField(
            model_name='matricula',
            name='data_matricula',
            field=models.DateField(default='1970-01-01'),
        ),
        migrations.AddField(
            model_name='matricula',
            name='data_movimentacao',
            field=models.DateField(default='1970-01-01'),
        ),
        migrations.AlterField(
            model_name='aluno',
            name='ra',
            field=models.CharField(default='', max_length=100),
        ),
        migrations.AlterField(
            model_name='matricula',
            name='situacao',
            field=models.CharField(choices=[('C', 'CURSANDO'), ('T', 'TRANSFERIDO'), ('M', 'REMANEJADO'), ('P', 'PROMOVIDO'), ('R', 'REPROVADO'), ('A', 'ARQUIVADA')], default='A', max_length=1),
        ),
    ]
