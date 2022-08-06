from rest_framework import serializers

from notificaciones.models import NotificacionRespaldo


class NotificacionRespaldoSerializer(serializers.ModelSerializer):
   class Meta:
      model = NotificacionRespaldo
      fields = ('id',
               'user_tag',
               'titulo',
               'cuerpo',
               'fue_revisada',
               'fecha',
               'dia'
               )