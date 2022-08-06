from django.db import models
from django.forms import ModelForm

import os
from django.dispatch import receiver

def get_upload_to_finca(instance, filename):
    folder_name = 'finca'
    return os.path.join(folder_name, filename)

# Create your models here.
class Finca(models.Model):
    id = models.BigAutoField(primary_key=True)
    nombre = models.CharField(max_length=200,unique=True)
    imagen = models.ImageField(null=True,blank=True,upload_to=get_upload_to_finca)
    descripcion = models.CharField(max_length=200)

    user = models.ForeignKey("users.Usuario", on_delete=models.CASCADE)

    class FincaForm(ModelForm):
        class Meta:
            ordering = ["nombre"]
            verbose_name = "Finca"

    def __str__(self):
        return self.nombre

@receiver(models.signals.post_delete, sender=Finca)
def auto_delete_file_on_delete_Finca(sender, instance, **kwargs):
    """
    Deletes file from filesystem
    when corresponding `MediaFile` object is deleted.
    """
    if instance.imagen:
        if os.path.isfile(instance.imagen.path):
            os.remove(instance.imagen.path)


@receiver(models.signals.pre_save, sender=Finca)
def auto_delete_file_on_change_Finca(sender, instance, **kwargs):
    """
    Deletes old file from filesystem
    when corresponding `MediaFile` object is updated
    with new file.
    """
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