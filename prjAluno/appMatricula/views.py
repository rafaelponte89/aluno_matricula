from django.shortcuts import render
from django.shortcuts import HttpResponse
from appClasse.models import Classe
from appAluno.models import Aluno
from .models import Matricula
from django.db.models import Q
from utilitarios.utilitarios import criarMensagem
from datetime import datetime
# Create your views here.


def matricula(request):
    
    return render(request, 'matricula.html')


def adicionar(reqeust):
    pass


def deletar(request):
    pass


def movimentar(request):
    
    try:
        matricula = Matricula.objects.get(pk=request.GET.get('matricula'))
        classe = (Classe.objects.get(pk=request.GET.getlist('classe_remanejamento')[0]) if (request.GET.getlist('classe_remanejamento')[0]) != '0' else None)
        movimentacao = request.GET.getlist('movimentacao')[0]
        data_movimentacao = request.GET.get('data_movimentacao')
        matricula.ano = request.GET.get('ano')
        matricula.situacao = movimentacao
        matricula.data_movimentacao = data_movimentacao
        matricula.save()
        
        if(movimentacao == "REMA"):
            if (verificar_matricula_ativa_no_ano(matricula.ano, matricula.aluno.rm)):
                matricula_nova = Matricula()
                matricula_nova.classe = classe
                matricula_nova.aluno = matricula.aluno
                matricula_nova.numero = Classe.retornarProximoNumeroClasse(Matricula, classe)
                matricula_nova.situacao = 'C'
                matricula_nova.ano = request.GET.get('ano')
                matricula_nova.classe = classe
                matricula_nova.data_matricula = data_movimentacao
                matricula_nova.save()
                return criarMensagem("Remanejamento efetuado!", "success")
            else:
                return criarMensagem("Aluno com matrícula ativa no Ano!!!","danger")
        elif (movimentacao == "BXTR"):
           
           
            return criarMensagem("Transferência efetuada!", "success")
        else:
             return criarMensagem("Movimentação efetuada!", "success")

        
    except Exception as erro:
        print(erro)
        return criarMensagem(f"Erro ao efetuar o Remanejamento!{erro}",
                             "danger")
        
        
def transferir(request):
    try:
        matricula = Matricula.objects.get(pk=request.GET.get('matricula'))
        matricula.ano = request.GET.get('ano')
        matricula.situacao = 'BXTR'
        matricula.data_movimentacao = request.GET.get('data_movimentacao')
        matricula.save()
        return criarMensagem("Transferência efetuada!", "success")
    
    except Exception as erro:
        return criarMensagem(f"Erro ao efetuar a Transferência!{erro}",
                             "danger")


def ordernar_alfabetica(request):
    classe = request.GET.getlist('classe')[0]
    linhas = carregar_linhas(classe, 'aluno__nome')
    return HttpResponse(linhas)

####
def carregar_movimentacao(request):
   
    movimentacoes = Matricula.retornarSituacao()
    opcoes = "<option value='0'>Selecione</option>"
                                            
    for m in movimentacoes:
     
        if m[0] == "BXTR":
            situacao = "TRANSFERIDO"
            cor = "text-danger"
        elif m[0] == "REMA":
            situacao = "REMANEJADO"
            cor = "text-success"
        elif m[0] == "NCFP":
            cor = "text-danger"
            situacao = "Ñ COMP. FORA PRAZO"
            
        if m[0] not in ['C','P','R']:
            opcoes += f"<option value={m[0]}>{situacao} </option>"
        
    return HttpResponse(opcoes)
#####


def carregar_classes_remanejamento(request):
    ano = request.GET.get('ano')
     
    classe_atual = Classe.objects.get(pk=request.GET.get('serie'))
    classes = Classe.objects.filter(ano=ano, serie=classe_atual.serie)
    classes = classes.exclude(pk=request.GET.get('serie'))
    opcoes = "<option value='0'>Selecione</option>"
                                            
    for c in classes:
        if c.periodo == "M":
            periodo = "MANHÃ"
        else:
            periodo = "TARDE"
        opcoes += f"<option value={c.id}>{c.serie}º {c.turma} - {periodo}</option>"
        
    return HttpResponse(opcoes)

def carregar_classes(request):
    ano = request.GET.get('ano')
    classes = Classe.objects.filter(ano=ano)
    opcoes = "<option value='0'>Selecione</option>"
                                            
    for c in classes:
        if c.periodo == "M":
            periodo = "MANHÃ"
        else:
            periodo = "TARDE"
        opcoes += f"<option value={c.id}>{c.serie}º {c.turma} - {periodo}</option>"
        
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
    cor = "text-dark"        
    for m in matriculas:
        if m.situacao == "C":
            situacao = "CURSANDO"
            cor = "text-primary"
        elif m.situacao == "BXTR":
            situacao = "TRANSFERIDO"
            cor = "text-danger"
        elif m.situacao == "REMA":
            situacao = "REMANEJADO"
            cor = "text-success"
        elif m.situacao == "P":
            situacao = "PROMOVIDO"
        elif m.situacao == "R":
            situacao = "REPROVADO"
        elif m.situacao == "NCFP":
            cor = "text-danger"
            situacao = "Ñ COMP. FORA PRAZO"
        else:
            situacao = "ARQUIVADO"
        if m.data_movimentacao is None:
            m.data_movimentacao = ''
        linhas += f"""<tr> <td class='text-center'><button class='rounded-circle bg-light text-dark border-success'>{m.numero} </button></td> <td >{m.aluno.nome}</td> <td class={cor}> {situacao} </td> 
                            <td  class='text-center'> {m.data_matricula} </td> 
                            <td  class='text-center text-danger'> {m.data_movimentacao} </td>
                        <td class='text-center'> <button type='button' class='btn btn-outline-dark btn-lg movimentar'
          value={m.id} data-bs-toggle='modal' data-bs-target='#movimentarModal'> 
                           <i class="bi bi-arrow-down-up"></i>
                        </button></td>
                                     <td class='text-center'> <button type='button' class='btn btn-outline-dark btn-lg excluir'
          value={m.id} > 
                          <i class="bi bi-trash3-fill"></i>
                        </button></td></tr>"""
        
    return linhas


def excluir_matricula(request):
    try:
        matricula = request.GET.get('matricula')
        matricula = Matricula.objects.get(pk=matricula)
        matricula.delete()
        return criarMensagem("Matrícula excluída com sucesso!", "success")
    
    except Exception as e:
        return criarMensagem(f"Matrícula não excluída!!!{e}", "warning")
    
    
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


# Verificar se existe matrícula ativa no ano, se não possuir pode matricular
# Se possuir não pode
def verificar_matricula_ativa_no_ano(ano, rm, situacao='C'):
    try:
        matriculas = Matricula.objects.filter(Q(ano=ano) & Q(aluno_id=rm) & Q(situacao=situacao))  
        if len(matriculas) == 0:
            print('sem matricula') 
            return True
        else:
            print('com matricula')
            return False
        
    except Exception as e:
        print(e)
        
        
# EM DESENVOLVIMENTO 26/02/2024
# modulo que efetuará todas as matrículas através de uma arquivo csv do próprio SED
def upload_matriculas(request):
    try:
        matriculas = request.GET.get('matriculas')
        cod_byte = matriculas.encode('utf-8')
        cod_str = cod_byte.decode('utf-8')
        linhas = cod_str.split('\n')
        linhas_array = []
        classe = int(request.GET.get('classe'))
        classe = Classe.objects.get(pk=classe)
        ano = request.GET.get('ano')
       
        data_matricula = request.GET.get('data_matricula')
        
        matriculas = Matricula.objects.filter(classe=classe)
        
        for matricula in matriculas:
            matricula.delete()
       
        for linha in range(3, len(linhas)):
            linhas_array.append(linhas[linha].split(';'))
    
        for linha in range(len(linhas_array)-1):  
            ra = int(linhas_array[linha][4])  
            situacao = ('C' if (len(linhas_array[linha][8]) == 0)
                        else linhas_array[linha][8])
            
            data_movimentacao = (None if(len(linhas_array[linha][9]) == 0) else 
                                 datetime.strptime(linhas_array[linha][9],"%d/%m/%Y"))
            print(data_movimentacao)
   
            rm = Aluno.objects.filter(ra=ra).values('rm')[:1]

            for cod in rm:
                aluno = Aluno.objects.get(pk=cod['rm'])
                
                if (verificar_matricula_ativa_no_ano(ano, aluno.rm)):
                    numero = Classe.retornarProximoNumeroClasse(Matricula, classe)
                    print("Situação",situacao)
                    print("Data Movimentacao",data_movimentacao)
                    print("data Matricula", data_matricula)
                    matricula = Matricula(ano=ano, classe=classe, aluno=aluno, 
                                    situacao=situacao, 
                                    data_matricula=data_matricula, numero=numero, data_movimentacao=data_movimentacao)
            
                    matricula.save()                
                
        return HttpResponse(carregar_linhas(classe))
    
    except Exception as e:
        return HttpResponse(carregar_linhas(0))
        