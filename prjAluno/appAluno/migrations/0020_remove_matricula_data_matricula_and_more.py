# Generated by Django 4.2.3 on 2024-02-09 12:13

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('appAluno', '0019_alter_matricula_data_matricula_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='matricula',
            name='data_matricula',
        ),
        migrations.RemoveField(
            model_name='matricula',
            name='data_movimentacao',
        ),
    ]
