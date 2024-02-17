from django.shortcuts import render, redirect
from .models import Aluno, Telefone, Matricula
from .models import Classe
from .forms import frmAluno
from django.contrib import messages
from django.http import HttpResponse
from django.db.models import Q
from django.views.decorators.csrf import csrf_exempt
from utilitarios.utilitarios import criarMensagem, padronizar_nome, realizar_backup_v2
import time
import io
from pathlib import Path
from os import path
import os.path
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib.styles import getSampleStyleSheet
from datetime import datetime
import os
from datetime import datetime
import csv
from .automatization import login_sed_2, acessar_caminho, buscar_dados

REF_TAMANHO_NOME = 2
REF_TAMANHO_RA = 7


def buscar_duplicados(alunos):
   
    nomes_rm = {}
    duplicados = {}
    for aluno in alunos:
        nome = aluno.nome.rstrip().lstrip().upper()
       
        if aluno.status != 1:
            if nome not in nomes_rm.keys():
                nomes_rm[nome] = [aluno.rm]
            else:
                nomes_rm[nome].append(aluno.rm)
   
    for k, v in nomes_rm.items():
        if len(v) > 1:
            duplicados[k] = v
            
    return duplicados.keys()
    
    
# Gravar registro do Aluno
def gravar(request):
    nome = padronizar_nome(request.POST.get("nome"))
    ra = request.POST.get("ra")
    tamanho_nome = len(nome)
    tamanho_ra = len(ra)
    
    try:
        
        is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
        if is_ajax:
            if request.method == 'POST':
                form = frmAluno({"nome": nome, "ra": ra})
                if form.is_valid():
                    if (tamanho_nome > REF_TAMANHO_NOME):
                        if (tamanho_ra > REF_TAMANHO_RA): 
                         
                            print('formulario',form["nome"])
                            form.save() 
      
                            mensagem = criarMensagem("Aluno Registrado com Sucesso!","success")
                        else:
                            mensagem = criarMensagem("RA muito Pequeno","warning")
                        
                    else:
                        mensagem = criarMensagem("Nome muito Pequeno!","warning")
                else:
                    if tamanho_nome == 0: 
                        mensagem = criarMensagem("Nome em Branco!!","warning")
                    elif tamanho_ra == 0: 
                        mensagem = criarMensagem("RA em Branco!!","warning")
   
                return mensagem
                                         
    except Exception as err:
        print(err)


def retornar_numeros_telefones(aluno):
    telefones = Telefone.objects.filter(aluno=aluno)
    texto_numeros = ""
    
    for tel in telefones:
        texto_numeros += "<span class='m-1'>" + tel.numero + "</span>"
    
    return texto_numeros
    

def atualizarTabela(alunos):
    nomes_duplicados = buscar_duplicados(alunos)
    tabela = ''
    print("Duplicados", nomes_duplicados)
    
    for aluno in alunos:
        nome = aluno.nome.rstrip().lstrip().upper()
        if aluno.status == 1:
            status_rm = '<td class="align-middle">' + str(aluno.rm) + '</td>'
            
            botao = '<button type="button" class="btn btn-outline-danger btn-lg  disabled" aria-label="cancelar'+str(aluno.nome)+  '" value="'+str(aluno.rm)+'"> \
                            <i class="bi bi-x-circle-fill"></i> \
                        </button>' 
        else:
            if nome in nomes_duplicados:
                status_rm = '<td class="align-middle">' + str(aluno.rm) + \
                '<button "type="button" class="btn btn-outline-primary m-2 advertencia" value='+str(aluno.rm)+' data-bs-toggle="modal" data-bs-target="#resolucaoDuplicidadeModal" ><i class="bi bi-person-fill-exclamation"></i></button></a></td>'
                botao = '<button type="button" class="btn btn-outline-dark btn-lg atualizar"  value='+str(aluno.rm)+' data-bs-toggle="modal" data-bs-target="#atualizarModal"> \
                            <i class="bi bi-arrow-repeat"></i> \
                        </button>'
            else:
                status_rm = '<td class="align-middle">' + str(aluno.rm) + '</td>'
                botao = '<button type="button" class="btn btn-outline-dark btn-lg atualizar" aria-label="atualizar'+str(aluno.nome)+'"  value="'+str(aluno.rm)+'" data-bs-toggle="modal" data-bs-target="#atualizarModal"> \
                            <i class="bi bi-arrow-repeat"></i> \
                        </button>'
                
                             
            
        tabela += f"""<tr> {status_rm}
                    <td class="align-middle">{aluno.nome}</td> 
                       
                        <td class="align-middle text-center">{retornar_numeros_telefones(aluno)}</td> 
                        <td class="align-middle text-center">{aluno.ra} </td> 
                        
                        <td class="align-middle text-center conteudoAtualizar">
                            {botao} 
                        </td>
                    </tr>"""    
                    
    #print("Atualizar Tabela", tabela)
    return HttpResponse(tabela)
  



def cancelarRM(request):
    rm_req = int(request.POST.get('rm'))
    aluno = Aluno.objects.get(pk=rm_req)
    aluno.status = 1
    aluno.save()
    return criarMensagem(f"{aluno.nome} - {aluno.rm} : Cancelado!!!","success")


# reset na tabela 
def recarregarTabela(request):
    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
   
    alunos = Aluno.retornarNUltimos()
    tabela = atualizarTabela(alunos)
    return tabela


def buscar(request):
    nome = padronizar_nome(request.POST.get("nome").upper().rstrip().lstrip())
    tamanho = len(nome)
    if (tamanho > REF_TAMANHO_NOME) :
        alunos = Aluno.objects.filter(nome__contains=nome)[:10]
        buscar_duplicados(alunos)
        tabela = atualizarTabela(alunos)
        
        if len(tabela.content)>0:
           
            return tabela
        else:
            mensagem = criarMensagem("Aluno Não Encontrado", "info")
            
            return mensagem
    else:
        return recarregarTabela(request)


def retornar_classes(request):
    
    ano = request.GET.get('ano')
    classes = Classe.objects.filter(ano=ano)
    opcoes = ""
    for i in classes:
        if i.periodo == "M":
            periodo = "MANHÃ"
        else:
            periodo = "TARDE"
        opcoes += f"<option value={i.id}>{i.serie}º{i.turma} {periodo}</option>"
    opcoes = f"<select class='form-select m-3 classes' aria-label='Default select example'> \
                    {opcoes}\
                  </select>"
    return HttpResponse(opcoes)


def retornar_status(codigo):
    if codigo == 0:
        return 'Ativo'
    elif codigo == 1:
        return 'Cancelado'
    else:
        return 'Arquivado'
    
    
# versao 2 (em desenvolvimento)
def buscar_dados_aluno(request):
    rm = request.POST.get('rm')
    print("RM", rm)
    aluno = Aluno.objects.get(pk=rm)

    telefones = Telefone.retornarListaTelefones()
    matriculas = Matricula.retornarSituacao()
    telefones_aluno = Telefone.objects.filter(aluno=aluno)
    matriculas_aluno = Matricula.objects.filter(aluno=aluno)
    selecionado = ""    
    
    def retornar_telefone( telefones_aluno):  
        selecionado_tel = ""     
        opcoes_telefone = f"<option {selecionado}> Selecione </option>"
        for i in range(len(telefones)):
            sigla, contato = telefones[i]
            if telefones_aluno.contato == sigla:
                selecionado_tel = "selected"
                opcoes_telefone += f"""<option value={sigla} {selecionado_tel}>{contato}</option>"""
            else:
                selecionado_tel = ""
                opcoes_telefone += f"""<option value='{sigla}' {selecionado_tel}>{contato}</option>"""
        return opcoes_telefone
    
    def retornar_matricula(matriculas_aluno):  
        selecionado_matricula = ""     
        opcoes_matricula = f"<option {selecionado}> Selecione </option>"
        for i in range(len(matriculas)):
            sigla, situacao = matriculas[i]
            if matriculas_aluno.situacao == sigla:
                selecionado_matricula = "selected"
                opcoes_matricula += f"""<option value={sigla} {selecionado_matricula}>{situacao}</option>"""
            else:
                selecionado_matricula = ""
                opcoes_matricula += f"""<option value='{sigla}' {selecionado_matricula}>{situacao}</option>"""
        return opcoes_matricula
    
    dados_telefone = "" 
    for i in range(len(telefones_aluno)):  
        dados_telefone += f"""
                   <div class="col-12 form-group d-flex align-items-center"> 
                  <input        
                    type="number"     
                    class="form-control numTelefone p-2" 
                    id="telefoneAtualizar" 
                    aria-describedby="emailHelp" 
                    placeholder="Telefone" 
                    value="{telefones_aluno[i].numero}"
                  /> 
                      <select class="form-select m-3 contato" aria-label="Default select example" id=periodoAtualizar> 
                        {retornar_telefone(telefones_aluno[i])}
                    </select> 
                   <button type="button" class="btn btn-danger m-1 removerTelefone" value="{telefones_aluno[i].id}"><i class="bi bi-telephone-minus"></i></button> 
                </div>"""
    dados_matricula = ""
    for i in range(len(matriculas_aluno)):  
        dados_matricula += f"""
                   <div class="col-12 form-group d-flex align-items-center"> 
                  <input        
                    type="number"     
                    class="form-control numTelefone p-2" 
                    id="telefoneAtualizar" 
                    aria-describedby="emailHelp" 
                    placeholder="Ano" 
                    value="{matriculas_aluno[i].ano}"
                  /> 
                      <select class="form-select m-3 contato" aria-label="Default select example" id=periodoAtualizar> 
                        {retornar_matricula(matriculas_aluno[i])}
                    </select> 
                   <button type="button" class="btn btn-danger m-1 removerTelefone" value="{matriculas_aluno[i].id}"><i class="bi bi-journal-minus"></i></button> 
                </div>"""
        
    dados = f"""<form id="cadastroAluno"> 
            <div class="row">
            <div class="form-group col-3">
             <label for="rmAtualizar">RM</label>
              <input
                type="number"
                class="form-control disabled"
                id="rmAtualizar"
                aria-describedby="emailHelp"
                placeholder="RM"
                disabled
                value = "{aluno.rm}"
              />
            </div>
            
            <div class="form-group col-9">
              <label for="nascimentoAtualizar">Data de Nascimento:</label>
              <input
                type="date"
                class="form-control"
                id="nascimentoAtualizar"
                aria-describedby="emailHelp"
                placeholder="Data de Nascimento"
                value = "{aluno.data_nascimento}"
              />
            </div>
            
            </div>
            <div class="row>
            <div class="form-group col-12">
              <label for="nomeAtualizar">Nome</label>
              <input
                type="text"
                class="form-control"
                id="nomeAtualizar"
                aria-describedby="emailHelp"
                placeholder="Nome"
                value = "{aluno.nome}"
              />
              
            </div>
            </div>
            <div class="row">
              <div class="col form-group">
                <label for="raAtualizar">Registro do Aluno (SED)</label>
                <input
                  type="number"
                  class="form-control"
                  id="raAtualizar"
                  aria-describedby="emailHelp"
                  placeholder="RA"
                  value = "{aluno.ra}"
                />
              </div>
              <div class="col-4 form-group">
                <label for="raDigitoAtualizar">Digito RA (SED)</label>
                <input
                  type="text"
                  class="form-control"
                  id="raDigitoAtualizar"
                  aria-describedby="emailHelp"
                  placeholder="RA Digito"
                  maxlength = "1"
                  value = "{aluno.d_ra}"
                />
              </div>
            </div>
            

            <div class="row mb-2" id="matriculas">
                   {dados_matricula}
            </div>
             <div class="row">
               <div class="col-1 form-group d-flex">
                  <button id="addTelefone" type="button" class="btn btn-primary mt-3"><i class="bi bi-telephone-plus"></i></button>
                </div>
            </div>
            <div class="row mb-2" id="telefones">
                   {dados_telefone}
            </div>
             
               <div class="modal-footer">
        <button type="button" class="btn btn-danger" data-bs-dismiss="modal">
          Cancelar
        </button>
         <button
              id="simAtualizar"
              type="button"
              class="btn btn-primary"
              data-bs-dismiss="modal"
              value={aluno.rm}
            >
              Atualizar
            </button>
      </div>
          """ 
    return HttpResponse(dados)


#versao 1
def buscar_dados_aluno_2(request):
    rm = request.POST.get('rm')
    print("RM", rm)
    aluno = Aluno.objects.get(pk=rm)
    #telefone = Telefone()
  
    periodos = Aluno.retornarPeriodos()
    telefones = Telefone.retornarListaTelefones()
    telefones_aluno = Telefone.objects.filter(aluno=aluno)
    selecionado = "" 
   
    opcoes_periodo = f"<option {selecionado}> Selecione </option>"
   
    print("Telefones",telefones_aluno)
    for i in range(len(periodos)):
        sigla, periodo = periodos[i]
        if aluno.periodo == sigla:
            selecionado = "selected"
            opcoes_periodo += f"""<option value={sigla} {selecionado}>{periodo}</option>"""
        else:
            selecionado = ""
            opcoes_periodo += f"""<option value='{sigla}' {selecionado}>{periodo}</option>"""
    
    def retornar_telefone( telefones_aluno):  
        selecionado_tel = ""     
        opcoes_telefone = f"<option {selecionado}> Selecione </option>"
        for i in range(len(telefones)):
            sigla, contato = telefones[i]
            if telefones_aluno.contato == sigla:
                selecionado_tel = "selected"
                opcoes_telefone += f"""<option value={sigla} {selecionado_tel}>{contato}</option>"""
            else:
                selecionado_tel = ""
                opcoes_telefone += f"""<option value='{sigla}' {selecionado_tel}>{contato}</option>"""
        return opcoes_telefone
    
    dados_telefone = "" 
    for i in range(len(telefones_aluno)):  
        dados_telefone += f"""
                   <div class="col-12 form-group d-flex align-items-center"> 
                  <input        
                    type="number"     
                    class="form-control numTelefone p-2" 
                    id="telefoneAtualizar" 
                    aria-describedby="emailHelp" 
                    placeholder="Telefone" 
                    value="{telefones_aluno[i].numero}"
                  /> 
                      <select class="form-select m-3 contato" aria-label="Default select example" id=periodoAtualizar> 
                        {retornar_telefone(telefones_aluno[i])}
                    </select> 
                   <button type="button" class="btn btn-danger m-1 removerTelefone" value="{telefones_aluno[i].id}"><i class="bi bi-telephone-minus"></i></button> 
                </div>"""
        
    dados = f"""<form id="cadastroAluno"> 
            <div class="form-group">
              <label for="nomeAtualizar">Nome</label>
              <input
                type="text"
                class="form-control"
                id="nomeAtualizar"
                aria-describedby="emailHelp"
                placeholder="Nome"
                value = "{aluno.nome}"
              />
            </div>
            <div class="row">
              <div class="col form-group">
                <label for="raAtualizar">Registro do Aluno (SED)</label>
                <input
                  type="number"
                  class="form-control"
                  id="raAtualizar"
                  aria-describedby="emailHelp"
                  placeholder="RA"
                  value = "{aluno.ra}"
                />
              </div>
              <div class="col-3 form-group">
                <label for="raDigitoAtualizar">Digito RA (SED)</label>
                <input
                  type="text"
                  class="form-control"
                  id="raDigitoAtualizar"
                  aria-describedby="emailHelp"
                  placeholder="RA Digito"
                  maxlength = "1"
                  value = "{aluno.d_ra}"
                />
              </div>
            </div>
            <div class="form-group">
              <label for="nascimentoAtualizar">Data de Nascimento:</label>
              <input
                type="date"
                class="form-control"
                id="nascimentoAtualizar"
                aria-describedby="emailHelp"
                placeholder="Data de Nascimento"
                value = "{aluno.data_nascimento}"
              />
            </div>
            <div class="row">
               <div class="col-1 form-group d-flex">
                  <button id="addTelefone" type="button" class="btn btn-primary mt-3"><i class="bi bi-telephone-plus"></i></button>
                </div>
            </div>
            <div class="row mb-2" id="telefones">
                   {dados_telefone}
            </div>
             
               <div class="modal-footer">
        <button type="button" class="btn btn-danger" data-bs-dismiss="modal">
          Cancelar
        </button>
         <button
              id="simAtualizar"
              type="button"
              class="btn btn-primary"
              data-bs-dismiss="modal"
              value={aluno.rm}
            >
              Atualizar
            </button>
      </div>
           
          """ 
    return HttpResponse(dados)  
  

def buscarRMCancelar(request):
    rm = request.POST.get('rm')
    print("RM", rm)
    aluno = Aluno.objects.get(pk=rm)
    dados = f'<div class="col-12"> <p class="text-white bg-dark" > RM: <span id="registroAluno">{aluno.rm} </span> </p> <p class="text-white bg-dark"> Nome: {aluno.nome} </p>  </div>'
    return HttpResponse(dados)

def del_telefone(request):
    id_tel = request.POST.get('id_tel')
    telefone = Telefone.objects.get(pk=id_tel)
    telefone.delete()
    
    return HttpResponse("Telefone Excluido")
    
# busca aluno por rm
@csrf_exempt
def buscarRM(request):
    rm = request.POST.get('rm')
    print("RM", rm)
    aluno = Aluno.objects.get(pk=rm)
   
    dados = f'<div class="col-sm-6 p-3"> \
           <div class="input-group"> \
      <div class="input-group-prepend"> \
        <span class="input-group-text bg-dark text-white" id="basic-addon1"><i class="bi bi-search"></i></span>\
      </div> \
            <input type="text" name="nome" maxlength="100" class="form-control formulario" placeholder="Nome do Aluno" aria-describedby="basic-addon1" required="" id="id_nome" value="{aluno.nome}"> \
            </div> \
            </div> \
            <div class="col-sm-2 p-3"> \
            <input type="number" name="ra" maxlength="20" class="form-control formulario" placeholder="RA" required="" id="id_ra" value="{aluno.ra}"> \
        </div> \
            <div class="col-sm-4 d-flex justify-content-center"> \
    <button \
      id="atualizar2" \
      class="btn btn-outline-primary m-3"\
      title="Atualizar Aluno" \
      value="{aluno.rm}" \
    > \
      Atualizar\
    </button>\
    \
    <button\
      id="relatorio"\
      class="btn btn-outline-dark m-3"\
      title="Gerar Relatório"\
      data-bs-toggle="modal"\
      data-bs-target="#relatorioModal"\
    >\
      Relatório\
    </button>\
    <button\
      id="bkp"\
      class="btn btn-outline-primary m-3"\
      title="Enviar Cópia para a Nuvem"\
    >\
      <i class="bi bi-cloud-arrow-up-fill"></i>\
    </button>\
  </div>'
        
    return HttpResponse(dados)
       
       
def atualizar(request):
    nome = padronizar_nome(request.POST.get("nome").lstrip().rstrip())
    ra = request.POST.get("ra")
    dra = request.POST.get("dra").upper()
    dt_nascimento = request.POST.get("dt_nascimento")
    telefones = request.POST.getlist("telefones[]")
    contatos = request.POST.getlist("contatos[]")
    novos_tel = request.POST.getlist("novos_tel[]")
        
    tamanho_ra = len(ra)

    rm = int(request.POST.get("rm"))
    tamanho_nome = len(nome)
    if rm != '':
        if (tamanho_nome > REF_TAMANHO_NOME):
           
            aluno = Aluno.objects.get(pk=rm)
            aluno.nome = nome
            aluno.ra = ra
            aluno.d_ra = dra
            aluno.data_nascimento = dt_nascimento
          
            for i in range(len(telefones)):
                if len(novos_tel) > 0:
                    telefone = Telefone()
                    if novos_tel[i] == "0":
                        
                        telefone.numero = telefones[i]
                        telefone.contato = contatos[i]
                        telefone.aluno = aluno
                        
                    else:
                        telefone = Telefone.objects.get(pk=int(novos_tel[i]))
                        telefone.numero = telefones[i]
                        telefone.contato = contatos[i]
                    telefone.save()
                
            ######
            if tamanho_ra > REF_TAMANHO_RA:
                aluno.ra = ra

            aluno.save()
            print("Nome Salvo", aluno.nome)

            mensagem = criarMensagem(f"Registro de Aluno Atualizado com Sucesso!!! RM: {rm} - Nome (Atualizado): {nome}","success")
        else:
            if tamanho_ra > REF_TAMANHO_RA:
                aluno.ra = ra
            elif (tamanho_nome == 0):
                mensagem = criarMensagem("Nome em Branco!!","warning")
            else:  
                mensagem = criarMensagem("Nome muito Pequeno!","warning")
        return mensagem
    else:
        return recarregarTabela(request)


def gerarIntervalo(rm_inicial, rm_final):
    
    alunos = Aluno.objects.filter(Q(rm__gte=rm_inicial) & Q(rm__lte=rm_final))
    return alunos
  
  
def index(request):
    #migrar_dados_aluno_serie()  
    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
    
    context = {
            'form': frmAluno(),
        }

    return render(request, 'index.html', context)


def baixar_pdf(request):
   
    rmi = int(request.POST.get("rmi"))
    rmf = int(request.POST.get("rmf"))
    maior = ''
    if rmi > rmf:
        maior = rmi
        rmi = rmf
        rmf = maior
    
    alunos = gerarIntervalo(rmi, rmf)
    elements = []
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, rightMargin=30, leftMargin=50, topMargin=30, bottomMargin=20)
    
    primeira_linha = ['RM', 'Nome']
    data_alunos = []
    data_alunos.append(primeira_linha)
    stylesheet = getSampleStyleSheet()
    normalStyle = stylesheet['BodyText']
    
    for i in range(len(alunos)):
        if alunos[i].status == 1:
            data_alunos.append([Paragraph(f'<para align=center size=12><strike>{alunos[i].rm}</strike></para>',normalStyle), Paragraph(f'<para size=12><strike>{alunos[i].nome}</strike></para>')])
        else:
            data_alunos.append([Paragraph(f'<para align=center size=12>{alunos[i].rm}</para>',normalStyle), Paragraph(f'<para size=12>{alunos[i].nome}</para>')])
        
    style_table = TableStyle(([('GRID',(0,0),(-1,-1), 0.5, colors.white),
                            ('LEFTPADDING',(0,0),(-1,-1),6),
                            ('TOPPADDING',(0,0),(-1,-1),4),
                            ('BOTTOMPADDING',(0,0),(-1,-1),3),
                            ('RIGHTPADDING',(0,0),(-1,-1),6),
                            ('ALIGN',(0,0),(-1,-1),'LEFT'),
                             ('ALIGN',(0,0),(0,-1),'CENTER'),
                            ('BACKGROUND',(0,0),(1,0), colors.lavender),
                            ('LINEBELOW',(0,0),(-1,-1),1, colors.black),
                            ('FONTSIZE',(0,0), (-1,-1), 13)
                            ]))
    
    t_aluno = Table(data_alunos, style=style_table, hAlign='LEFT', repeatRows=1, colWidths=[60, 450])
    
    elements.append(t_aluno)
    
    doc.build(elements)
    nome_arquivo = str(rmi) + '_' + str(rmf) + datetime.strftime(datetime.now(),'_%d/%m/%Y_%H_%M_%S')
    response = HttpResponse(content_type='application/pdf')
    
    response['Content-Disposition'] = (
        f'attachment; filename={nome_arquivo}.pdf')
    
    response.write(buffer.getvalue())
    buffer.close()
    
    return response


# Em desenvolvimento 11/01/2024
def exibirTurmas(ano=None):
    lista = Aluno.objects.filter(Q(ano=ano))
    return lista


def baixar_pdf_lista_telefonica(request):
   
    serie = int(request.GET.get("serie"))
    turma = int(request.GET.get("turma"))
    periodo = request.GET.get("periodo")
    ano = request.GET.get("ano")
    
    alunos = exibirTurmas(serie, turma, periodo, ano)
    elements = []
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, rightMargin=30, leftMargin=50, topMargin=30, bottomMargin=20)
    
    primeira_linha = ['RM', 'Nome']
    data_alunos = []
    data_alunos.append(primeira_linha)
    stylesheet = getSampleStyleSheet()
    normalStyle = stylesheet['BodyText']
    
    for i in range(len(alunos)):
        if alunos[i].status == 1:
            data_alunos.append([Paragraph(f'<para align=center size=12><strike>{alunos[i].rm}</strike></para>',normalStyle), Paragraph(f'<para size=12><strike>{alunos[i].nome}</strike></para>')])
        else:
            data_alunos.append([Paragraph(f'<para align=center size=12>{alunos[i].rm}</para>',normalStyle), Paragraph(f'<para size=12>{alunos[i].nome}</para>')])
        
    style_table = TableStyle(([('GRID',(0,0),(-1,-1), 0.5, colors.white),
                            ('LEFTPADDING',(0,0),(-1,-1),6),
                            ('TOPPADDING',(0,0),(-1,-1),4),
                            ('BOTTOMPADDING',(0,0),(-1,-1),3),
                            ('RIGHTPADDING',(0,0),(-1,-1),6),
                            ('ALIGN',(0,0),(-1,-1),'LEFT'),
                             ('ALIGN',(0,0),(0,-1),'CENTER'),
                            ('BACKGROUND',(0,0),(1,0), colors.lavender),
                            ('LINEBELOW',(0,0),(-1,-1),1, colors.black),
                            ('FONTSIZE',(0,0), (-1,-1), 13)
                            ]))
    
    t_aluno = Table(data_alunos, style=style_table, hAlign='LEFT', repeatRows=1, colWidths=[60, 450])
    
    elements.append(t_aluno)
    
    doc.build(elements)
    nome_arquivo = str(rmi) + '_' + str(rmf) + datetime.strftime(datetime.now(),'_%d/%m/%Y_%H_%M_%S')
    response = HttpResponse(content_type='application/pdf')
    
    response['Content-Disposition'] = (
        f'attachment; filename={nome_arquivo}.pdf')
    
    response.write(buffer.getvalue())
    buffer.close()
    
    return response

