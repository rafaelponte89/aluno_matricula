from django.urls import path
from .views import (classe, gravar, atualizar, deletar, listar, 
                    buscar, exibirTelaMatricula, buscarAluno, 
                    adicionarNaClasse, exibirClasses, exibirQuadro, gerarTurmas)

urlpatterns = [
    path('classe', classe, name='classe'),
    path('gravarclasse', gravar, name='gravarclasse'),
    path('atualizarclasse', atualizar, name='atualizarclasse'),
    path('deletarclasse', deletar, name='deletarclasse'),
    path('listarclasse', listar, name='listarclasse'),
    path('buscarclasse', buscar, name='buscarclasse'),
    path('telamatricular', exibirTelaMatricula, name='telamatricular'),
    path('buscarAluno', buscarAluno, name='buscarAluno'),
    path('adicionarNaClasse', adicionarNaClasse, name='adicionarNaClasse'),
    path('exibirClasse', exibirClasses, name='exibirClasse'),
    path('exibirQuadro', exibirQuadro, name='exibirQuadro'),
    
    path('gerarTurmas', gerarTurmas, name='gerarTurmas'),
]