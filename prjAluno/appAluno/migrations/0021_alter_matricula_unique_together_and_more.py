# Generated by Django 4.2.3 on 2024-02-09 12:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('appAluno', '0020_remove_matricula_data_matricula_and_more'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='matricula',
            unique_together=set(),
        ),
        migrations.AddField(
            model_name='matricula',
            name='data_matricula',
            field=models.DateField(null=True),
        ),
        migrations.AddField(
            model_name='matricula',
            name='data_movimentacao',
            field=models.DateField(null=True),
        ),
        migrations.AlterUniqueTogether(
            name='matricula',
            unique_together={('ano', 'aluno', 'situacao', 'data_movimentacao')},
        ),
    ]
