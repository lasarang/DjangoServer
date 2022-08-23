from finca.models import Finca
from django.db import models
from django.forms import ModelForm

import os
from django.dispatch import receiver

def get_upload_to_cultivo(instance, filename):
    folder_name = 'cultivo'
    #print(instance.hueca_id)
    return os.path.join(folder_name, filename)

# Create your models here.
class Cultivo(models.Model):
    id = models.BigAutoField(primary_key=True)
    nombre = models.CharField(max_length=200,unique=True)
    imagen = models.ImageField(null=True,blank=True,upload_to=get_upload_to_cultivo)
    minimo_temperatura = models.FloatField(blank=True,default=0)
    maximo_temperatura = models.FloatField(blank=True,default=0)

    minimo_humedad = models.FloatField(blank=True,default=0)
    maximo_humedad = models.FloatField(blank=True,default=0)

    minimo_precipitacion = models.FloatField(blank=True,default=0)
    maximo_precipitacion = models.FloatField(blank=True,default=0)

    minimo_radiacion = models.FloatField(blank=True,default=0)
    maximo_radiacion = models.FloatField(blank=True,default=0)

    class CultivoForm(ModelForm):
        class Meta:
            ordering = ["nombre"]
            verbose_name = "Cultivo"

    def __str__(self):
        return self.nombre

@receiver(models.signals.post_delete, sender=Cultivo)
def auto_delete_file_on_delete_Cultivo(sender, instance, **kwargs):
    """
    Deletes file from filesystem
    when corresponding `MediaFile` object is deleted.
    """
    if instance.imagen:
        if os.path.isfile(instance.imagen.path):
            os.remove(instance.imagen.path)


@receiver(models.signals.pre_save, sender=Cultivo)
def auto_delete_file_on_change_Cultivo(sender, instance, **kwargs):
    """
    Deletes old file from filesystem
    when corresponding `MediaFile` object is updated
    with new file.
    """

    print(sender)
    print(instance)
    print(instance.pk)
    print("instance")

    if not instance.pk:
        return False

    try:
        old_file = sender.objects.get(pk=instance.pk).imagen
    except sender.DoesNotExist:
        return False

    new_file = instance.imagen
    if not old_file == new_file:
        if os.path.isfile(old_file.path):
            os.remove(old_file.path)


class ListaCultivo(models.Model):
    id = models.BigAutoField(primary_key=True)
    id_cultivo = models.ForeignKey(Cultivo, on_delete=models.CASCADE)
    id_finca = models.ForeignKey(Finca, on_delete=models.CASCADE)
    #esActivo = models.BooleanField(default=True)
    id_user = models.ForeignKey("users.Usuario", on_delete=models.CASCADE)
    minimo_temperatura = models.FloatField(blank=True,default=0)
    maximo_temperatura = models.FloatField(blank=True,default=0)

    minimo_humedad = models.FloatField(blank=True,default=0)
    maximo_humedad = models.FloatField(blank=True,default=0)

    minimo_precipitacion = models.FloatField(blank=True,default=0)
    maximo_precipitacion = models.FloatField(blank=True,default=0)

    minimo_radiacion = models.FloatField(blank=True,default=0)
    maximo_radiacion = models.FloatField(blank=True,default=0)

    class Meta:
        verbose_name = "ListaCultivo"
        unique_together = ('id_finca', 'id_user',)
        
    
    def __str__(self):
        return self.id_cultivo.nombre + ' - ' + self.id_finca.nombre + ' - ' + self.id_user.user.first_name + '-' + self.id_user.user.last_name