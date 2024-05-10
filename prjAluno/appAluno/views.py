from django.shortcuts import render, redirect
from .models import Aluno, Telefone
from appClasse.models import Classe
from appMatricula.models import Matricula
from .forms import frmAluno
from django.http import HttpResponse
from django.db.models import Q
from django.views.decorators.csrf import csrf_exempt
from utilitarios.utilitarios import criarMensagem, padronizar_nome, retornarNomeMes, anonimizarDado
import io
from os import path
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib.styles import getSampleStyleSheet
from datetime import datetime
from datetime import datetime

REF_TAMANHO_NOME = 2
REF_TAMANHO_RA = 7


def buscar_duplicados(alunos):
   
    nomes_rm = {}
    duplicados = {}
    for aluno in alunos:
        nome = aluno.nome.strip().upper()
        if aluno.status != 1:
            nomes_rm.setdefault(nome, []).append(aluno.rm)
   
    duplicados = {k: v for k, v in nomes_rm.items() if len(v) > 1}
            
    return duplicados.keys()
    
    
# Gravar registro do Aluno
def gravar(request):
    nome = padronizar_nome(request.POST.get("nome"))
    ra = request.POST.get("ra")
    
    if request.method != 'POST' or not (is_ajax := request.headers.get('X-Requested-With') == 'XMLHttpRequest'):
        return
    
    form = frmAluno({"nome": nome, "ra": ra})
    if form.is_valid():
        if len(nome) > REF_TAMANHO_NOME and len(ra) > REF_TAMANHO_RA:
            form.save()
            return criarMensagem("Aluno Registrado com Sucesso!", "success")
        return criarMensagem("Nome muito Pequeno!" if len(nome) == 0 else "RA muito Pequeno", "warning")
    return criarMensagem("Nome em Branco!!" if len(nome) == 0 else "RA em Branco!!", "warning")


def retornar_ultima_matricula_ativa(aluno):
    ultima_matricula = Matricula.objects.filter(aluno=aluno).filter(situacao='C').order_by('-ano').first()
    return ultima_matricula.classe if ultima_matricula else '-'
    
    
def atualizarTabela(alunos):
    nomes_duplicados = buscar_duplicados(alunos)
    tabela = ''
    
    for aluno in alunos:
        nome = aluno.nome.strip().upper()
        status_rm = f'<td class="align-middle">{aluno.rm}</td>'
        botao = ''
        botao_declaracao = ''
        classes = 'btn btn-outline-dark btn-lg'
        icon = '<i class="bi bi-arrow-repeat"></i>'

        if aluno.status == 1:
            icon = '<i class="bi bi-x-circle-fill"></i>'
            classes = 'btn btn-outline-danger btn-lg  disabled'
            
        elif nome in nomes_duplicados:
            status_rm = f'<td>{aluno.rm}'
            status_rm += f'<button "type="button" class="btn btn-outline-primary btn-sm m-1 advertencia" value="{aluno.rm}" data-bs-toggle="modal" data-bs-target="#resolucaoDuplicidadeModal"><i class="bi bi-person-fill-exclamation"></i></button></td>'
       
        botao += f'<button type="button" class="{classes} atualizar" value="{aluno.rm}"\
                 data-bs-toggle="modal" data-bs-target="#atualizarModal">\
                 {icon}\
                 </button>'
        
        botao_declaracao += f'<button type="button" class="{classes} declaracao" value="{aluno.rm}">\
                 <i class="bi bi-journal"></i>\
                 </button>'
      
            
        tabela += f"""<tr>{status_rm}
                        <td class="align-middle">{aluno.nome}</td> 
                        <td class="align-middle text-center">{retornar_ultima_matricula_ativa(aluno)}</td> 
                        <td class="align-middle text-center">{retornar_numeros_telefones(aluno)}</td> 
                        <td class="align-middle text-center">{aluno.ra}</td> 
                        <td class="align-middle text-center conteudoAtualizar">{botao}</td>
                        <td class="align-middle text-center">{botao_declaracao}</td>

                    </tr>"""    

    return HttpResponse(tabela)

def cancelarRM(request):
    rm_req = int(request.POST.get('rm'))
    aluno = Aluno.objects.get(pk=rm_req)
    aluno.status = 1
    aluno.save()
    return criarMensagem(f"{aluno.nome} - {aluno.rm} : Cancelado!!!","success")


# reset na tabela 
def recarregarTabela(request):
    alunos = Aluno.retornarNUltimos()
    tabela = atualizarTabela(alunos)
    return tabela


def buscar(request):
    nome = padronizar_nome(request.POST.get("nome"))
    filtro = (request.POST.get("filtro"))
    print('filtro', filtro)
    
    if len(nome) > REF_TAMANHO_NOME:
        if filtro == 'a':
            status = 2
            alunos = Aluno.objects.filter(status=status).filter(nome__contains=nome)[:10]

        else:
            alunos = Aluno.objects.filter(nome__contains=nome)[:10]
        buscar_duplicados(alunos)
        tabela = atualizarTabela(alunos)
        
        return tabela if tabela.content else criarMensagem("Aluno Não Encontrado", "info")
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
    

def retornar_numeros_telefones(aluno):
    telefones = (Telefone.objects.filter(aluno=aluno)
                 .values_list("numero", flat=True))
    texto_numeros = ("" .join(f"<span class='m-1'>{numero}</span>" 
                              for numero in telefones))
    return texto_numeros
  
    
def retornar_telefones(aluno):
    telefones = Telefone.retornarListaTelefones()
    telefones_aluno = Telefone.objects.filter(aluno=aluno)
    print(telefones)
    for telefone in telefones_aluno:
        print(telefone.contato)
   
# em desenvolvimento 10/05/2024
def buscar_historico_matriculas(request):
    rm = request.POST.get('rm')
    aluno = Aluno.objects.get(pk=rm)
    matriculas_aluno = Matricula.objects.filter(aluno=aluno).order_by('-ano')
    dados_matricula=''
    
    for matricula in matriculas_aluno:
        descritivo_situacao = Matricula.retornarDescricaoSituacao(matricula)
        dados_matricula += f"""
                   <div class="col-12 form-group d-flex align-items-center"> 
                  <input        
                    type="text"     
                    class="form-control m-2" 
                   
                    aria-describedby="emailHelp" 
                    placeholder="Ano" 
                    value="{matricula.ano}"
                    disabled
                  /> 
                   <input        
                    type="text"     
                    class="form-control m-2" 
                   
                    aria-describedby="emailHelp" 
                    placeholder="Ano" 
                    value=" {descritivo_situacao}"
                    disabled
                  /> 
                      
                      <input        
                    type="text"     
                    class="form-control m-2" 
                    
                    aria-describedby="emailHelp" 
                    placeholder="Ano" 
                    value="{matricula.classe}"
                    disabled
                  /> 
                </div>"""
    
    return HttpResponse(dados_matricula)

def buscar_telefones_aluno(request):
    rm = request.POST.get('rm')
    aluno = Aluno.objects.get(pk=rm)
    telefones = Telefone.retornarListaTelefones()
    telefones_aluno = Telefone.objects.filter(aluno=aluno)
    selecionado = "" 
    adicionar_tel = """<div class="row">
               <div class="col-1 form-group d-flex">
                  <button id="addTelefone" type="button" class="btn btn-primary mt-3"><i class="bi bi-telephone-plus"></i></button>
                </div>
            </div>"""
    
    def retornar_telefone( telefones_aluno):  
        selecionado_tel = ""     
        opcoes_telefone = f"<option {selecionado}> Selecione </option>"
        for i in range(len(telefones)):
            sigla, contato = telefones[i]
            if telefones_aluno.contato == sigla:
                selecionado_tel = "selected"
                opcoes_telefone += f"""<option value={sigla} {selecionado_tel}>{contato}</option>"""
            else:
                
                opcoes_telefone += f"""<option value='{sigla}'>{contato}</option>"""
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

    dados_telefone = adicionar_tel + dados_telefone
    return HttpResponse(dados_telefone)


def buscar_dados_aluno(request):
    rm = request.POST.get('rm')
    print("RM", rm)
    aluno = Aluno.objects.get(pk=rm)

    telefones = Telefone.retornarListaTelefones()
    matriculas = Matricula.retornarSituacao()
    telefones_aluno = Telefone.objects.filter(aluno=aluno)
    matriculas_aluno = Matricula.objects.filter(aluno=aluno).order_by('-ano')
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
                
                opcoes_telefone += f"""<option value='{sigla}'>{contato}</option>"""
        return opcoes_telefone
    
    def retornar_matricula(matriculas_aluno):  
        situacao = ''
        for i in range(len(matriculas)):
            sigla, situacao = matriculas[i]
            if matriculas_aluno.situacao == sigla or (matriculas_aluno.situacao == 'TRAN' and sigla == 'BXTR'):
                situacao = situacao
                break
        return situacao
    
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
                    type="text"     
                    class="form-control m-2" 
                   
                    aria-describedby="emailHelp" 
                    placeholder="Ano" 
                    value="{matriculas_aluno[i].ano}"
                    disabled
                  /> 
                   <input        
                    type="text"     
                    class="form-control m-2" 
                   
                    aria-describedby="emailHelp" 
                    placeholder="Ano" 
                    value=" {retornar_matricula(matriculas_aluno[i])}"
                    disabled
                  /> 
                      
                      <input        
                    type="text"     
                    class="form-control m-2" 
                    
                    aria-describedby="emailHelp" 
                    placeholder="Ano" 
                    value="{matriculas_aluno[i].classe}"
                    disabled
                  /> 
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
            
            <ul class="nav nav-tabs mt-4">
                <li class="nav-item">
                    <a id="aba1" class="nav-link active" aria-current="page" href="#">Telefones</a>
                </li>
                <li class="nav-item">
                    <a id="aba2" class="nav-link" href="#">Matrículas</a>
                </li>
 
            </ul>

            <div id="dados" class="mb-2">

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
       
#Atualizar registro do aluno      
def atualizar(request):
    print(request.POST.get("nome"))
    nome = padronizar_nome(request.POST.get("nome"))
    ra = request.POST.get("ra")
    dra = request.POST.get("dra").upper()
    dt_nascimento = request.POST.get("dt_nascimento")
    telefones = request.POST.getlist("telefones[]")
    print("telefones",telefones)
    contatos = request.POST.getlist("contatos[]")
    print("contato",contatos)
    novos_tel = request.POST.getlist("novos_tel[]")
    print("novos_tel",novos_tel)
        
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
    context = {'form': frmAluno()}
    return render(request, 'index.html', context)

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


def baixar_lista_telefonica(request):
    from reportlab.lib.pagesizes import A4

    classe = Classe.objects.get(pk=int(request.POST.get("classe")))
    matriculas = Matricula.objects.filter(classe=classe).order_by('numero')
    
    telefones = ''
    elements = []
    
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, rightMargin=30, leftMargin=30, topMargin=30, bottomMargin=20, pagesize=(A4[1], A4[0]))
    
    titulo = "Lista Telefônica " + str(classe)
    print(titulo)
    
    primeira_linha = ['Nº','Nome', 'Telefones']
    data_alunos = []
    data_alunos.append([titulo])
    data_alunos.append(primeira_linha)
    
    for m in matriculas:
        aluno = Aluno.objects.get(pk=m.aluno.rm)
        tel_aluno = Telefone.objects.filter(aluno=aluno)[:6]
        for t in tel_aluno:
            telefones = telefones + str(t) + ' '
        data_alunos.append([m.numero, m.aluno.nome, telefones])
        telefones = ''       
                 
    style_table = TableStyle(([('GRID',(0,1),(-1,-1), 0.5, colors.gray),
                               ('SPAN', (0,0), (2,0)),
                            ('LEFTPADDING',(0,0),(-1,-1),6),
                            ('TOPPADDING',(0,0),(-1,-1),4),
                            ('BOTTOMPADDING',(0,0),(-1,-1),3),
                            ('RIGHTPADDING',(0,0),(-1,-1),6),
                            ('ALIGN',(0,0),(-1,-1),'LEFT'),
                             ('ALIGN',(0,0),(0,-1),'CENTER'),
                            ('BACKGROUND',(0,1),(2,1), colors.lavender),
                            ('FONTSIZE',(0,0), (-1,-1), 13),
                            ('BOTTOMPADDING',(0,0),(0,0),20),
                            ('FONTSIZE',(0,0),(0,0),18),
                            ]))
    
    t_aluno = Table(data_alunos, hAlign='CENTER', 
                    repeatRows=1, style=style_table)
    
    elements.append(t_aluno)
    
    doc.build(elements, )
    nome_arquivo = str(classe) + datetime.strftime(datetime.now(),'_%d/%m/%Y_%H_%M_%S')
    response = HttpResponse(content_type='application/pdf')
    
    response['Content-Disposition'] = (
        f'attachment; filename={nome_arquivo}.pdf')
    
    response.write(buffer.getvalue())
    buffer.close()
    
    return response


## Nova Personalizável
def footer(canvas, doc, content):
    canvas.saveState()
    w, h = content.wrap(doc.width, doc.bottomMargin)
    content.drawOn(canvas, doc.leftMargin, h)

    canvas.restoreState()

def header_and_footer(canvas, doc, header_content, footer_content):
    header(canvas, doc, header_content,)
    footer(canvas, doc, footer_content)

def header(canvas, doc, content):
        canvas.saveState()
        w, h = content.wrap(doc.width, doc.topMargin)
        content.drawOn(canvas, doc.leftMargin, doc.height + doc.bottomMargin + doc.topMargin - h)
        canvas.restoreState()
        
def baixar_lista_alunos_personalizavel(request):
    from reportlab.lib.pagesizes import A4
    from reportlab.platypus.paragraph import Paragraph
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import cm
    from reportlab.platypus import SimpleDocTemplate, PageTemplate
    from reportlab.platypus.frames import Frame
    from reportlab.lib import pagesizes
    from reportlab.platypus.paragraph import Paragraph
    from functools import partial

    
    classe = Classe.objects.get(pk=int(request.POST.get("classe")))

    titulo_lista = request.POST.get('titulo')
    tamanho_fonte = float(request.POST.get('tamanho_fonte'))
    colunas_em_branco = (request.POST.get('colunas')).split(',')
   
    tamanho_colunas_em_branco = (request.POST.get('tam_colunas')).split(',')
    
    tipo_pagina = request.POST.get('pagina')
    repeticao = int(request.POST.get('repeticao'))

    if tipo_pagina == 'r':
        tamanho_pagina = (A4[0], A4[1])  # retrato
    else:
        tamanho_pagina = (A4[1], A4[0])  # paisagem

    classe = Classe.objects.get(pk=int(request.POST.get("classe")))
    matriculas = (Matricula.objects.filter(classe=classe).
                  filter(situacao='C').
                  order_by('aluno__nome'))

    
    buffer = io.BytesIO()

    titulo = str(titulo_lista) + " - " + str(classe)
    print(titulo)
    primeira_linha = ['Nº','Nome']
    primeira_linha.extend(colunas_em_branco)
    data_alunos = []
    data_alunos.append([titulo])
    data_alunos.append(primeira_linha)



    style = ParagraphStyle(
        name='Normal',
        fontSize=10,
        alignment=1
    )



    pdf = SimpleDocTemplate(buffer, pagesize=tamanho_pagina, 
        leftMargin = 1.5 * cm, 
        rightMargin = 1.5 * cm,
        topMargin = 1.5 * cm, 
        bottomMargin = 0.5 * cm)

    frame = Frame(pdf.leftMargin, pdf.bottomMargin, pdf.width, pdf.height, id='normal')
    
    if tipo_pagina == 'r':
        espacos = "&nbsp;" *52
        header_content =( Paragraph(f"""
                               <strong><font size="18">EMEB PROFª VICTÓRIA OLIVITO NONINO </font></strong> <br/>
                                 Rua 14, 1303 A - Conjunto Habtacional José Luís Simões - Orlândia - SP - (16)3820-8230  <br/>
                                 <img src="appAluno/static/appAluno/jpeg/logo_prefeitura.jpg" valign="middle" height="50" width="50" />{espacos}victorianonino@gmail.com {espacos}<img src="appAluno/static/appAluno/jpeg/logo_escola.jpg" valign="middle" height="50" width="50" />""", style=style ) )
      
    
    else:
        espacos = "&nbsp;" * 53
        header_content =( Paragraph(f"""
                               <strong><font size="18">EMEB PROFª VICTÓRIA OLIVITO NONINO </font></strong> <br/>
                                 Rua 14, 1303 A - Conjunto Habtacional José Luís Simões - Orlândia - SP - (16)3820-8230  <br/>
                                 <img src="appAluno/static/appAluno/jpeg/logo_prefeitura.jpg" valign="middle" height="50" width="50" />{espacos}victorianonino@gmail.com {espacos}<img src="appAluno/static/appAluno/jpeg/logo_escola.jpg" valign="middle" height="50" width="50" />""", style=style ) )
                     
    
    count = 0
    linha = ''
    for m in matriculas:
       
        for i in range(1, repeticao + 1):
            count += 1
            linha = [count, str(m.aluno.nome)]
            for col in range(len(colunas_em_branco)):
                linha.append(' ' * int(tamanho_colunas_em_branco[col]) )
            
            data_alunos.append(linha)
    colunas_totais = len(colunas_em_branco) + 1               
    style_table = TableStyle(([('GRID',(0,1),(-1,-1), 0.5, colors.gray),
                               ('SPAN', (0,0), (colunas_totais, 0)),
                            ('LEFTPADDING',(0,0),(-1,-1),6),
                            ('TOPPADDING',(0,0),(-1,-1),4),
                            ('BOTTOMPADDING',(0,0),(-1,-1),3),
                            ('RIGHTPADDING',(0,0),(-1,-1),6),
                            ('ALIGN',(0,0),(-1,-1),'LEFT'),
                             ('ALIGN',(0,0),(0,-1),'CENTER'),
                            ('BACKGROUND',(0,1),(colunas_totais,1), colors.lavender),
                            ('FONTSIZE',(0,0), (-1,-1), 13),
                            ('BOTTOMPADDING',(0,0),(0,0),20),
                            ('FONTSIZE',(0,0),(0,0),18),
                            ('FONTSIZE',(0,2),(-1,-1), tamanho_fonte)
                            ]))
    
    t_aluno = Table(data_alunos, style=style_table, hAlign='CENTER', 
                    repeatRows=2)

    template = PageTemplate(id='test', frames=frame, onPage=partial(header, content=header_content))

    pdf.addPageTemplates([template])


    
    # conteudo
    pdf.build([t_aluno], onLaterPages=partial(header, content=header_content))

    response = HttpResponse(content_type='application/pdf')
    
    response.write(buffer.getvalue())
    buffer.close()
    
    return response

# Em Desenvolvimento 05/05/2024
def baixar_declaracao(request):
    from reportlab.lib.pagesizes import A4
    from reportlab.platypus.paragraph import Paragraph
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import cm
    from reportlab.platypus import SimpleDocTemplate, PageTemplate
    from reportlab.platypus.frames import Frame
    from reportlab.lib import pagesizes
    from reportlab.platypus.paragraph import Paragraph
    from functools import partial

    tamanho_pagina = (A4[0], A4[1])  # retrato
    
    aluno = Aluno.objects.get(pk = request.POST.get('rm'))
    matricula = Matricula.objects.filter(aluno=aluno).order_by('-ano').order_by('id').last()
    #matricula = Matricula.objects.filter(aluno=aluno).filter(situacao='C').order_by('-ano').first()
    nome_operador = request.POST.get('nome_op')
    cargo_operador = request.POST.get('cargo_op')
    rg_operador = request.POST.get('rg_op')

    buffer = io.BytesIO()

    style = ParagraphStyle(
        name='Normal',
        fontSize=10,
        alignment=1
    )
    
    corpo = ParagraphStyle(
        name='Arial',
        fontSize=14,
        alignment=4,
        firstLineIndent=40,
        spaceBefore = 15,
        leading=24
        
      
    )
    
    titulo = ParagraphStyle(
        name='Arial',
        fontSize=18,
        alignment=1,
        spaceAfter=40
    )

    style_data = ParagraphStyle(
        name='Arial',
        fontSize=14,
        alignment=2,
        spaceAfter=40
    )
    
    quebras="<br/>"*15
    p_quebras = Paragraph(f"""{quebras}""")

    pdf = SimpleDocTemplate(buffer, pagesize=tamanho_pagina, 
        leftMargin = 1.5 * cm, 
        rightMargin = 1.5 * cm,
        topMargin = 1.5 * cm, 
        bottomMargin = 0.5 * cm)

    frame = Frame(pdf.leftMargin, pdf.bottomMargin, pdf.width, pdf.height, id='normal')
    
    espacos = "&nbsp;"*52
    header_content =(Paragraph(f"""
                               <strong><font size="18">EMEB PROFª VICTÓRIA OLIVITO NONINO </font></strong> <br/>
                                 Rua 14, 1303 A - Conjunto Habtacional José Luís Simões - Orlândia - SP - (16)3820-8230  <br/>
                                 <img src="appAluno/static/appAluno/jpeg/logo_prefeitura.jpg" valign="middle" height="50" width="50" />{espacos}victorianonino@gmail.com {espacos}<img src="appAluno/static/appAluno/jpeg/logo_escola.jpg" valign="middle" height="50" width="50" />""", style=style ) )
      
   
    if matricula is not None:
        descritivo_situacao = Matricula.retornarDescricaoSituacao(matricula)
        dt_nascimento = (aluno.data_nascimento).split('-')
    
        quebras = "<br/>" * 6
        data = datetime.now()
        data_emissao = Paragraph(f"""Orlândia, {data.day} de {retornarNomeMes(data.month)} de {data.year}.""",style=style_data)

        if matricula.situacao == 'C':
            p_titulo = Paragraph("""<strong><u>Declaração de Matrícula</u> </strong>""",style=titulo)
            p1 = (Paragraph(f"""Declaro, para os devidos fins de direito, que o(a) aluno(a) <strong>{aluno.nome} </strong>, 
                        portador(a) do RA Escolar: <strong>{aluno.ra} - {aluno.d_ra} SP </strong> está <strong>{descritivo_situacao}</strong> o 
                        <strong>{matricula.classe} </strong> do Ensino Fundamental de 9 anos nesta unidade no ano letivo de <strong>{matricula.ano}</strong>.""", style=corpo))
        elif matricula.situacao == 'BXTR':    
            p_titulo = Paragraph("""<strong><u>Declaração de Transferência</u> </strong>""",style=titulo)
            p1 =(Paragraph(f"""Declaro para os devidos fins de direito, que o(a) aluno(a): <strong>{aluno.nome}</strong> nascido(a) em <strong>{dt_nascimento[2]}/{dt_nascimento[1]}/{dt_nascimento[0]} </strong>
                    portador(a) do RA Escolar: <strong>{aluno.ra} - {aluno.d_ra}</strong> do <strong>{matricula.classe} </strong> do Ensino Fundamental de 9 anos nesta unidade escolar,
                    solicitou na presente data <strong>transferência </strong> para estabelecimento congênere, estando apto(a) ao prosseguimento de estudos no <strong>{matricula.classe.serie}º ano
                    do Ensino Fundamental de 9 anos</strong>.""", style=corpo))
        p2 = Paragraph(f"""Por ser expressão da verdade firmo a presente declaração.""", style=corpo)

    else:
        p_titulo = Paragraph("""""")
        p1 = Paragraph("""Sem informações a exibir!!!""", style=titulo)
        data_emissao = Paragraph("""""")
        p2 = Paragraph("""""")


    

    p_assinatura = Paragraph(f"""________________________________<br/> {nome_operador} <br/>{cargo_operador}<br/>RG: {rg_operador}""", style=style)
    template = PageTemplate(id='test', frames=frame, onPage=partial(header, content=header_content))
    pdf.addPageTemplates([template])
  
   
    # conteudo
    pdf.build([p_quebras,data_emissao,p_titulo,p1,p2,p_quebras,p_assinatura], onLaterPages=partial(header, content=header_content))

    response = HttpResponse(content_type='application/pdf')
    
    response.write(buffer.getvalue())
    buffer.close()
    
    return response
