import tempfile
from django.shortcuts import render
from django.http import HttpResponse
from django.template.loader import render_to_string
from cultivo.models import Cultivo, ListaCultivo
from cultivo.serializers import ListaCultivoNewSerializer
from influxdb import influxdbConnector
from users.models import Usuario
from finca.models import Finca
from weasyprint import HTML
from rest_framework.response import Response
from rest_framework import status
from rest_framework import generics
from rest_framework.decorators import api_view,authentication_classes,permission_classes
from rest_framework.authentication import SessionAuthentication, BasicAuthentication,TokenAuthentication
from rest_framework.permissions import AllowAny
from datetime import datetime
from . import constantes, utils
from random import randint


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


#Reporte General Mejorado
@api_view(['POST'])
@authentication_classes([SessionAuthentication, BasicAuthentication,TokenAuthentication])
@permission_classes([AllowAny])
def generate_pdf_general_final(request):
    if request.user.is_authenticated:
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
            cultivosXFinca = ListaCultivo.objects.filter(id_user=usuario)
        except Usuario.DoesNotExist:
            return Response({'message': 'No existe un cultivo registrado en esta finca'},status=status.HTTP_404_NOT_FOUND)

        medicionesInflux = influxdbConnector.get_data_by_finca_final(constantes.TIEMPOS[tiempo]['start'], constantes.TIEMPOS[tiempo]['stop'], user_tag)   


        dataReporteFinal = ListaCultivoNewSerializer(cultivosXFinca, many=True).data

        bodyReporte = []

        for dataXListaCultivo in dataReporteFinal:

            print('Temperatura' in medicionesInflux)

            #Verifica si Influx tiene data de temperatura
            if 'Temperatura' in medicionesInflux:
                for medicionInfluxT in medicionesInflux['Temperatura']:
                    if medicionInfluxT[0] == dataXListaCultivo['finca']['nombre']:
                        dataXListaCultivo['minimo_temperatura_medido'] = medicionInfluxT[1] +' °C'
                        dataXListaCultivo['promedio_temperatura_medido'] = medicionInfluxT[2] +' °C'
                        dataXListaCultivo['maximo_temperatura_medido'] = medicionInfluxT[3] +' °C'
            else:
                dataXListaCultivo['minimo_temperatura_medido'] = '-'
                dataXListaCultivo['promedio_temperatura_medido'] = '-'
                dataXListaCultivo['maximo_temperatura_medido'] = '-'
            
            #Verifica si Influx tiene data de humedad
            if 'Humedad' in medicionesInflux:
                for medicionInfluxH in medicionesInflux['Humedad']:
                    if medicionInfluxH[0] == dataXListaCultivo['finca']['nombre']:
                        dataXListaCultivo['minimo_humedad_medido'] = medicionInfluxH[1] +' %H'
                        dataXListaCultivo['promedio_humedad_medido'] = medicionInfluxH[2] +' %H'
                        dataXListaCultivo['maximo_humedad_medido'] = medicionInfluxH[3] +' %H'
            else:
                dataXListaCultivo['minimo_humedad_medido'] = '-'
                dataXListaCultivo['promedio_humedad_medido'] = '-'
                dataXListaCultivo['maximo_humedad_medido'] = '-'
            
            #Verifica si Influx tiene data de precipitacion
            if 'Precipitacion' in medicionesInflux:
                for medicionInfluxP in medicionesInflux['Precipitacion']:
                    if medicionInfluxP[0] == dataXListaCultivo['finca']['nombre']:
                        dataXListaCultivo['minimo_precipitacion_medido'] = medicionInfluxP[1] +' ml'
                        dataXListaCultivo['promedio_precipitacion_medido'] = medicionInfluxP[2] +' ml'
                        dataXListaCultivo['maximo_precipitacion_medido'] = medicionInfluxP[3] +' ml'
            else:
                dataXListaCultivo['minimo_precipitacion_medido'] = '-'
                dataXListaCultivo['promedio_precipitacion_medido'] = '-'
                dataXListaCultivo['maximo_precipitacion_medido'] = '-'
            
            #Verifica si Influx tiene data de radiacion solar
            if 'Radiación Solar' in medicionesInflux:
                for medicionInfluxRS in medicionesInflux['Radiación Solar']:
                    if medicionInfluxRS[0] == dataXListaCultivo['finca']['nombre']:
                        dataXListaCultivo['minimo_radiacion_medido'] = medicionInfluxRS[1] +' lux'
                        dataXListaCultivo['promedio_radiacion_medido'] = medicionInfluxRS[2] +' lux'
                        dataXListaCultivo['maximo_radiacion_medido'] = medicionInfluxRS[3] +' lux'
            else:
                dataXListaCultivo['minimo_radiacion_medido'] = '-'
                dataXListaCultivo['promedio_radiacion_medido'] = '-'
                dataXListaCultivo['maximo_radiacion_medido'] = '-'
            
            
            dataXListaCultivo['nombre_cultivo'] = dataXListaCultivo['cultivo']['nombre']
            dataXListaCultivo['nombre_finca'] = dataXListaCultivo['finca']['nombre']
            del dataXListaCultivo['cultivo']
            del dataXListaCultivo['finca']
            del dataXListaCultivo['user']
            bodyReporte.append(dict(dataXListaCultivo))
        
        contexto = {
            'user_tag': user_tag,
            'fecha': current_time,
            'title': constantes.TIEMPOS[tiempo]['title'],
            'logo': constantes.LOGO,
            'bodyReporte': bodyReporte,
            'usuario': usuario,
        }

        # Rendered
        html_string = render_to_string('reportes/reporte_general_final.html', context=contexto)
        html = HTML(string=html_string)

        result = html.write_pdf()

        # Creating http response
        reporteCode = str(randint(0, 1000))+""+str(randint(0, 1000))+""+str(randint(0, 1000))

        response = HttpResponse(content_type='application/pdf;')
        response['Content-Disposition'] = 'inline; filename=reporte_general_'+reporteCode+'.pdf'
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