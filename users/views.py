from rest_framework import viewsets, permissions
from notificaciones.serializers import NotificacionRespaldoSerializer

from .models import Usuario

from .serializers import UsuarioNewSerializer
from .serializers import UsuarioSerializer

from . import decrypt
import json

from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from rest_framework import status
from rest_framework import generics

from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.authentication import SessionAuthentication, BasicAuthentication, TokenAuthentication
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.contrib.auth import authenticate, login
from rest_framework.status import (
    HTTP_404_NOT_FOUND,
    HTTP_200_OK
)

from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

from rest_framework.views import APIView
from fcm_django.models import FCMDevice
from firebase_admin.messaging import Message, Notification

from datetime import datetime, timezone

LISTA_DIAS_DICT = {0:'LUNES',1:'MARTES',2:'MIÉRCOLES',3:'JUEVES',4:'VIERNES',5:'SÁBADO',6:'DOMINGO'}


class UsuarioViewSet(viewsets.ModelViewSet):
    queryset = Usuario.objects.all()
    permission_classes = [permissions.AllowAny]
    serializer_class = UsuarioSerializer


# Get if User have active Token
# Unique Token for User
@api_view(['GET'])
@authentication_classes([SessionAuthentication, BasicAuthentication, TokenAuthentication])
@permission_classes([IsAuthenticated])
def isActiveToken(request, user):
    active = Token.objects.filter(user=user).exists()
    data = {'active': active}
    return Response(data, status=status.HTTP_200_OK)


@api_view(['POST'])
@authentication_classes([])
@permission_classes([AllowAny])
def login(request):

    raw = request.data.get('raw')
    decrypted = decrypt.decrypt(raw)

    print(decrypted)

    data = json.loads(decrypted)

    print(data)

    serializer = ObtainAuthToken.serializer_class(
        data=data, context={'request': request})

    print(serializer)
    if serializer.is_valid():
        user = serializer.validated_data['user']
        usuario = Usuario.objects.get(user=user)
        token, created = Token.objects.get_or_create(user=user)
        data = {
            "message": 'Logged In',
            "username": usuario.user.username,
            "id_user_device": usuario.user.id,
            "user_tag": usuario.user_tag,
            "id_user": usuario.id,
            "user_type": usuario.user_type,
            'Auth-token': token.key,
        }
        return Response(data, status=HTTP_200_OK)

    return Response({'error': 'User not authorized'}, status=HTTP_404_NOT_FOUND)


# Obtener registro de relación finca - cultivo - usuario, si se envia el parametro user_tag, se trae solo las del usuario
@api_view(['GET'])
@authentication_classes([SessionAuthentication, BasicAuthentication, TokenAuthentication])
@permission_classes([AllowAny])
def users(request):
    
    if request.user.is_authenticated:
        data = Usuario.objects.all()
        serializer = UsuarioNewSerializer(data, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    msg = {
        'error': 'Permission Denied!'
    }
    return Response(msg, status=status.HTTP_403_FORBIDDEN)



class DeleteFCMDevice(APIView):
    permission_classes = (AllowAny,)
    def delete(self, request, *args, **kwargs):
        user=kwargs.get('pk', 0)
        if user==0:
            return Response({"Error"})
        devices=FCMDevice.objects.filter(user=user)
        for device in devices:
            device.delete()
        return Response({"Successful"})


class NotificationFCM(APIView):
    permission_classes = (AllowAny,)
    def post(self, request, *args, **kwargs):

        #print(list(Usuario.objects.values_list('id',flat=True)))
        list_tupl_user_user_type = list(Usuario.objects.values_list('id','user_type'))

        print(list(Usuario.objects.values_list('id','user_type')))
        #devices = FCMDevice.objects.all()
        devices = FCMDevice.objects.filter(user__in=[1,2,3,4])
        print(devices)
        for device in devices:
            print(device)
            print(device.send_message(Message(notification=Notification(title="Prueba Django", body="Prueba Django", image="image_url"))))
            device.is_active=True
            device.save()
        return Response({'Notificación enviada con éxito'})

class NotificationSingleFCM(APIView):
    permission_classes = (AllowAny,)
    def post(self, request, *args, **kwargs):

        #Información proveniente desde Influx
        print(request.data)
        dataNotificacionInflux = request.data
        dataNotificacionInfluxTitle = dataNotificacionInflux['_message'].split(",")[0]
        dataNotificacionInfluxBody = dataNotificacionInflux['_message'].split(",")[1]
        dataNotificacionInfluxUserTag = dataNotificacionInflux['usuario']

        try:
            data = Usuario.objects.get(user_tag=dataNotificacionInfluxUserTag)
        except Usuario.DoesNotExist:
            return Response({'message': 'Usuario no existe'},status=status.HTTP_404_NOT_FOUND)

        #Obtener id de User y enviar notificación a usuario
        device = FCMDevice.objects.get(user = data.user.id)
        device.send_message(Message(notification=Notification(title=dataNotificacionInfluxTitle, body=dataNotificacionInfluxBody)))
        device.is_active=True
        device.save()

        #Guardar data en tabla de NotificacionesRespaldo
        requestData = {}
        requestData["user_tag"] = data.user_tag
        requestData["titulo"] = dataNotificacionInfluxTitle
        requestData["cuerpo"] = dataNotificacionInfluxBody
        requestData["fue_revisada"] = "N"

        serializerNotificacion = NotificacionRespaldoSerializer(data=requestData)
        if serializerNotificacion.is_valid():
            serializerNotificacion.save()

        return Response({'Notificación enviada con éxito'})
