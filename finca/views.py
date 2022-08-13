from rest_framework import viewsets, permissions
from rest_framework.response import Response
from rest_framework import status
from rest_framework import generics
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.authentication import SessionAuthentication, BasicAuthentication, TokenAuthentication
from rest_framework.permissions import AllowAny
from users.models import Usuario
from .models import Finca
from .serializers import FincaSerializer
import base64
from django.core.files.base import ContentFile
from random import randint


class FincaViewSet(viewsets.ModelViewSet):
    queryset = Finca.objects.all()
    permission_classes = [permissions.AllowAny]
    serializer_class = FincaSerializer

# Deberia Leer las fincas del usuario auth sin usar Serializer
@api_view(['GET'])
@authentication_classes([SessionAuthentication, BasicAuthentication, TokenAuthentication])
@permission_classes([AllowAny])
def get_fincas(request):
    if request.user.is_authenticated:
        user_tag = request.data.get("user_tag")
        result = generics.get_object_or_404(Usuario, user_tag=user_tag)

        if result is not None:
            fincas = Finca.objects.filter(user=result)
            lista = []
            if len(fincas) > 0:
                for finca in fincas:
                    lista.append(finca.nombre)

                message = {
                    'fincas': lista
                }
                return Response(message, status=status.HTTP_200_OK)
            return Response({'message': 'Usuario no tiene fincas'}, status=status.HTTP_400_BAD_REQUEST)
        return Response({'message': 'Error al obtener las fincas'}, status=status.HTTP_400_BAD_REQUEST)

    msg = {
        'error': 'Permission Denied!'
    }
    return Response(msg, status=status.HTTP_403_FORBIDDEN)

# Deberia Leer las fincas del usuario auth usando Serializer
@api_view(['GET'])
@authentication_classes([SessionAuthentication, BasicAuthentication, TokenAuthentication])
@permission_classes([AllowAny])
def get_fincas_2(request):
    if request.user.is_authenticated:
        user_tag = request.data.get("user_tag")
        user_type = request.data.get("user_type")

        if user_type == 1: 
            result = Finca.objects.all()

            if result is not None:
                fincas = Finca.objects.filter(user=result)

                if len(fincas) > 0:
                    serializer = FincaSerializer(fincas, many=True)
                    return Response(serializer.data, status=status.HTTP_200_OK)
                return Response({'message': 'Usuario no tiene fincas'}, status=status.HTTP_400_BAD_REQUEST)
            return Response({'message': 'Error al obtener las fincas'}, status=status.HTTP_400_BAD_REQUEST)

        elif user_type == 2:
            result = generics.get_object_or_404(Usuario, user_tag=user_tag)

            if result is not None:
                fincas = Finca.objects.filter(user=result)

                if len(fincas) > 0:
                    serializer = FincaSerializer(fincas, many=True)
                    return Response(serializer.data, status=status.HTTP_200_OK)
                return Response({'message': 'Usuario no tiene fincas'}, status=status.HTTP_400_BAD_REQUEST)
            return Response({'message': 'Error al obtener las fincas'}, status=status.HTTP_400_BAD_REQUEST)    

    msg = {
        'error': 'Permission Denied!'
    }
    return Response(msg, status=status.HTTP_403_FORBIDDEN)

# Lee, crea, actualiza y elimina una finca del usuario auth con una pk
@api_view(['GET', 'POST', 'PUT', 'DELETE'])
@authentication_classes([SessionAuthentication, BasicAuthentication, TokenAuthentication])
@permission_classes([AllowAny])
def finca(request, pk):

    if request.method == 'GET' and request.user.is_authenticated:
        data = generics.get_object_or_404(Finca, id=pk)
        if data is not None:
            serializer = FincaSerializer(data, many=False)
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response({'message': 'Configuracion no existe'}, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'POST' and request.user.is_authenticated:
        user_tag = request.data.get("user_tag")
        nombre = request.data.get("nombre")

        usuario = generics.get_object_or_404(Usuario, user_tag=user_tag)

        data = {
            "nombre": nombre,
            "user": usuario.id,
        }

        serializer = FincaSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'PUT' and request.user.is_authenticated:
        data = generics.get_object_or_404(Finca, id=pk)
        if data is not None:
            serializer = FincaSerializer(data, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response({'message': 'Configuracion no existe'}, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE' and request.user.is_authenticated:
        data = generics.get_object_or_404(Finca, id=pk)
        if data is not None:
            data.delete()
            msg = {
                'message': 'Configuracion eliminado exitosamente'
            }
            return Response(msg, status=status.HTTP_200_OK)
        return Response({'message': 'Configuracion no existe'}, status=status.HTTP_400_BAD_REQUEST)

    else:
        msg = {
            'error': 'Permission Denied!'
        }
        return Response(msg, status=status.HTTP_403_FORBIDDEN)



#NUEVO

# Obtener todas las fincas
@api_view(['GET'])
@authentication_classes([SessionAuthentication, BasicAuthentication, TokenAuthentication])
@permission_classes([AllowAny])
def fincas(request):
    if request.user.is_authenticated:
        data = Finca.objects.all()
        serializer = FincaSerializer(data, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    msg = {
        'error': 'Permission Denied!'
    }
    return Response(msg, status=status.HTTP_403_FORBIDDEN)

# Crear un Finca
@api_view(['POST'])
@authentication_classes([SessionAuthentication, BasicAuthentication, TokenAuthentication])
@permission_classes([AllowAny])
def fincasCrear(request):

    if request.user.is_authenticated:

        fincaCode = str(randint(0, 1000))+""+str(randint(0, 1000))+""+str(randint(0, 1000))
        format, imgstr = request.data['imagen'].split(';base64,') 
        ext = format.split('/')[-1] 
        data = ContentFile(base64.b64decode(imgstr), name='finca_' + fincaCode+'.' + ext)
        request.data._mutable = True
        request.data['imagen'] = data
        request.data._mutable = False

        serializer = FincaSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    msg = {
        'error': 'Permission Denied!'
    }
    return Response(msg, status=status.HTTP_403_FORBIDDEN)

# Obtener, Actualizar o Eliminar un Finca por pk
@api_view(['GET', 'PUT', 'DELETE'])
@authentication_classes([SessionAuthentication, BasicAuthentication, TokenAuthentication])
@permission_classes([AllowAny])
def finca_new(request, pk):

    #Valida que exista el Finca (aplica para métodos que no sean POST)
    if request.user.is_authenticated:
        try:
            data = Finca.objects.get(pk=pk)
        except Finca.DoesNotExist:
            return Response({'message': 'Finca no existe'},status=status.HTTP_404_NOT_FOUND)

    #Obtiene Finca por Pk
    if request.method == 'GET' and request.user.is_authenticated:
        serializer = FincaSerializer(data, many=False)
        return Response(serializer.data, status=status.HTTP_200_OK)

    #Actualiza Finca por pk, se puede actualizar por partes
    elif request.method == 'PUT' and request.user.is_authenticated:
        if "imagen" in request.data:
            fincaCode = str(randint(0, 1000))+""+str(randint(0, 1000))+""+str(randint(0, 1000))
            format, imgstr = request.data['imagen'].split(';base64,') 
            ext = format.split('/')[-1] 
            request.data._mutable = True
            request.data['imagen'] = ContentFile(base64.b64decode(imgstr), name='finca_' + fincaCode+'.' + ext)
            request.data._mutable = False
        serializer = FincaSerializer(data, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    #Elimina Finca por pk (recomendable no usar)
    elif request.method == 'DELETE' and request.user.is_authenticated:
        data.delete()
        return Response({'message': 'Finca eliminada con éxito'}, status=status.HTTP_200_OK)

    else:
        msg = {
            'error': 'Permission Denied!'
        }
        return Response(msg, status=status.HTTP_403_FORBIDDEN)