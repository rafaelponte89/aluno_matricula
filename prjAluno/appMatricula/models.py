from django.db import models
from appClasse.models import Classe
from appAluno.models import Aluno
# Create your models here.
#Matrícula do aluno (NÃO IMPLEMENTADO)
class Matricula(models.Model):
    SITUACAO = (
        ('C', 'CURSANDO'),
        ('BXTR', 'TRANSFERIDO'),
        ('REMA', 'REMANEJADO'),
        ('NCFP', 'Ñ COMP. FORA PRAZO'),
        ('P', 'PROMOVIDO'),
        ('R', 'REPROVADO'),
    )
    ano = models.IntegerField(blank=False, null=False, default=0)
    classe = models.ForeignKey(Classe, on_delete=models.RESTRICT, default='')
    aluno = models.ForeignKey(Aluno, on_delete=models.RESTRICT, default='')
    numero = models.IntegerField(blank=False, null=False, default=0)
    situacao = models.CharField(max_length=4, choices=SITUACAO, default='A')
    data_matricula = models.DateField(null=True)
    data_movimentacao = models.DateField(null=True)
    
    def __str__(self):
        return f'{self.aluno} - {self.classe}' 
    
    class Meta:
        unique_together = ['id', 'ano', 'aluno', 'situacao', 'data_matricula']   
    
    def retornarSituacao():
        return Matricula.SITUACAO
