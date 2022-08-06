from rest_framework import serializers
from .models import Finca

class FincaSerializer(serializers.ModelSerializer):
	class Meta:
		model = Finca
		fields = ('id','nombre', 'imagen', 'user', 'descripcion')
