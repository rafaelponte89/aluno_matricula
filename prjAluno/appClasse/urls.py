from django.urls import path
from .views import (classe, gravar, atualizar, deletar, listar, 
                    buscar, exibirTelaMatricula, buscarAluno, 
                    adicionarNaClasse, exibirTurma)

urlpatterns = [
    path('classe', classe, name='classe'),
    path('classe/gravar', gravar, name='gravarclasse'),
    path('classe/atualizar', atualizar, name='atualizarclasse'),
    path('classe/deletar', deletar, name='deletarclasse'),
    path('classe/listar', listar, name='listarclasse'),
    path('classe/buscar/', buscar, name='buscarclasse'),
    path('classe/matriculas', exibirTelaMatricula, name='telamatricular'),
    path('classe/buscarAluno', buscarAluno, name='buscarAluno'),
    path('classe/adicionarNaClasse', adicionarNaClasse, name='adicionarNaClasse'),
    path('classe/exibirTurma', exibirTurma, name='exibirTurma')
]