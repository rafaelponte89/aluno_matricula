from django.urls import path
from .views import (adicionar, transferir, deletar, matricula, 
                    ordernar_alfabetica, carregar_classes, carregar_matriculas, buscar_matricula)

urlpatterns = [
    path('matricula', matricula, name='matricula'),
    path('adicionar', adicionar, name='adicionar'),
    path('transferir', transferir, name='transferir'),
    path('deletar', deletar, name='deletar'),
    path('ordenarAlfabeto', ordernar_alfabetica, name='ordemalfabetica'),
    path('carregarClasses', carregar_classes, name='carregarclasses'),
    path('carregarMatriculas', carregar_matriculas, name='carregarmatriculas'),
    path('buscarMatricula', buscar_matricula, name='buscarmatricula'),
]