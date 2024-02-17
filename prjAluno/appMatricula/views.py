from django.shortcuts import render
from django.shortcuts import HttpResponse
from appClasse.models import Classe
from appAluno.models import Matricula
from utilitarios.utilitarios import criarMensagem
# Create your views here.


def matricula(request):
    
    return render(request, 'matricula.html')


def adicionar(reqeust):
    pass


def deletar(request):
    pass


def transferir(request):
    try:
        matricula = Matricula.objects.get(pk=request.GET.get('matricula'))
        matricula.situacao = 'T'
        matricula.data_movimentacao = request.GET.get('data_movimentacao')
        matricula.save()
        return criarMensagem("Transferência efetuada!", "success")
    
    except Exception as erro:
        return criarMensagem(f"Erro ao efetuar a Transferência!{erro}", "danger")


def ordernar_alfabetica (request):
    classe = request.GET.getlist('classe')[0]
    linhas = carregar_linhas(classe, 'aluno__nome')
    return HttpResponse(linhas)


def carregar_classes(request):
    ano = request.GET.get('ano')
    classes = Classe.objects.filter(ano=ano)
    opcoes = "<option value=''>Selecione</option>"
                                                 
    for c in classes:
        opcoes += f"<option value={c.id}>{c.serie}º {c.turma} - {c.periodo}"
        
    return HttpResponse(opcoes)


def carregar_linhas(classe, ordem="numero"):
    linhas = ""
    situacao = ""
    matriculas = Matricula.objects.filter(classe=classe).order_by(ordem)
    numero = 0
    
    if ordem == "aluno__nome":
        for m in matriculas:
            numero = numero + 1
            m.numero = numero
            m.save()
            
    for m in matriculas:
        if m.situacao == "C":
            situacao = "CURSANDO"
            cor = "text-primary"
        elif m.situacao == "T":
            situacao = "TRANSFERIDO"
            cor = "text-danger"
        elif m.situacao == "M":
            situacao = "REMANEJADO"
        elif m.situacao == "P":
            situacao = "PROMOVIDO"
        elif m.situacao == "R":
            situacao = "REPROVADO"
        else:
            situacao = "ARQUIVADO"
            
        linhas += f"""<tr> <td>{m.numero} </td> <td >{m.aluno.nome}</td> <td class={cor}> {situacao} </td> 
        <td> <button type='button' class='btn btn-outline-dark btn-lg transferir'
          value={m.id} data-bs-toggle='modal' data-bs-target='#transferirModal'> 
                           <i class="bi bi-arrow-down"></i> 
                        </button><td> </tr>"""
        
    return linhas


def buscar_matricula(request):
    matricula = request.GET.get('matricula')
    matricula = Matricula.objects.get(pk=matricula)
    corpo = ""
    
    corpo = f"""<form>
                    <input type='hidden' id='matricula' value={matricula.id} />
                    <div class='row'>
                    <div class='col form-group'>
                    <label for='rmAluno'>RM</label>
                    <input id='rmAluno' class='form-control' type='text' value='{matricula.aluno.rm}' disabled='disabled'\>
                    </div>
                    </div>
                    
                    <div class='row'>
                    <div class='col form-group'> 
                    <label for='nomeAluno'>Aluno</label>
                    <input id='nomeAluno' class='form-control' type='text' value='{matricula.aluno.nome}' disabled='disabled'\>
                    </div>
                    </div>
                    
                    <div class='row>
                    <div class='col form-group'> 
                    <label for='dataMovimentacao'>Data Movimentação</label>
                    <input id='dataMovimentacao' class='form-control' type='date' value='{matricula.data_movimentacao}' \>
                    </div>
                              
        
                    
                    </div>
                    
                    </form>
                    """
    
    return HttpResponse(corpo)
    
    
def carregar_matriculas(request):
    classe = request.GET.getlist('classe')[0]
    linhas = carregar_linhas(classe, 'numero')
    
    return HttpResponse(linhas)
    