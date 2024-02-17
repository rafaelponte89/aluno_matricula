from django.db import models

# Create your models here.
#Classe do ano (NÃO IMPLEMENTADO)
class Classe(models.Model):
    
    class Meta:
        unique_together =(("serie", "turma", "ano"))
        
    PERIODO_CHOICES = (
        ("M","MANHÃ"),
        ("T","TARDE"),
    )
    serie = models.CharField(max_length=1, default='')
    turma = models.CharField(max_length=1, default='')
    ano = models.CharField(max_length=4, default='')
    periodo = models.CharField(max_length=1, choices=PERIODO_CHOICES, default='')
    def __str__(self):
        return f'{self.serie}º {self.turma} {self.periodo}'
    
    def retornarPeriodos():
        return Classe.PERIODO_CHOICES
    