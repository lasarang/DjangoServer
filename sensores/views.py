from finca.models import Finca
from cultivo.models import Cultivo
from users.models import Usuario
from django.shortcuts import render
from rest_framework import viewsets, permissions

from .models import RaspBerry

from .serializers import RaspBerrySerializer

import json

from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from rest_framework import status
from rest_framework import generics

from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.authentication import SessionAuthentication, BasicAuthentication, TokenAuthentication
from rest_framework.permissions import AllowAny
from rest_framework.authtoken.models import Token

from datetime import datetime


class RaspBerryViewSet(viewsets.ModelViewSet):
    queryset = RaspBerry.objects.all()
    permission_classes = [permissions.AllowAny]
    serializer_class = RaspBerrySerializer

# Lee una lista de objetos (RPI) que tiene id, cultivo, finca del usuario auth
@api_view(['GET'])
@authentication_classes([SessionAuthentication, BasicAuthentication, TokenAuthentication])
@permission_classes([AllowAny])
def raspberryAll(request, user_tag):
    if request.user.is_authenticated:
        result = generics.get_object_or_404(Usuario, user_tag=user_tag)

        if result is not None:
            data = RaspBerry.objects.filter(user=result)
            redes = []
            for red in data:
                objeto = {
                    'id': red.id,
                    'cultivo': red.cultivo.nombre,
                    'finca': red.finca.nombre,
                }
                redes.append(objeto)

            respuesta = {
                'data': redes
            }

            return Response(respuesta, status=status.HTTP_200_OK)
    msg = {
        'error': 'Permission Denied!'
    }
    return Response(msg, status=status.HTTP_403_FORBIDDEN)

# Lee una lista de objetos (RPI) del usuario auth basado en un cultivo 
@api_view(['GET'])
@authentication_classes([SessionAuthentication, BasicAuthentication, TokenAuthentication])
@permission_classes([AllowAny])
def fincas_cultivo(request, user_tag, cultivo):
    if request.user.is_authenticated:
        result = generics.get_object_or_404(Usuario, user_tag=user_tag)
        cultivoR = generics.get_object_or_404(Cultivo, nombre=cultivo)

        if result is not None and cultivoR is not None:
            data = RaspBerry.objects.filter(user=result, cultivo=cultivoR)
            fincas = []
            for red in data:
                fincas.append(red.finca.nombre)

            respuesta = {
                'data': fincas
            }

            return Response(respuesta, status=status.HTTP_200_OK)
    msg = {
        'error': 'Permission Denied!'
    }
    return Response(msg, status=status.HTTP_403_FORBIDDEN)

# Lee, crea, actualiza y elimina un objeto (RPI) de un usuario auth que con un pk
@api_view(['GET', 'POST', 'PUT', 'DELETE'])
@authentication_classes([SessionAuthentication, BasicAuthentication, TokenAuthentication])
@permission_classes([AllowAny])
def rapsberry(request, id):

    if(request.method == 'GET' and request.user.is_authenticated):
        data = generics.get_object_or_404(RaspBerry, id=id)
        if data is not None:
            now = datetime.now()
            current_time = now.strftime("%d %b %y %H:%M:%S")
            respuesta = {
                'id_cultivo': data.cultivo.id,
                'cultivo': data.cultivo.nombre,
                'finca': data.finca.nombre,
                'date': current_time,
                'user': data.user.user_tag
            }
            return Response(respuesta, status=status.HTTP_200_OK)
        return Response({'message': 'RaspBerry no existe'}, status=status.HTTP_400_BAD_REQUEST)

    elif(request.method == 'POST' and request.user.is_authenticated):

        cultivo = request.data.get('cultivo')
        finca = request.data.get('finca')
        user_tag = request.data.get('user_tag')

        cultivoR = generics.get_object_or_404(Cultivo, nombre=cultivo)
        fincaR = generics.get_object_or_404(Finca, nombre=finca)
        usuario = generics.get_object_or_404(Usuario, user_tag=user_tag)

        data = {
            'id': id,
            'cultivo': cultivoR.id,
            'finca': fincaR.id,
            'user': usuario.id
        }

        serializer = RaspBerrySerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif(request.method == 'PUT' and request.user.is_authenticated):
        data = generics.get_object_or_404(RaspBerry, id=id)
        if data is not None:
            datos = {}
            cultivo = request.data.get('cultivo')
            finca = request.data.get('finca')

            if cultivo is not None:
                cultivoR = generics.get_object_or_404(Cultivo, nombre=cultivo)
                datos['cultivo'] = cultivoR.id

            if finca is not None:
                fincaR = generics.get_object_or_404(Finca, nombre=finca)
                datos['finca'] = fincaR.id

            serializer = RaspBerrySerializer(data, data=datos, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response({'message': 'RaspBerry no existe'}, status=status.HTTP_400_BAD_REQUEST)

    elif(request.method == 'DELETE' and request.user.is_authenticated):
        data = generics.get_object_or_404(RaspBerry, id=id)
        if data is not None:
            data.delete()
            msg = {
                'message': 'RaspBerry eliminado exitosamente'
            }
            return Response(msg, status=status.HTTP_200_OK)
        return Response({'message': 'RaspBerry no existe'}, status=status.HTTP_400_BAD_REQUEST)

    else:
        msg = {
            'error': 'Permission Denied!'
        }
        return Response(msg, status=status.HTTP_403_FORBIDDEN)
