from django.db import models
from django.utils import timezone

# Create your models here.

LISTA_DIAS = (
   (0, 'LUNES'),
   (1, 'MARTES'),
   (2, 'MIÉRCOLES'),
   (3, 'JUEVES'),
   (4, 'VIERNES'),
   (5, 'SÁBADO'),
   (6, 'DOMINGO'),
)

class NotificacionRespaldo(models.Model):
   id = models.BigAutoField(primary_key=True)
   user_tag = models.CharField(max_length=200)
   titulo = models.CharField(max_length=2000)
   cuerpo = models.CharField(max_length=2000)
   fue_revisada = models.CharField(max_length=1)
   fecha = models.DateTimeField(default=timezone.now, blank=True)
   dia = models.IntegerField(choices = LISTA_DIAS, default=timezone.now().weekday(), blank=True)
