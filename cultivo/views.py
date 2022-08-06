from finca.models import Finca
from finca.serializers import FincaSerializer
from users.models import Usuario
from django.shortcuts import render
from rest_framework import viewsets, permissions

from .models import Cultivo, ListaCultivo
from .serializers import CultivoSerializer, ListaCultivoSerializer, ListaCultivoNewSerializer

from django.http import JsonResponse
from rest_framework.response import Response

from rest_framework import status
from rest_framework import generics

from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.authentication import SessionAuthentication, BasicAuthentication, TokenAuthentication
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAdminUser
from rest_framework.status import (
    HTTP_400_BAD_REQUEST,
    HTTP_404_NOT_FOUND,
    HTTP_200_OK
)

from rest_framework.decorators import api_view

import base64
from django.core.files.base import ContentFile


# generate random integer values
from random import seed
from random import randint

class CultivoViewSet(viewsets.ModelViewSet):
    queryset = Cultivo.objects.all()
    permission_classes = [permissions.AllowAny]
    serializer_class = CultivoSerializer


class ListaCultivoViewSet(viewsets.ModelViewSet):
    queryset = ListaCultivo.objects.all()
    permission_classes = [permissions.AllowAny]
    serializer_class = ListaCultivoSerializer


# Obtener todos los cultivos
@api_view(['GET'])
@authentication_classes([SessionAuthentication, BasicAuthentication, TokenAuthentication])
@permission_classes([AllowAny])
def crops(request):

    print(request.user.is_authenticated)

    if request.user.is_authenticated:
        data = Cultivo.objects.all()
        serializer = CultivoSerializer(data, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    msg = {
        'error': 'Permission Denied!'
    }
    return Response(msg, status=status.HTTP_403_FORBIDDEN)

# Crear un cultivo
@api_view(['POST'])
@authentication_classes([SessionAuthentication, BasicAuthentication, TokenAuthentication])
@permission_classes([AllowAny])
def cultivosCrear(request):

    if request.user.is_authenticated:

        cultivoCode = str(randint(0, 1000))+""+str(randint(0, 1000))+""+str(randint(0, 1000))
        format, imgstr = request.data['imagen'].split(';base64,') 
        ext = format.split('/')[-1] 
        data = ContentFile(base64.b64decode(imgstr), name='cultivo_' + cultivoCode+'.' + ext)
        request.data._mutable = True
        request.data['imagen'] = data
        request.data._mutable = False


        serializer = CultivoSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    msg = {
        'error': 'Permission Denied!'
    }
    return Response(msg, status=status.HTTP_403_FORBIDDEN)

# Obtener, Actualizar o Eliminar un cultivo por pk
@api_view(['GET', 'PUT', 'DELETE'])
@authentication_classes([SessionAuthentication, BasicAuthentication, TokenAuthentication])
@permission_classes([AllowAny])
def cultivo(request, pk):

    #Valida que exista el cultivo (aplica para métodos que no sean POST)
    if request.user.is_authenticated:
        try:
            data = Cultivo.objects.get(pk=pk)
        except Cultivo.DoesNotExist:
            return Response({'message': 'Cultivo no existe'},status=status.HTTP_404_NOT_FOUND)

    #Obtiene Cultivo por Pk
    if request.method == 'GET' and request.user.is_authenticated:
        serializer = CultivoSerializer(data, many=False)
        return Response(serializer.data, status=status.HTTP_200_OK)

    #Actualiza Cultivo por pk, se puede actualizar por partes
    elif request.method == 'PUT' and request.user.is_authenticated:
        if "imagen" in request.data:
            cultivoCode = str(randint(0, 1000))+""+str(randint(0, 1000))+""+str(randint(0, 1000))
            format, imgstr = request.data['imagen'].split(';base64,') 
            ext = format.split('/')[-1] 
            request.data._mutable = True
            request.data['imagen'] = ContentFile(base64.b64decode(imgstr), name='cultivo_' + cultivoCode+'.' + ext)
            request.data._mutable = False

        serializer = CultivoSerializer(data, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    #Elimina Cultivo por pk (recomendable no usar)
    elif request.method == 'DELETE' and request.user.is_authenticated:
        data.delete()
        return Response({'message': 'Cultivo eliminado con éxito'}, status=status.HTTP_200_OK)

    else:
        msg = {
            'error': 'Permission Denied!'
        }
        return Response(msg, status=status.HTTP_403_FORBIDDEN)


# Deberia ser leer los cutlivos del usuario authenticado
@api_view(['GET'])
@authentication_classes([SessionAuthentication, BasicAuthentication, TokenAuthentication])
@permission_classes([AllowAny])
def cultivos_user(request):
    if request.user.is_authenticated:
        user_tag = request.data.get("user_tag")

        usuario = generics.get_object_or_404(Usuario, user_tag=user_tag)

        if usuario is not None:
            distintos = ListaCultivo.objects.filter(
                id_user=usuario).values('id_cultivo').distinct()
            cultivos = []

            for cultivo in distintos:
                data = generics.get_object_or_404(
                    Cultivo, id=cultivo['id_cultivo'])
                cultivos.append(data)

            print(cultivos)
            serializer = CultivoSerializer(cultivos, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response({'message': 'Error al obtener los cultivos'}, status=status.HTTP_400_BAD_REQUEST)

    msg = {
        'error': 'Permission Denied!'
    }
    return Response(msg, status=status.HTTP_403_FORBIDDEN)



# Deberia ser leer la lista de fincas que tiene un usuario usando su auth y un cultivo 
@api_view(['GET'])
@authentication_classes([SessionAuthentication, BasicAuthentication, TokenAuthentication])
@permission_classes([AllowAny])
def fincas_cultivo_user(request):
    if request.user.is_authenticated:
        user_tag = request.data.get("user_tag")
        planta = request.data.get("cultivo")
        print(user_tag, planta)

        cultivo = generics.get_object_or_404(Cultivo, nombre=planta)
        usuario = generics.get_object_or_404(Usuario, user_tag=user_tag)

        fincas = ListaCultivo.objects.filter(
            id_cultivo=cultivo, id_user=usuario).values('id_finca').distinct()

        if len(fincas) > 0:
            lista = []
            for finca in fincas:
                data = generics.get_object_or_404(Finca, id=finca['id_finca'])
                lista.append(data.nombre)

            message = {
                'fincas': lista
            }
            return Response(message, status=status.HTTP_200_OK)
        return Response({'message': 'Usuario no tiene fincas'}, status=status.HTTP_400_BAD_REQUEST)

    msg = {
        'error': 'Permission Denied!'
    }
    return Response(msg, status=status.HTTP_403_FORBIDDEN)





# Todo Nuevo

# Obtener los cultivos de un usuario por medio del user_tag
@api_view(['GET'])
@authentication_classes([SessionAuthentication, BasicAuthentication, TokenAuthentication])
@permission_classes([AllowAny])
def cultivos_user_new(request):
    if request.user.is_authenticated:

        #Obtener params de un url
        user_tag = request.GET["user_tag"]

        try:
            usuario = Usuario.objects.get(user_tag=user_tag)
        except Usuario.DoesNotExist:
            return Response({'message': 'El Usuario no existe'},status=status.HTTP_404_NOT_FOUND)

        distintos = ListaCultivo.objects.filter(id_user=usuario).values('id_cultivo').distinct()
        cultivos = []

        for cultivo in distintos:
            #data = generics.get_object_or_404(Cultivo, id=cultivo['id_cultivo'])
            try:
                data = Cultivo.objects.get(id=cultivo['id_cultivo'])
            except Cultivo.DoesNotExist:
                return Response({'message': 'El cultivo '+cultivo['id_cultivo']+' no existe'},status=status.HTTP_404_NOT_FOUND)
            
            cultivos.append(data)
        print(cultivos)
        serializer = CultivoSerializer(cultivos, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    msg = {
        'error': 'Permission Denied!'
    }
    return Response(msg, status=status.HTTP_403_FORBIDDEN)



# Obtener las fincas de un usuario por medio del user_tag
@api_view(['GET'])
@authentication_classes([SessionAuthentication, BasicAuthentication, TokenAuthentication])
@permission_classes([AllowAny])
def fincas_user_new(request):
    if request.user.is_authenticated:
        #Obtener params de un url
        user_tag = request.GET["user_tag"]

        try:
            usuario = Usuario.objects.get(user_tag=user_tag)
        except Usuario.DoesNotExist:
            return Response({'message': 'El Usuario no existe'},status=status.HTTP_404_NOT_FOUND)

        distintos = ListaCultivo.objects.filter(id_user=usuario).values('id_finca').distinct()
        fincas = []

        for cultivo in distintos:
            try:
                data = Finca.objects.get(id=cultivo['id_finca'])
            except Finca.DoesNotExist:
                return Response({'message': 'La finca '+cultivo['id_finca']+' no existe'},status=status.HTTP_404_NOT_FOUND)
            
            fincas.append(data)
        print(fincas)
        serializer = FincaSerializer(fincas, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    msg = {
        'error': 'Permission Denied!'
    }
    return Response(msg, status=status.HTTP_403_FORBIDDEN)



# Obtener finca por usuario y que cultiva cada finca por user_tag
@api_view(['GET'])
@authentication_classes([SessionAuthentication, BasicAuthentication, TokenAuthentication])
@permission_classes([AllowAny])
def finca_cultivo_user_new(request):
    if request.user.is_authenticated:
        #Obtener params de un url
        user_tag = request.GET["user_tag"]

        try:
            usuario = Usuario.objects.get(user_tag=user_tag)
        except Usuario.DoesNotExist:
            return Response({'message': 'El Usuario no existe'},status=status.HTTP_404_NOT_FOUND)


        dataListaCultivo = ListaCultivo.objects.filter(id_user=usuario)
        serializer = ListaCultivoNewSerializer(dataListaCultivo, many=True)
        
        return Response(serializer.data, status=status.HTTP_200_OK)
    msg = {
        'error': 'Permission Denied!'
    }
    return Response(msg, status=status.HTTP_403_FORBIDDEN)



# Crear nueva relación usuario - finca - cultivo
@api_view(['POST'])
@authentication_classes([SessionAuthentication, BasicAuthentication, TokenAuthentication])
@permission_classes([AllowAny])
def farms_crop_user_create(request):
    if request.user.is_authenticated:

        id_user = request.data.get("id_user")
        id_finca = request.data.get("id_finca")
        id_cultivo = request.data.get("id_cultivo")

        try:
            usuario = Usuario.objects.get(id=id_user)
        except Usuario.DoesNotExist:
            return Response({'message': 'El Usuario no existe'},status=status.HTTP_404_NOT_FOUND)

        try:
            cultivo = Cultivo.objects.get(id=id_cultivo)
        except Cultivo.DoesNotExist:
            return Response({'message': 'El Cultivo no existe'},status=status.HTTP_404_NOT_FOUND)

        try:
            finca = Finca.objects.get(id=id_finca)
        except Finca.DoesNotExist:
            return Response({'message': 'La Finca no existe'},status=status.HTTP_404_NOT_FOUND)


        serializer = ListaCultivoSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            dataResp = ListaCultivo.objects.get(pk=serializer.data["id"])
            serializer = ListaCultivoNewSerializer(dataResp, many=False)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    msg = {
        'error': 'Permission Denied!'
    }
    return Response(msg, status=status.HTTP_403_FORBIDDEN)


# Obtener registro de relación finca - cultivo - usuario, si se envia el parametro user_tag, se trae solo las del usuario
@api_view(['GET'])
@authentication_classes([SessionAuthentication, BasicAuthentication, TokenAuthentication])
@permission_classes([AllowAny])
def farms_crops_users(request):
    
    if len(request.GET.dict()) == 0:

        if request.user.is_authenticated:
            data = ListaCultivo.objects.all()
            serializer = ListaCultivoNewSerializer(data, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)

        msg = {
            'error': 'Permission Denied!'
        }
        return Response(msg, status=status.HTTP_403_FORBIDDEN)

    else:
        if request.user.is_authenticated:

            user_tag = request.GET["user_tag"]

            try:
                usuario = Usuario.objects.get(user_tag=user_tag)
            except Usuario.DoesNotExist:
                return Response({'message': 'El Usuario no existe'},status=status.HTTP_404_NOT_FOUND)


            dataListaCultivo = ListaCultivo.objects.filter(id_user=usuario)
            serializer = ListaCultivoNewSerializer(dataListaCultivo, many=True)
            
            return Response(serializer.data, status=status.HTTP_200_OK)
        msg = {
            'error': 'Permission Denied!'
        }
        return Response(msg, status=status.HTTP_403_FORBIDDEN)

# Obtener, Actualizar y Eliminar relación usuario - finca - cultivo
@api_view(['GET', 'PUT', 'DELETE'])
@authentication_classes([SessionAuthentication, BasicAuthentication, TokenAuthentication])
@permission_classes([AllowAny])
def finca_cultivo_user(request, pk):

    #Valida que exista la relación
    if request.user.is_authenticated:
        try:
            data = ListaCultivo.objects.get(pk=pk)
        except ListaCultivo.DoesNotExist:
            return Response({'message': 'El objeto que relaciona al Usuario, Cultivo y Finca no existe'},status=status.HTTP_404_NOT_FOUND)

    #Obtiene relación Cultivo - Finca - Usuario por Pk
    if request.method == 'GET' and request.user.is_authenticated:
        serializer = ListaCultivoNewSerializer(data, many=False)
        return Response(serializer.data, status=status.HTTP_200_OK)

    #Actualiza relación Cultivo - Finca - Usuario por pk, se puede actualizar por partes
    elif request.method == 'PUT' and request.user.is_authenticated:
        serializer = ListaCultivoSerializer(data, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            serializerResp = ListaCultivoNewSerializer(data, many=False)
            return Response(serializerResp.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    #Elimina relación Cultivo - Finca - Usuario por pk (recomendable no usar)
    elif request.method == 'DELETE' and request.user.is_authenticated:
        data.delete()
        return Response({'message': 'Relación Usuario, Cultivo y Finca eliminada con éxito'}, status=status.HTTP_200_OK)

    else:
        msg = {
            'error': 'Permission Denied!'
        }
        return Response(msg, status=status.HTTP_403_FORBIDDEN)