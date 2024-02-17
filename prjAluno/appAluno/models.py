from django.db import models
from appClasse.models import Classe
# Create your models here.
# Aluno
class Aluno (models.Model):
    
    rm = models.IntegerField(primary_key=True,)
    nome = models.CharField(max_length=150)
    #status (0 - arquivado, 1 - cancelado, 2 - ativo) 
    status = models.IntegerField(default=0) 
    ra = models.CharField(max_length=100, default='')
    d_ra = models.CharField(max_length=1, default='')
    data_nascimento = models.CharField(max_length=10, default='')

    def __str__(self):
       
        return f'[{self.rm}] {self.nome}'
    
    # Retorna o último aluno no banco de dados
    def retornarUltimo():
        aluno = Aluno.objects.last()
        return aluno
    
    def retornarNUltimos(n=5):
        alunos = Aluno.objects.order_by('-rm')[:n]
        return alunos
    
#Telefones do aluno (NÃO IMPLEMENTADO)
class Telefone(models.Model):
    TEL_CHOICES = (
        ('M','MÃE'),
        ('P','PAI'),
        ('T','TIA/TIO'),
        ('I','IRMÃ/IRMÃO'),
        ('A','AVÓ/AVÔ'),
        ('R','RESPONSÁVEL'),
        ('O','OUTRO')
    )
    aluno = models.ForeignKey(Aluno, on_delete=models.RESTRICT)
    contato = models.CharField(max_length=1, choices=TEL_CHOICES, blank=False, null=False)
    numero = models.CharField(max_length=10, default='')
    
    def __str__(self):   
        return f'{self.numero} - {self.aluno.nome}'
    
    def retornarListaTelefones():
        return Telefone.TEL_CHOICES

#Matrícula do aluno (NÃO IMPLEMENTADO)
class Matricula(models.Model):
    SITUACAO = (
        ('C', 'CURSANDO'),
        ('T', 'TRANSFERIDO'),
        ('M', 'REMANEJADO'),
        ('P', 'PROMOVIDO'),
        ('R', 'REPROVADO'),
        ('A', 'ARQUIVADA')
    )
    ano = models.IntegerField(blank=False, null=False, default=0)
    classe = models.ForeignKey(Classe, on_delete=models.RESTRICT, default='')
    aluno = models.ForeignKey(Aluno, on_delete=models.RESTRICT, default='')
    numero = models.IntegerField(blank=False, null=False, default=0)
    situacao = models.CharField(max_length=1, choices=SITUACAO, default='A')
    data_matricula = models.DateField(null=True)
    data_movimentacao = models.DateField(null=True)
    
    def __str__(self):
        return f'{self.aluno} - {self.classe}' 
    
    class Meta:
        unique_together = ['ano', 'aluno', 'situacao', 'data_matricula']   
    
    def retornarSituacao():
        return Matricula.SITUACAO
    
        
#Documentos do aluno (NÃO IMPLEMENTADO)
class Prontuario(models.Model):
    DOCUMENTO_CHOICES = (
        ('CN','Certidão de Nascimento'),
        ('RGA','RG - Aluno'),
        ('CPFA','CPF - Aluno'),
        ('CV','Carteira Vacinação'),
        ('RGR','RG - Responsável'),
        ('CPFR','CPF - Responsável'),
        ('CNH','CNH'),
        ('FM','Ficha de Matrícula'),
        ('CR','Comprovante de Residência'),
        ('LD','Laudo'),
        ('OT','Outros')
    )
    #aluno = models.ForeignKey(Aluno)
    descricao = models.CharField(max_length=4, choices=DOCUMENTO_CHOICES, blank=False, null=False, default='') 
    caminho = models.ImageField()

    
    

    