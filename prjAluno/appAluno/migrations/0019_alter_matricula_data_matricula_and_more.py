# Generated by Django 4.2.3 on 2024-02-09 12:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('appAluno', '0018_alter_matricula_data_matricula_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='matricula',
            name='data_matricula',
            field=models.DateField(),
        ),
        migrations.AlterField(
            model_name='matricula',
            name='data_movimentacao',
            field=models.DateField(),
        ),
    ]
