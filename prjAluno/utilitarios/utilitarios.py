from django.shortcuts import HttpResponse
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
from datetime import datetime
def criarMensagem(texto, tipo):
        
    mensagem = HttpResponse(f"<div style='display:block;' id='mensagem' class='alert alert-{tipo}' role='alert' >{texto} </div>")
    return  mensagem

def padronizar_nome(nome):
    acentuados = {'Á':'A','Ã':'A','Â':'A','É':'E','Ê':'E','Í':'I','Î':'I','Ó':'O','Õ':'O','Ô':'O','Ú':'U','Û':'U','Ç':'C','\'':'','\`':''}   
    #acentuados = {'Á':'A','Ã':'A','Â':'A','É':'E','Ê':'E','Í':'I','Î':'I','Ó':'O','Õ':'O','Ô':'O','Ú':'U','Û':'U'}   

    letra_nova = ''
    for letra in nome:
        if letra in acentuados.keys():
            letra_nova = acentuados[letra]
            nome = nome.replace(letra, letra_nova)
            
    return nome.rstrip(' ').lstrip(' ')


        
def testePadronizaNome():
    alunos = Aluno.objects.all()
    
    padronizar_nomes(alunos)
    
# Migrar Serie,Turma,Ano EM DESENVOLVIMENTO
def migrar_dados_aluno_serie():
    alunos = Aluno.objects.filter(rm__gte=3520)
    j = 0
    acumulador = 0
    ls_arquivo_csv = []
    print(len(alunos))
    with open("serie_turma.csv", "r", encoding="utf-8") as arquivo:
        arquivo_csv = csv.reader(arquivo, delimiter=",")
        for i, linha in enumerate(arquivo_csv):  
            ls_arquivo_csv.append(linha)           
    
    print("Arquivo CsvTamanho", len(ls_arquivo_csv))
    print("Objetos Alunos tamanho", len(alunos))
    for i in range(len(alunos)):
        while j < len(ls_arquivo_csv)-1:
            #print(ls_arquivo_csv[j][3])
            
            if ((alunos[i].ra).lstrip().rstrip() == (ls_arquivo_csv[j][3]).lstrip().rstrip()):
                alunos[i].serie = ls_arquivo_csv[j][0]
                alunos[i].turma = ls_arquivo_csv[j][1]
                if (ls_arquivo_csv[j][1] == 'A' or ls_arquivo_csv[j][1] == 'B'):
                    alunos[i].periodo='M'
                elif (ls_arquivo_csv[j][1] == 'C' or ls_arquivo_csv[j][1] == 'D' or ls_arquivo_csv[j][1] == 'E'):
                    alunos[i].periodo= 'T'
                else:
                    alunos[i].periodo= ''

                alunos[i].ano = ls_arquivo_csv[j][2]
                alunos[i].save()
                acumulador += 1
                print(alunos[i].nome, alunos[i].ra, alunos[i].serie,
                      alunos[i].turma, alunos[i].ano)
    
            j += 1
        j = 0
    print(acumulador)
# Migração para base de dados
def migrar_dados_aluno():
    alunos = Aluno.objects.filter(rm__gte=3520)
    j = 0
    acumulador = 0
    nomes_migrados = []
    nao_migrados = []
    nao_migrados_count = 0
    ls_arquivo_csv = []
    print(len(alunos))
    with open("alunos.csv","r",encoding="utf-8") as arquivo:
        arquivo_csv = csv.reader(arquivo, delimiter=",")
        for i, linha in enumerate(arquivo_csv):  
            ls_arquivo_csv.append(linha)           
    
    print("Arquivo CsvTamanho",len(ls_arquivo_csv))
    print("Objetos Alunos tamanho", len(alunos))
    for i in range(len(alunos)):
        while j < len(ls_arquivo_csv)-1:
            nome_aluno = padronizar_nome(alunos[i].nome)
            nome_aluno_csv = padronizar_nome(ls_arquivo_csv[j][0])
            if nome_aluno == nome_aluno_csv and nome_aluno not in nomes_migrados:
                    alunos[i].ra = ls_arquivo_csv[j][1]
                    alunos[i].d_ra = ls_arquivo_csv[j][2]
                    alunos[i].data_nascimento = ls_arquivo_csv[j][3]
                    alunos[i].save()
                    nomes_migrados.append(nome_aluno)
                    acumulador += 1
                    print(nome_aluno == nome_aluno)
                    print(acumulador)
            j += 1
        j = 0
        
    for i in range(len(alunos)):
        nome_aluno = padronizar_nome(alunos[i].nome)
        for j in range(len(nomes_migrados)):
            if nome_aluno not in nomes_migrados and nome_aluno not in nao_migrados:
                nao_migrados.append(nome_aluno)
                nao_migrados_count += 1
                #print(padronizar_nome(linha[0]),"RA:", linha[1],"Digito RA",linha[2],"Data Nascimento:",linha[3] )
    with open("migracao_quantidade_alunos.txt","w") as arquivo:
        for nome in nomes_migrados:
            arquivo.write(nome + '\n')    
        arquivo.write("Total de Mudancas: " +  str(acumulador))
    with open("nao_migrados.txt","w") as arquivo:
        for nome in nao_migrados:
            arquivo.write(nome + '\n')    
        arquivo.write("Nao Migrados: " +  str(nao_migrados_count))
    
# Converte data do formato dd/mm/aaaa para aaaa-mm-dd
def converter_data():
    alunos = Aluno.objects.all()
    
    try:    
        for aluno in alunos:
            if len(aluno.data_nascimento) > 0:
                data_nascimento = datetime.strptime(aluno.data_nascimento, "%d/%m/%Y").date()
                data_convertida = data_nascimento.strftime("%Y-%m-%d")
                aluno.data_nascimento = data_convertida
                aluno.save()
    except:
        pass
# Create your views here.
def criar_log(mensagem, texto):
    with open('log_backup.txt','a') as bkp_log:
        bkp_log.write((datetime.now().strftime('%d/%m/%Y - %H:%M:%S') + ' Status: ' + mensagem + ' Descricao: ' + texto + '\n'))


# backup utilizando pydrive
def realizar_backup_v2(request):
   
    try:
        gauth = GoogleAuth()
        #gauth.CommandLineAuth()
        gauth.LocalWebserverAuth()
        drive = GoogleDrive(gauth)
        #gauth.LocalWebserverAuth()
   
        #gauth.LocalWebserverAuth()
        arquivo = "db.sqlite3"
        gfile = drive.CreateFile({'parents': [{'id': '1TeRTAGnqX8gkBvFDQovVGtZrvm8GhK0s'}]})
        gfile.SetContentFile(f"bd/{arquivo}")
        gfile.Upload()
        criar_log("Salvo com sucesso", f"Upload {arquivo}")
        return criarMensagem(f"Backup Efetuado na Nuvem!!! Arquivo: {arquivo}", "info")
    except(Exception):
        return criarMensagem(f"Falha no Backup!!!", "danger")

  

             
