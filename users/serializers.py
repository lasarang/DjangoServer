from rest_framework import serializers
from .models import Usuario

from django.contrib.auth.models import User

class UserSerializer(serializers.ModelSerializer):
	class Meta:
		model = User
		fields = ('id','username', 'password','first_name', 'last_name', 'email')

class UsuarioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Usuario
        fields = ('id','user','user_tag')


class UserNewSerializer(serializers.ModelSerializer):
	class Meta:
		model = User
		fields = ('id','username','first_name', 'last_name', 'email')

class UsuarioNewSerializer(serializers.ModelSerializer):
    data_user_table = UserNewSerializer(read_only=True,source='user')
    class Meta:
        model = Usuario
        fields = ('id',
                  'data_user_table',
                  'user_tag',
                  'user_type'
                 )