from cultivo.models import Cultivo
from django.db import models
from django.utils.dateparse import parse_date
from django.forms import ModelForm
from django.contrib.auth.models import User


TIPO_DE_USUARIO = (
    (1, 'AGRICULTOR'),
    (2, 'ADMIN')
)

# Create your models here.
class Usuario(models.Model):
    id = models.BigAutoField(primary_key=True)
    user_tag = models.CharField(max_length=200, unique=True)
    user_type = models.IntegerField( choices = TIPO_DE_USUARIO, default=1)
    user = models.OneToOneField(User, on_delete=models.CASCADE, default=None,null=True)

    class UsuarioForm(ModelForm):
        class Meta:
            ordering = ["user.username"]
            verbose_name = "Usuario"

    def __str__(self):
        return self.user.first_name + ' - ' + self.user.last_name
