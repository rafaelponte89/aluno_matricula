from django.shortcuts import render
from appClasse.models import Classe
from appMatricula.models import Matricula
from django.http import JsonResponse, HttpResponse

# Create your views here.

def dashboard(request):
   

    return render(request, 'dashboard.html',)


def visualizar_alunos_periodo(request):

    ano = request.GET.get('ano')

    manha =  Matricula.objects.filter(classe__periodo='M').filter(situacao='C').filter(ano=ano).count()
    tarde =  Matricula.objects.filter(classe__periodo='T').filter(situacao='C').filter(ano=ano).count()
    print(manha, tarde)
    print('executon')
    dados = {
        'manha': manha,
        'tarde': tarde
    }

    return JsonResponse(dados, safe=False)

def visualizar_alunos_mes(request):

    ano = request.GET.get('ano')
    dados = {
        'Janeiro': 0,
        'Fevereiro': 0,
        'Março': 0,
        'Abril': 0,
        'Maio': 0,
        'Junho': 0,
        'Julho': 0,
        'Agosto': 0,
        'Setembro': 0,
        'Outubro': 0,
        'Novembro': 0,
        'Dezembro': 0
    }
    mes = 0
    for k,v in dados.items():
        mes += 1
        dados[k] =  (Matricula.objects.filter(situacao='C').filter(ano=ano).filter(data_matricula__month__lte=mes).count())

    
    return JsonResponse(dados, safe=False)
    





