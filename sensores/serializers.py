from rest_framework import serializers
from .models import RaspBerry

class RaspBerrySerializer(serializers.ModelSerializer):
	class Meta:
		model = RaspBerry
		fields = (
			'id',
			'cultivo', 
			'finca',
			'user',
		)
