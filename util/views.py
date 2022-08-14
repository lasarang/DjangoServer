# -*- coding: utf-8 -*-
import tempfile

from django.shortcuts import render
from django.http import HttpResponse, FileResponse
from django.template.loader import render_to_string
from cultivo.models import Cultivo
from influxdb import influxdbConnector
from users.models import Usuario
from weasyprint import HTML


from rest_framework import viewsets, permissions

from django.http import JsonResponse

from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from rest_framework import status
from rest_framework import generics

from rest_framework.decorators import api_view,authentication_classes,permission_classes
from rest_framework.authentication import SessionAuthentication, BasicAuthentication,TokenAuthentication
from rest_framework.permissions import IsAuthenticated,AllowAny,IsAdminUser
from django.contrib.auth import authenticate, login
from rest_framework.status import (
    HTTP_400_BAD_REQUEST,
    HTTP_404_NOT_FOUND,
    HTTP_200_OK
)

from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator


import urllib.request
import urllib.parse
from datetime import date, datetime
from . import constantes, utils


# Create your views here.
@api_view(['POST'])
@authentication_classes([SessionAuthentication, BasicAuthentication,TokenAuthentication])
@permission_classes([AllowAny])
def generate_pdf_general(request):
    if request.user.is_authenticated:

        planta = request.data.get("cultivo")
        user_tag = request.data.get("user_tag")
        tiempo = request.data.get("tiempo")
        now = datetime.now()
        current_time = now.strftime("%d %b %y %H:%M:%S")

        # Model data

        try:
            usuario = Usuario.objects.get(user_tag=user_tag)
        except Usuario.DoesNotExist:
            return Response({'message': 'Usuario no existe'},status=status.HTTP_404_NOT_FOUND)

        try:
            cultivo = Cultivo.objects.get(nombre=planta)
        except Cultivo.DoesNotExist:
            return Response({'message': 'Cultivo no existe'},status=status.HTTP_404_NOT_FOUND)

        print(usuario)
        print(cultivo)

        data = influxdbConnector.get_data_by_finca(constantes.TIEMPOS[tiempo]['start'], constantes.TIEMPOS[tiempo]['stop'], planta, user_tag)   

        contexto = {
            'planta': planta,
            'user_tag': user_tag,
            'fecha': current_time,
            'title': constantes.TIEMPOS[tiempo]['title'],
            'logo': constantes.LOGO,
            'foto_cultivo': constantes.LOCAL_URL_TEST + 'static/images/' + str(cultivo.imagen),
            'cultivo': cultivo,
            'usuario': usuario,
            'lista_temperatura': data['Temperatura: '],
            'lista_precipitacion': data['Precipitacion:'],
            'lista_humedad': data['Humedad: '],
            'lista_radiacion': data['Radiación Solar: '],
        }

        # Rendered
        html_string = render_to_string('reportes/reporte_general.html', context=contexto)
        html = HTML(string=html_string)

        result = html.write_pdf()

        # Creating http response
        response = HttpResponse(content_type='application/pdf;')
        response['Content-Disposition'] = 'inline; filename=list_people.pdf'
        response['Content-Transfer-Encoding'] = 'binary'
        with tempfile.NamedTemporaryFile(delete=False) as output:
            output.write(result)
            output.flush()
            output = open(output.name, 'rb')
            response.write(output.read())

        return response

    msg = {
        'error': 'Permission Denied!'
    }
    return Response(msg, status=status.HTTP_403_FORBIDDEN)

# Create your views here.
@api_view(['POST'])
@authentication_classes([SessionAuthentication, BasicAuthentication,TokenAuthentication])
@permission_classes([AllowAny])
def generate_pdf_general_2(request):
    if request.user.is_authenticated:

        planta = request.data.get("cultivo")
        user_tag = request.data.get("user_tag")

        # Model data

        usuario = generics.get_object_or_404(Usuario,user_tag=user_tag)
        cultivo = generics.get_object_or_404(Cultivo,nombre=planta)

        data = influxdbConnector.get_data_by_finca('-3h', 'now()', planta, user_tag)
        
        contexto = {
            'planta': planta,
            'user_tag': user_tag,
            'logo' : constantes.LOGO,
            'foto_cultivo' : constantes.LOCAL_URL + 'static/images/' + str(cultivo.imagen),  
            'cultivo': cultivo,
            'usuario': usuario,
            'lista_temperatura': data['Temperatura: '],
            'lista_precipitacion': data['Precipitacion:'],
            'lista_humedad': data['Humedad: '],
            'lista_radiacion': data['Radiación Solar: '],
        }

        # Rendered
        html_string = render_to_string('reportes/reporte_general.html', context=contexto)
        

        return HttpResponse(html_string)

    msg={
            'error':'Permission Denied!'
        }
    return Response(msg,status=status.HTTP_403_FORBIDDEN)


@api_view(['POST'])
@authentication_classes([SessionAuthentication, BasicAuthentication,TokenAuthentication])
@permission_classes([AllowAny])
def generate_pdf_detalle_finca(request):
    if request.user.is_authenticated:

        medida = request.data.get("medida")
        planta = request.data.get("cultivo")
        finca = request.data.get("finca")
        tiempo = request.data.get("tiempo")
        user_tag = request.data.get("user_tag")

        now = datetime.now()
        current_time = now.strftime("%d %b %y %H:%M:%S")

        # Model data

        cultivo = generics.get_object_or_404(Cultivo,nombre=planta)
        usuario = generics.get_object_or_404(Usuario,user_tag=user_tag)

        data = {}

        data['medida'] = medida
        data['finca'] = finca
        data['cultivo'] = planta
        data['tiempo'] = tiempo
        data['user_tag'] = user_tag
        data['id'] = medida
        data['modo'] = "inicio"

        url_inicio_temperatura = utils.get_url_grafana_by_time(data)
        data['modo'] = "historico"
        url_historico_temperatura = utils.get_url_grafana_by_time(data)

        data['medida'] = "precipitacion"
        data['id']  = "precipitacion"
        data['modo'] = "inicio"
        url_inicio_precipitacion = utils.get_url_grafana_by_time(data)
        data['modo'] = "historico"
        url_historico_precipitacion = utils.get_url_grafana_by_time(data)

        data['id']  = "humedad"
        data['medida'] = "humedad"
        data['modo'] = "inicio"
        url_inicio_humedad = utils.get_url_grafana_by_time(data)
        data['modo'] = "historico"
        url_historico_humedad = utils.get_url_grafana_by_time(data)
        
        data['id']  = "radiacion"
        data['medida'] = "radiacion"
        data['modo'] = "inicio"
        url_inicio_radiacion = utils.get_url_grafana_by_time(data)
        data['modo'] = "historico"
        url_historico_radiacion = utils.get_url_grafana_by_time(data)

        
        fincas = influxdbConnector.get_data_by_finca_detalle_2(constantes.TIEMPOS[tiempo]['start'], constantes.TIEMPOS[tiempo]['stop'], planta, finca, user_tag)
        nodos = influxdbConnector.get_data_by_nodo(constantes.TIEMPOS[tiempo]['start'], constantes.TIEMPOS[tiempo]['stop'], finca, planta, user_tag)

        print(fincas)
        print(nodos)
        empty_finca = [[finca, " - ", " - " , " - "]]

        lista_temperatura = []
        lista_precipitacion = []
        lista_humedad = []
        lista_radiacion = []

        lista_temperatura_nodo = []
        lista_precipitacion_nodo = []
        lista_humedad_nodo = []
        lista_radiacion_nodo = []

        there_is_data = True

        if fincas is not None and fincas:
            lista_temperatura = fincas['Temperatura: ']
            lista_precipitacion = fincas['Precipitacion:']
            lista_humedad = fincas['Humedad: ']
            lista_radiacion = fincas['Radiación Solar: ']

            lista_temperatura_nodo = nodos['Temperatura: ']
            lista_precipitacion_nodo = nodos['Precipitacion:']
            lista_humedad_nodo = nodos['Humedad: ']
            lista_radiacion_nodo = nodos['Radiación Solar: ']

            there_is_data = True
        else:
            lista_temperatura = empty_finca
            lista_precipitacion = empty_finca
            lista_humedad = empty_finca
            lista_radiacion = empty_finca

            lista_temperatura_nodo = empty_finca
            lista_precipitacion_nodo = empty_finca
            lista_humedad_nodo = empty_finca
            lista_radiacion_nodo = empty_finca

            there_is_data = False

        contexto = {
            'planta': planta,
            'user_tag': user_tag,
            'fecha': current_time,
            'finca': finca,
            'logo' : constantes.LOGO,
            'foto_cultivo' : constantes.LOCAL_URL + 'static/images/' + str(cultivo.imagen),  
            'cultivo': cultivo,
            'usuario': usuario,
            'title': constantes.TIEMPOS[tiempo]['title'],
            'subtitle': constantes.IDS[medida]['title'],
            'fincas': fincas,
            'nodos': nodos,
            'there_is_data': there_is_data,
            'lista_temperatura_finca': lista_temperatura,
            'lista_precipitacion_finca': lista_precipitacion,
            'lista_humedad_finca': lista_humedad,
            'lista_radiacion_finca': lista_radiacion,
            'lista_temperatura_nodo': lista_temperatura_nodo,
            'lista_precipitacion_nodo': lista_precipitacion_nodo,
            'lista_humedad_nodo': lista_humedad_nodo,
            'lista_radiacion_nodo': lista_radiacion_nodo,
            'url_inicio_temperatura': url_inicio_temperatura + '&width=800&height=800',
            'url_historico_temperatura': url_historico_temperatura,
            'url_inicio_precipitacion': url_inicio_precipitacion + '&width=800&height=800',
            'url_historico_precipitacion': url_historico_precipitacion,
            'url_inicio_humedad': url_inicio_humedad + '&width=800&height=800',
            'url_historico_humedad': url_historico_humedad,
            'url_inicio_radiacion': url_inicio_radiacion + '&width=800&height=800',
            'url_historico_radiacion': url_historico_radiacion,
        }

        # Rendered
        html_string = render_to_string('reportes/reporte_detalle_finca.html', context=contexto)
        html = HTML(string=html_string)

        result = html.write_pdf()

        # Creating http response
        response = HttpResponse(content_type='application/pdf;')
        response['Content-Disposition'] = 'inline; filename=list_people.pdf'
        response['Content-Transfer-Encoding'] = 'binary'
        with tempfile.NamedTemporaryFile(delete=False) as output:
            output.write(result)
            output.flush()
            output = open(output.name, 'rb')
            response.write(output.read())

        return response

    msg={
            'error':'Permission Denied!'
        }
    return Response(msg,status=status.HTTP_403_FORBIDDEN)


@api_view(['POST'])
@authentication_classes([SessionAuthentication, BasicAuthentication,TokenAuthentication])
@permission_classes([AllowAny])
def generate_pdf_detalle_sensor(request):
    if request.user.is_authenticated:

        medida = request.data.get("medida")
        planta = request.data.get("cultivo")
        finca = request.data.get("finca")
        tiempo = request.data.get("tiempo")
        nodo = request.data.get("sensor")
        user_tag = request.data.get("user_tag")

        now = datetime.now()
        current_time = now.strftime("%d %b %y %H:%M:%S")

        # Model data

        cultivo = generics.get_object_or_404(Cultivo,nombre=planta)
        usuario = generics.get_object_or_404(Usuario,user_tag=user_tag)

        data = {}

        data['medida'] = "temperatura"
        data['finca'] = finca
        data['cultivo'] = planta
        data['tiempo'] = tiempo
        data['user_tag'] = user_tag
        data['id'] = medida
        data['modo'] = "sensor_inicio"

        url_inicio_temperatura = utils.get_url_grafana_by_time_sensor(data, nodo)
        data['modo'] = "sensor_historico"
        url_historico_temperatura = utils.get_url_grafana_by_time_sensor(data, nodo)

        data['medida'] = "precipitacion"
        data['id']  = "precipitacion"
        data['modo'] = "sensor_inicio"
        url_inicio_precipitacion = utils.get_url_grafana_by_time_sensor(data, nodo)
        data['modo'] = "sensor_historico"
        url_historico_precipitacion = utils.get_url_grafana_by_time_sensor(data, nodo)

        data['id']  = "humedad"
        data['medida'] = "humedad"
        data['modo'] = "sensor_inicio"
        url_inicio_humedad = utils.get_url_grafana_by_time_sensor(data, nodo)
        data['modo'] = "sensor_historico"
        url_historico_humedad = utils.get_url_grafana_by_time_sensor(data, nodo)
        
        data['id']  = "radiacion"
        data['medida'] = "radiacion"
        data['modo'] = "sensor_inicio"
        url_inicio_radiacion = utils.get_url_grafana_by_time_sensor(data, nodo)
        data['modo'] = "sensor_historico"
        url_historico_radiacion = utils.get_url_grafana_by_time_sensor(data, nodo)

        nodos = influxdbConnector.get_data_by_nodo_detalle_2(constantes.TIEMPOS[tiempo]['start'], constantes.TIEMPOS[tiempo]['stop'], finca, planta, user_tag, nodo)
        empty_nodo = [[nodo, " - ", " - " , " - "]]

        lista_temperatura_nodo = []
        lista_precipitacion_nodo = []
        lista_humedad_nodo = []
        lista_radiacion_nodo = []

        if nodos is not None and nodos:
            lista_temperatura_nodo = nodos['Temperatura: ']
            lista_precipitacion_nodo = nodos['Precipitacion:']
            lista_humedad_nodo = nodos['Humedad: ']
            lista_radiacion_nodo = nodos['Radiación Solar: ']
        else:
            lista_temperatura_nodo = empty_nodo
            lista_precipitacion_nodo = empty_nodo
            lista_humedad_nodo = empty_nodo
            lista_radiacion_nodo = empty_nodo

        contexto = {
            'planta': planta,
            'user_tag': user_tag,
            'fecha': current_time,
            'finca': finca,
            'logo' : constantes.LOGO,
            'foto_cultivo' : constantes.LOCAL_URL + 'static/images/' + str(cultivo.imagen),  
            'cultivo': cultivo,
            'usuario': usuario,
            'title': constantes.TIEMPOS[tiempo]['title'],
            'subtitle': nodo,
            'nodos': nodos,
            'lista_temperatura': lista_temperatura_nodo,
            'lista_precipitacion': lista_precipitacion_nodo,
            'lista_humedad': lista_humedad_nodo,
            'lista_radiacion': lista_radiacion_nodo,
            'url_inicio_temperatura': url_inicio_temperatura + '&width=800&height=800',
            'url_historico_temperatura': url_historico_temperatura,
            'url_inicio_precipitacion': url_inicio_precipitacion + '&width=800&height=800',
            'url_historico_precipitacion': url_historico_precipitacion,
            'url_inicio_humedad': url_inicio_humedad + '&width=800&height=800',
            'url_historico_humedad': url_historico_humedad,
            'url_inicio_radiacion': url_inicio_radiacion + '&width=800&height=800',
            'url_historico_radiacion': url_historico_radiacion,
        }
        

        # Rendered
        html_string = render_to_string('reportes/reporte_detalle_nodo.html', context=contexto)
        html = HTML(string=html_string)

        result = html.write_pdf()

        # Creating http response
        response = HttpResponse(content_type='application/pdf;')
        response['Content-Disposition'] = 'inline; filename=list_people.pdf'
        response['Content-Transfer-Encoding'] = 'binary'
        with tempfile.NamedTemporaryFile(delete=False) as output:
            output.write(result)
            output.flush()
            output = open(output.name, 'rb')
            response.write(output.read())

        return response

    msg={
            'error':'Permission Denied!'
        }
    return Response(msg,status=status.HTTP_403_FORBIDDEN)