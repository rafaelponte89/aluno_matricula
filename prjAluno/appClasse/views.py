from django.shortcuts import render
from .models import Classe
from appAluno.models import Aluno
from appMatricula.models import Matricula
from django.shortcuts import HttpResponse
from datetime import datetime
from django.db.models import Q
from utilitarios.utilitarios import criarMensagem, criarMensagemModal
from appMatricula.views import verificar_matricula_ativa_no_ano

# Create your views here.
def classe(request): 
    context = {
        'periodos': Classe.PERIODO_CHOICES
    }   
    return render(request, 'classe.html', context)


def buscar(request):
    classe = request.GET.get('classe')
    classe = Classe.objects.get(pk=classe)
    corpo = ""
    
    selecionado = "" 
    periodos = Classe.retornarPeriodos()
    opcoes_periodo = f"<option {selecionado}> Selecione </option>"
   
    for i in range(len(periodos)):
        sigla, periodo = periodos[i]
        if classe.periodo == sigla:
            selecionado = "selected"
            opcoes_periodo += f"""<option value={sigla} {selecionado}>{periodo}</option>"""
        else:
            selecionado = ""
            opcoes_periodo += f"""<option value='{sigla}' {selecionado}>{periodo}</option>"""
    
    corpo = f"""<form>
                    <input type='hidden' id='codClasse' value={classe.id} />
                    <div class='row'>
                    <div class='col form-group'> 
                    <label for='serieAtualizar'>Série</label>
                    <input id='serieAtualizar' class='form-control' type='number' value={classe.serie} \>
                    </div>            
                     <div class='col form-group'> 
                      <label for='turmaAtualizar'>Turma</label>
                    <input id='turmaAtualizar' class='form-control' type='text' value={classe.turma} \>
                    </div>
                     <div class='col form-group'> 
                      <label for='periodoAtualizar'>Período</label>
                    <select id='periodoAtualizar' class='form-control' >
                     {opcoes_periodo}
                    </select>
                    </div>
                    </div> 
                </form>
                    """
    
    return HttpResponse(corpo)
    

#Gravar classe
def gravar(request):
    try:
        ano = request.GET.get('ano')
        serie = request.GET.get('serie')
        turma = request.GET.get('turma')
        periodo = request.GET.get('periodo')
    
        classe = Classe()
        classe.ano = ano
        classe.serie = serie
        classe.turma = turma.upper()
        classe.periodo = periodo
        classe.save()
    
        return criarMensagem('Classe salva com sucesso!!!', 'success')

    except:
        return criarMensagem('Erro ao gravar!!!', 'danger')
    
#Deletar classe
def deletar(request):
    try:
        classe = request.GET.get("classe")
        classe = Classe.objects.get(pk=classe)
        classe.delete()
        return criarMensagem('Classe deletada com sucesso!!!','warning')
    except Exception as erro:
        return criarMensagem(erro, 'danger')
    
#Atualizar classe
def atualizar(request):

    try:
        classeid = request.GET.get('classe')
        
        classe = Classe.objects.get(pk=classeid)
      
        classe.ano = request.GET.get('ano')
   
        classe.serie = request.GET.get('serie')
        classe.turma = request.GET.get('turma').upper()
        classe.periodo = request.GET.get('periodo')
        print(classeid, classe.ano, classe.serie, classe.turma, classe.periodo)
        classe.save()
        return criarMensagem("Classe Atualizada com Sucesso!!!","success")
    except Exception as e:
        print(e)
        return criarMensagem("Erro ao Atualizar Classe!!!", "danger")


#Construir tabela das classes do ano recebido como parâmetro
def carregarAnoAtual(ano):
    classe = Classe.objects.filter(ano=ano)
    corpo = ''
    
    for c in classe:
        if c.periodo == "M":
            periodo = "MANHÃ"
        else:
            periodo = "TARDE"
        
        corpo += f"""<tr><td class='text-center'>{c.serie}</td><td class='text-center'>{c.turma}</td><td class='text-center'>{periodo}</td> <td class='text-center'>  <button type="button" class="btn btn-outline-dark btn-lg atualizar"
          value={c.id} data-bs-toggle="modal" data-bs-target="#atualizarModal"> 
                            <i class="bi bi-arrow-repeat"></i> 
                        </button> </td>
                        <td class='text-center'>  <button type="button" class="btn btn-outline-dark btn-lg matricular"
                        value={c.id} data-bs-toggle="modal" data-bs-target="#matricularModal" title="Adicionar Matrícula"> 
                            <i class="bi bi-journal-plus"></i> 
                        </button> </td>
                        <td class='text-center'>  <button type="button" class="btn btn-outline-dark btn-lg visualizar"
                        value={c.id} data-bs-toggle="modal" data-bs-target="#visualizarClasseModal"> 
                            <i class="bi bi-eye"></i>
                        </button> </td>
                        </tr>"""
        
    return corpo 
    
 
#Listar classes em HTML   
def listar(request):
    ano = request.GET.get("ano")
    return HttpResponse(carregarAnoAtual(ano))


#Buscar aluno
def buscarAluno(request):
    nome = request.GET.get('nome')   
    # Se status não ativo
    alunos = Aluno.objects.filter(Q(nome__contains=nome))[:5]
    linhas = ''
    for a in alunos:
        linhas += f"""<tr><td>{a.nome}</td><td>{a.ra}</td><td class='text-center'><button type="button" class="btn btn-outline-dark btn-lg adicionarNaClasse"
                        value={a.rm} > 
                        <i class="bi bi-plus-circle-fill"></i>
                        </button></td></tr>"""
    
    return HttpResponse(linhas)    


def matricular_aluno(ano, classe, aluno, numero, data_matricula, data_movimentacao=None, situacao='C'):
    matricula_nova = Matricula(ano=ano, classe=classe, aluno=aluno, 
                                numero=numero,
                                data_matricula=data_matricula, 
                                data_movimentacao=data_movimentacao,
                                situacao=situacao,
                                )

    matricula_nova.save()
    
    
#Adicionar aluno na classe        
def adicionarNaClasse(request):
    try:
         
        aluno = Aluno.objects.get(pk=request.GET.get('aluno'))
        ano = request.GET.get('ano')
        if (verificar_matricula_ativa_no_ano(ano, aluno.rm)):
            classe = Classe.objects.get(pk=request.GET.get('classe'))   
            matricular_aluno(ano, classe, aluno, 
                              Classe.retornarProximoNumeroClasse(Matricula, classe),
                              request.GET.get('data_matricula'))
            
            aluno.status = 2
            aluno.save()
            
            return criarMensagemModal("Matrícula Efetuada", "success")
        else:
            return criarMensagemModal("Com Matrícula Ativa no Ano!!!", "danger")

    except Exception as error:    
        print(error)
        return criarMensagemModal("Erro ao efetuar a Matrícula", "danger")


#Visualizar alunos da classe
def exibirClasses(request):
    codigo_classe = request.GET.get('classe')
    classe = Classe.objects.get(pk=codigo_classe)
    matriculas = Matricula.objects.filter(Q(classe=classe)).order_by('numero')
    linhas = ''
    
    if classe.periodo == "M":
        periodo = "MANHÃ"
    else:
        periodo = "TARDE"
    
    for m in matriculas:
        linhas += f"""<tr><td>{m.numero}</td>  <td>{m.aluno.nome}</td></tr>"""

    tabela = f"""<div class="row mt-3">
      <div class="col-12">
    <h5 class='bg-body-secondary d-flex rounded-5 justify-content-center p-2'><strong>{classe.serie}º{classe.turma} - {periodo} </strong></h5>

    <table id="tabelaAlunos" class="table table-hover table-responsive">
      <thead>
        <th>Nº</th> 
        <th>Nome do Aluno</th>
      </thead>
      <tbody>
        {linhas}
      </tbody>
    </table>
    </div>
    </div>"""
  
    return HttpResponse(tabela)  
    
#Exibir tela da matrícula  
def exibirTelaMatricula(request):
    codigo_classe = request.GET.get("classe")
    classe = Classe.objects.get(pk=codigo_classe)
    
    if classe.periodo == "M":
        periodo = "MANHÃ"
    else:
        periodo = "TARDE"
            
    tela = f"""<form>
                    <h5 class='bg-body-secondary d-flex rounded-5 justify-content-center p-2'><strong>{classe.serie}º{classe.turma} - {periodo} </strong></h5>
                    <input type='hidden' id='codClasseMatricula' value={classe.id} />
                    <div class='row'>
                    <div class='col form-group'>
                    <label for='nomeAluno'>Nome</label>
                    <input id='nomeAluno' class='form-control' type='text'\>
                    </div>   
                    <div class='col-5 form-group'> 
                    <label for='dataMatricula'>Data da Matrícula</label>
                    <input id='dataMatricula' class='form-control' type='date' value='{datetime.now().strftime("%Y-%m-%d")}'\>
                    </div>               
                    </div>
                    <div class='row'>
                    
                    </div>
                    
                    </form>
                    """
   
    return HttpResponse(tela)


def contar(serie,ano,periodo):
    classes = Classe.objects.filter(ano=ano).filter(serie=serie).filter(periodo=periodo)
    
    return len(classes)


def gerarTurmas(request):
    ano = request.GET.get('ano')
    turma = 65
    
    for s in range(1, 10):
        serie_manha = int(request.GET.get('m'+str(s)))
        serie_tarde = int(request.GET.get('t'+str(s)))
        print(serie_manha)
        print(serie_tarde)
        if (serie_manha) > 0:
           
            for i in range(serie_manha):
                classe = Classe()
                classe.ano = ano
                classe.serie = s
                classe.turma = chr(turma)
                classe.periodo = "M"
                classe.save()
                turma += 1
        if (serie_tarde) > 0: 
            for i in range(serie_tarde):
                classe = Classe()
                classe.ano = ano
                classe.serie = s
                classe.turma = chr(turma)
                classe.periodo = "T"
                classe.save()
                turma += 1
        turma = 65
                
    return HttpResponse("Geradas as salas") 


def exibirQuadro(request):
    
    ano = request.GET.get('ano')
    
    classe = Classe.objects.filter(ano=ano)
    if (classe):
        desabilita = 'disabled'
    else:
        desabilita =''
        
    tela = """ <div class="row">
            <div class="col-4 text-center"><strong>Ano</strong></div>
            <div class="col-4 text-center"><strong>Manhã</strong></div>
            <div class="col-4 text-center"><strong>Tarde</strong></div>
          </div>
            """
            
    for i in range(1, 10):
        
        tela += f"""<div
            class="row mt-2 d-flex justify-content-center align-items-center"
          >
            <div class="col-4 text-center  bg-body-secondary p-1 rounded-4"><strong>{i}<span>º</span></strong></div>
            <div class="col-4 text-center">
              <input type="number" class="form-control" value="{contar(i,ano,'M')}" id="m{i}" {desabilita} />
            </div>
            <div class="col-4 text-center">
              <input type="number" class="form-control" value="{contar(i,ano,'T')}" id="t{i}" {desabilita} />
            </div>
          </div>"""
          
    return HttpResponse(tela)
    