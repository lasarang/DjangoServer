from rest_framework import serializers

from finca.serializers import FincaSerializer
from users.serializers import UsuarioSerializer
from .models import Cultivo, ListaCultivo

class CultivoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cultivo
        fields = ('id',
                  'nombre',
                  'imagen',
                  'minimo_temperatura',
                  'maximo_temperatura',
                  'minimo_humedad',
                  'maximo_humedad',
                  'minimo_precipitacion',
                  'maximo_precipitacion',
                  'minimo_radiacion',
                  'maximo_radiacion'
                 )


class ListaCultivoSerializer(serializers.ModelSerializer):
    class Meta:
        model = ListaCultivo
        fields = ('id',
                  'id_cultivo',
                  'id_finca',
                  'id_user'
                 )


class ListaCultivoNewSerializer(serializers.ModelSerializer):
    cultivo = CultivoSerializer(read_only=True,source='id_cultivo')
    finca = FincaSerializer(read_only=True,source='id_finca')
    user = UsuarioSerializer(read_only=True,source='id_user')
    class Meta:
        model = ListaCultivo
        fields = ('id',
                  'cultivo',
                  'finca',
                  'user'
                 )