from django.shortcuts import render, HttpResponse
from .models import Ano
from appMatricula.models import Matricula
from utilitarios.utilitarios import criarMensagem

# Create your views here.
def inicial_ano(request):
    return render(request,"ano.html")


def gravar_ano(request):
    ano = Ano(ano=request.GET.get('ano'))
    try:
        ano.save()
        return criarMensagem("Ano salvo com sucesso","success")
    except Exception as err:
        return criarMensagem(f"Erro ao salvar ano {err}", "danger")


def excluir_ano(request):
    ano = Ano.objects.filter(pk=request.GET.get('ano'))[0]
    try:
        ano.delete()
        return criarMensagem("Ano deletado com sucesso", "success")
    except:
        return criarMensagem(f"Erro ao excluir ano {ano}","danger")


def buscar_ano(request):
    try:
        ano = Ano.objects.filter(ano=request.GET.get("ano"))[0]
        return HttpResponse(f"""<tr><td class='text-center'> <button type='button' class='btn btn-outline-dark btn-lg selecionarAno'
          value={ano.ano} > {ano.ano} </button></td>
        <td class='text-center'> <button type='button' class='btn btn-outline-dark btn-lg excluir'
          value={ano.id} > 
                          <i class="bi bi-trash3-fill"></i>
                        </button></td>
        <td class='text-center'><button type='button' class='btn btn-outline-dark btn-lg status'
          value={ano.id} > 
                          {retornarStatusAno(ano.id)}
                        </button></td></td>
        </tr>""")
    except:
        return criarMensagem("Nenhum resultado!","info")
    

def listar_ano(request):
    anos = Ano.objects.all()[:10]
    linhas = ''
    for a in anos:
        linhas += f"""<tr><td class='text-center'><button type='button' class='btn btn-outline-dark btn-lg selecionarAno'
          value={a.ano} > {a.ano} </button></td>
        <td class='text-center'> <button type='button' class='btn btn-outline-dark btn-lg excluir'
          value={a.id}> 
                          <i class="bi bi-trash3-fill"></i>
                        </button></td>
        <td class='text-center'><button type='button' class='btn btn-outline-dark btn-lg status'
          value={a.id}> 
                          {retornarStatusAno(a.id)}
                        </button></td></td>
        </tr>"""
    
    return HttpResponse(linhas) 
    

def retornarStatusAno(ano):
    ano = Ano.objects.get(pk=ano)
    if ano.fechado:
        return '<i class="bi bi-lock-fill"></i>'
    else:
        return '<i class="bi bi-unlock-fill"></i>'


def fechar_abrir_ano(request):
    ano = Ano.objects.get(pk=request.GET.get('ano'))
    matriculas = Matricula.objects.filter(ano=ano)

    ano.fechado = not ano.fechado
    ano.save()
    for matricula in matriculas:
        if ano.fechado and matricula.situacao == 'C':
            matricula.situacao = 'P'
        else:
            if matricula.situacao == 'P':
                matricula.situacao = 'C'
        
        matricula.save()

    return HttpResponse(ano.fechado)
    

def status_ano(request):
    ano = Ano.objects.get(pk=request.GET.get('ano'))
    return HttpResponse(ano.fechado)


def selecionar_ano(request):
    ano = Ano.objects.filter(ano=request.GET.get('ano'))[0]
    return HttpResponse(ano.id)
   



