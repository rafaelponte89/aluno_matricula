from django.shortcuts import render
from appClasse.models import Classe
from appAno.models import Ano
from appMatricula.models import Matricula
from django.http import JsonResponse, HttpResponse

# Create your views here.

def dashboard(request):
   

    return render(request, 'dashboard.html',)


def visualizar_alunos_periodo(request):

    ano = Ano.objects.get(pk=request.GET.get('ano'))

    manha =  Matricula.objects.filter(classe__periodo='M').filter(situacao='C').filter(ano=ano).count()
    tarde =  Matricula.objects.filter(classe__periodo='T').filter(situacao='C').filter(ano=ano).count()
    integral =  Matricula.objects.filter(classe__periodo='I').filter(situacao='C').filter(ano=ano).count()

    print(manha, tarde)
    print('executon')
    dados = {
        'Manhã': manha,
        'Tarde': tarde,
        'Integral': integral

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
        dados[k] =  (Matricula.objects.exclude(situacao='REMA').filter(ano=ano).filter(data_matricula__month__lte=mes).count()
        -Matricula.objects.filter(situacao='BXTR').filter(ano=ano).filter(data_movimentacao__month__lte=mes).count()
        -Matricula.objects.filter(situacao='NFCP').filter(ano=ano).filter(data_movimentacao__month__lte=mes).count())
    print(dados)
    return JsonResponse(dados, safe=False)
    





