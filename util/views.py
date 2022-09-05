import tempfile
from django.shortcuts import render
from django.http import HttpResponse
from django.template.loader import render_to_string
from cultivo.models import Cultivo, ListaCultivo
from cultivo.serializers import ListaCultivoNewSerializer
from influxdb import influxdbConnector
from notificaciones.models import NotificacionRespaldo
from notificaciones.serializers import NotificacionRespaldoSerializer
from users.models import Usuario
from finca.models import Finca
from weasyprint import HTML
from rest_framework.response import Response
from rest_framework import status
from rest_framework import generics
from rest_framework.decorators import api_view,authentication_classes,permission_classes
from rest_framework.authentication import SessionAuthentication, BasicAuthentication,TokenAuthentication
from rest_framework.permissions import AllowAny
from datetime import datetime, timedelta, date
from . import constantes, utils
from random import randint

LISTA_DIAS_DICT = {0:'LUNES',1:'MARTES',2:'MIÉRCOLES',3:'JUEVES',4:'VIERNES',5:'SÁBADO',6:'DOMINGO'}

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






#=====================================================================================#
#========================NUEVOS REPORTES==============================================#
#=====================================================================================#

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

        try:
            usuario = Usuario.objects.get(user_tag=user_tag)
        except Usuario.DoesNotExist:
            return Response({'message': 'Usuario no existe'},status=status.HTTP_404_NOT_FOUND)

        try:
            cultivosXFinca = ListaCultivo.objects.filter(id_user=usuario)
        except ListaCultivo.DoesNotExist:
            return Response({'message': 'No existe un cultivo registrado en esta finca'},status=status.HTTP_404_NOT_FOUND)

        medicionesInflux = influxdbConnector.obtenerDataFincaFinal(constantes.TIEMPOS[tiempo]['start'], constantes.TIEMPOS[tiempo]['stop'], user_tag)   


        dataReporteFinal = ListaCultivoNewSerializer(cultivosXFinca, many=True).data

        bodyReporte = []

        for dataXListaCultivo in dataReporteFinal:

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



#Reporte Por Fincas Mejorado
@api_view(['POST'])
@authentication_classes([SessionAuthentication, BasicAuthentication,TokenAuthentication])
@permission_classes([AllowAny])
def generate_pdf_detalle_finca_final(request):
    if request.user.is_authenticated:

        medida = request.data.get("medida")
        finca = request.data.get("finca")
        tiempo = request.data.get("tiempo")
        user_tag = request.data.get("user_tag")

        now = datetime.now()
        current_time = now.strftime("%d %b %y %H:%M:%S")

        try:
            usuario = Usuario.objects.get(user_tag=user_tag)
        except Usuario.DoesNotExist:
            return Response({'message': 'Usuario no existe'},status=status.HTTP_404_NOT_FOUND)

        try:
            finca_data = Finca.objects.get(nombre=finca)
        except Finca.DoesNotExist:
            return Response({'message': 'Finca no existe'},status=status.HTTP_404_NOT_FOUND)

        try:
            cultivosXFinca = ListaCultivo.objects.filter(id_user=usuario).filter(id_finca=finca_data)
        except ListaCultivo.DoesNotExist:
            return Response({'message': 'No existe un cultivo registrado en esta finca'},status=status.HTTP_404_NOT_FOUND)


        dataReporteFinal = ListaCultivoNewSerializer(cultivosXFinca, many=True).data

        data = {}
        bodyReporte = []

        data['finca'] = finca
        data['tiempo'] = tiempo
        data['user_tag'] = user_tag

        medicionesInfluxFincas = influxdbConnector.obtenerDataFincaDetalleFinal(constantes.TIEMPOS[tiempo]['start'], constantes.TIEMPOS[tiempo]['stop'], finca, user_tag)
        medicionesInfluxNodos = influxdbConnector.obtenerDataNodoFinca(constantes.TIEMPOS[tiempo]['start'], constantes.TIEMPOS[tiempo]['stop'], finca, user_tag)

        for dataXListaCultivo in dataReporteFinal:

            if medida == 'temperatura':
                dataXListaCultivo['data_nodos'] = []
                dataXListaCultivo['medida_simbolo'] = '°C'

                data['id']  = "temperatura"
                data['medida'] = "temperatura"
                data['modo'] = "inicio"
                dataXListaCultivo['url_inicio'] = utils.get_url_grafana_by_time(data)+'&width=600&height=600'
                data['modo'] = "historico"
                dataXListaCultivo['url_historico'] = utils.get_url_grafana_by_time(data)
                #Verifica si Influx de Finca tiene data de temperatura
                if 'Temperatura' in medicionesInfluxFincas:
                    for medicionInfluxTF in medicionesInfluxFincas['Temperatura']:
                        if medicionInfluxTF[0] == dataXListaCultivo['finca']['nombre']:
                            dataXListaCultivo['minimo_medido'] = medicionInfluxTF[1]
                            dataXListaCultivo['promedio_medido'] = medicionInfluxTF[2]
                            dataXListaCultivo['maximo_medido'] = medicionInfluxTF[3]
                else:
                    dataXListaCultivo['minimo_medido'] = '-'
                    dataXListaCultivo['promedio_medido'] = '-'
                    dataXListaCultivo['maximo_medido'] = '-'

                #Verifica si Influx de Nodos tiene data de temperatura
                if 'Temperatura' in medicionesInfluxNodos:
                    for medicionInfluxTN in medicionesInfluxNodos['Temperatura']:
                        dataXListaCultivo['data_nodos'].append(medicionInfluxTN)
                else:
                    dataXListaCultivo['data_nodos'].append(["-","-","-","-"])

        
            elif medida == 'humedad':
                dataXListaCultivo['data_nodos'] = []
                dataXListaCultivo['medida_simbolo'] = '%H'

                data['id']  = "humedad"
                data['medida'] = "humedad"
                data['modo'] = "inicio"
                dataXListaCultivo['url_inicio'] = utils.get_url_grafana_by_time(data)+'&width=800&height=800'
                data['modo'] = "historico"
                dataXListaCultivo['url_historico'] = utils.get_url_grafana_by_time(data)
                #Verifica si Influx de Finca tiene data de humedad
                if 'Humedad' in medicionesInfluxFincas:
                    for medicionInfluxHF in medicionesInfluxFincas['Humedad']:
                        if medicionInfluxHF[0] == dataXListaCultivo['finca']['nombre']:
                            dataXListaCultivo['minimo_medido'] = medicionInfluxHF[1]
                            dataXListaCultivo['promedio_medido'] = medicionInfluxHF[2]
                            dataXListaCultivo['maximo_medido'] = medicionInfluxHF[3]
                else:
                    dataXListaCultivo['minimo_medido'] = '-'
                    dataXListaCultivo['promedio_medido'] = '-'
                    dataXListaCultivo['maximo_medido'] = '-'

                #Verifica si Influx de Nodos tiene data de humedad
                if 'Humedad' in medicionesInfluxNodos:
                    for medicionInfluxHN in medicionesInfluxNodos['Humedad']:
                        dataXListaCultivo['data_nodos'].append(medicionInfluxHN)
                else:
                    dataXListaCultivo['data_nodos'].append(["-","-","-","-"])
            
            elif medida == 'precipitacion':
                dataXListaCultivo['data_nodos'] = []
                dataXListaCultivo['medida_simbolo'] = 'ml'

                data['id']  = "precipitacion"
                data['medida'] = "precipitacion"
                data['modo'] = "inicio"
                dataXListaCultivo['url_inicio'] = utils.get_url_grafana_by_time(data)+'&width=800&height=800'
                data['modo'] = "historico"
                dataXListaCultivo['url_historico'] = utils.get_url_grafana_by_time(data)
                #Verifica si Influx de Finca tiene data de humedad
                if 'Precipitacion' in medicionesInfluxFincas:
                    for medicionInfluxPF in medicionesInfluxFincas['Precipitacion']:
                        if medicionInfluxPF[0] == dataXListaCultivo['finca']['nombre']:
                            dataXListaCultivo['minimo_medido'] = medicionInfluxPF[1]
                            dataXListaCultivo['promedio_medido'] = medicionInfluxPF[2]
                            dataXListaCultivo['maximo_medido'] = medicionInfluxPF[3]
                else:
                    dataXListaCultivo['minimo_medido'] = '-'
                    dataXListaCultivo['promedio_medido'] = '-'
                    dataXListaCultivo['maximo_medido'] = '-'

                #Verifica si Influx de Nodos tiene data de humedad
                if 'Precipitacion' in medicionesInfluxNodos:
                    for medicionInfluxPN in medicionesInfluxNodos['Precipitacion']:
                        dataXListaCultivo['data_nodos'].append(medicionInfluxPN)
                else:
                    dataXListaCultivo['data_nodos'].append(["-","-","-","-"])

            elif medida == 'radiacion':
                dataXListaCultivo['data_nodos'] = []
                dataXListaCultivo['medida_simbolo'] = 'lux'

                data['id']  = "radiacion"
                data['medida'] = "radiacion"
                data['modo'] = "inicio"
                dataXListaCultivo['url_inicio'] = utils.get_url_grafana_by_time(data)+'&width=800&height=800'
                data['modo'] = "historico"
                dataXListaCultivo['url_historico'] = utils.get_url_grafana_by_time(data)
                #Verifica si Influx de Finca tiene data de humedad
                if 'Radiación Solar' in medicionesInfluxFincas:
                    for medicionInfluxRSF in medicionesInfluxFincas['Radiación Solar']:
                        if medicionInfluxRSF[0] == dataXListaCultivo['finca']['nombre']:
                            dataXListaCultivo['minimo_medido'] = medicionInfluxRSF[1]
                            dataXListaCultivo['promedio_medido'] = medicionInfluxRSF[2]
                            dataXListaCultivo['maximo_medido'] = medicionInfluxRSF[3]
                else:
                    dataXListaCultivo['minimo_medido'] = '-'
                    dataXListaCultivo['promedio_medido'] = '-'
                    dataXListaCultivo['maximo_medido'] = '-'

                #Verifica si Influx de Nodos tiene data de humedad
                if 'Radiación Solar' in medicionesInfluxNodos:
                    for medicionInfluxRSN in medicionesInfluxNodos['Radiación Solar']:
                        dataXListaCultivo['data_nodos'].append(medicionInfluxRSN)
                else:
                    dataXListaCultivo['data_nodos'].append(["-","-","-","-"])
            
            dataXListaCultivo['nombre_cultivo'] = dataXListaCultivo['cultivo']['nombre']
            dataXListaCultivo['nombre_finca'] = dataXListaCultivo['finca']['nombre']
            del dataXListaCultivo['cultivo']
            del dataXListaCultivo['finca']
            del dataXListaCultivo['user']
            bodyReporte.append(dict(dataXListaCultivo))

        #print(bodyReporte)
        contexto = {
            'planta': 'cebolla',
            'user_tag': user_tag,
            'fecha': current_time,
            'finca': finca,
            'logo' : constantes.LOGO,
            'usuario': usuario,
            'tiempo': constantes.TIEMPOS[tiempo]['title'],
            'medida': constantes.IDS[medida]['title'],
            'bodyReporte': bodyReporte,
        }

        # Rendered
        html_string = render_to_string('reportes/reporte_detalle_finca_final.html', context=contexto)
        html = HTML(string=html_string)

        result = html.write_pdf()

        # Creating http response
        reporteCode = str(randint(0, 1000))+""+str(randint(0, 1000))+""+str(randint(0, 1000))

        response = HttpResponse(content_type='application/pdf;')
        response['Content-Disposition'] = 'inline; filename=reporte_finca_detallado_'+medida+'_'+reporteCode+'.pdf'
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



#Reporte Por Fincas Varias Medidas
@api_view(['POST'])
@authentication_classes([SessionAuthentication, BasicAuthentication,TokenAuthentication])
@permission_classes([AllowAny])
def generate_pdf_detalle_finca_medidas_final(request):
    if request.user.is_authenticated:

        medidas = request.data.get("medidas")
        finca = request.data.get("finca")
        tiempo = request.data.get("tiempo")
        user_tag = request.data.get("user_tag")

        now = datetime.now()
        current_time = now.strftime("%d %b %y %H:%M:%S")

        try:
            usuario = Usuario.objects.get(user_tag=user_tag)
        except Usuario.DoesNotExist:
            return Response({'message': 'Usuario no existe'},status=status.HTTP_404_NOT_FOUND)

        try:
            finca_data = Finca.objects.get(nombre=finca)
        except Finca.DoesNotExist:
            return Response({'message': 'Finca no existe'},status=status.HTTP_404_NOT_FOUND)

        try:
            cultivosXFinca = ListaCultivo.objects.filter(id_user=usuario).filter(id_finca=finca_data)
        except Usuario.DoesNotExist:
            return Response({'message': 'No existe un cultivo registrado en esta finca'},status=status.HTTP_404_NOT_FOUND)


        dataReporteFinal = ListaCultivoNewSerializer(cultivosXFinca, many=True).data

        data = {}
        bodyReporte = []

        data['finca'] = finca
        data['tiempo'] = tiempo
        data['user_tag'] = user_tag

        medicionesInfluxFincas = influxdbConnector.obtenerDataFincaDetalleFinal(constantes.TIEMPOS[tiempo]['start'], constantes.TIEMPOS[tiempo]['stop'], finca, user_tag)
        medicionesInfluxNodos = influxdbConnector.obtenerDataNodoFinca(constantes.TIEMPOS[tiempo]['start'], constantes.TIEMPOS[tiempo]['stop'], finca, user_tag)

        for dataXListaCultivo in dataReporteFinal:

            dataXListaCultivo['dataMedida'] = []
            for medida in medidas:
                dataXListaCultivoMedida = {}
                
                if medida == 'temperatura':
                    dataXListaCultivoMedida['tipo_medida']= 'Temperatura'
                    dataXListaCultivoMedida['data_nodos'] = []
                    dataXListaCultivoMedida['medida_simbolo'] = '°C'

                    data['id']  = "temperatura"
                    data['medida'] = "temperatura"
                    data['modo'] = "inicio"
                    dataXListaCultivoMedida['url_inicio'] = utils.get_url_grafana_by_time(data)+'&width=600&height=600'
                    data['modo'] = "historico"
                    dataXListaCultivoMedida['url_historico'] = utils.get_url_grafana_by_time(data)
                    #Verifica si Influx de Finca tiene data de temperatura
                    if 'Temperatura' in medicionesInfluxFincas and medicionesInfluxFincas['Temperatura'] != None:
                        for medicionInfluxTF in medicionesInfluxFincas['Temperatura']:
                            if medicionInfluxTF[0] == dataXListaCultivo['finca']['nombre']:
                                dataXListaCultivoMedida['minimo_medido'] = medicionInfluxTF[1]
                                dataXListaCultivoMedida['promedio_medido'] = medicionInfluxTF[2]
                                dataXListaCultivoMedida['maximo_medido'] = medicionInfluxTF[3]
                    else:
                        dataXListaCultivoMedida['minimo_medido'] = '-'
                        dataXListaCultivoMedida['promedio_medido'] = '-'
                        dataXListaCultivoMedida['maximo_medido'] = '-'

                    #Verifica si Influx de Nodos tiene data de temperatura
                    if 'Temperatura' in medicionesInfluxNodos:
                        for medicionInfluxTN in medicionesInfluxNodos['Temperatura']:
                            dataXListaCultivoMedida['data_nodos'].append(medicionInfluxTN)
                    else:
                        dataXListaCultivoMedida['data_nodos'].append(["-","-","-","-"])

                elif medida == 'humedad':
                    dataXListaCultivoMedida['tipo_medida']= 'Humedad'
                    dataXListaCultivoMedida['data_nodos'] = []
                    dataXListaCultivoMedida['medida_simbolo'] = '%H'

                    data['id']  = "humedad"
                    data['medida'] = "humedad"
                    data['modo'] = "inicio"
                    dataXListaCultivoMedida['url_inicio'] = utils.get_url_grafana_by_time(data)+'&width=800&height=800'
                    data['modo'] = "historico"
                    dataXListaCultivoMedida['url_historico'] = utils.get_url_grafana_by_time(data)
                    #Verifica si Influx de Finca tiene data de humedad
                    if 'Humedad' in medicionesInfluxFincas and medicionesInfluxFincas['Humedad'] != None:
                        for medicionInfluxHF in medicionesInfluxFincas['Humedad']:
                            if medicionInfluxHF[0] == dataXListaCultivo['finca']['nombre']:
                                dataXListaCultivoMedida['minimo_medido'] = medicionInfluxHF[1]
                                dataXListaCultivoMedida['promedio_medido'] = medicionInfluxHF[2]
                                dataXListaCultivoMedida['maximo_medido'] = medicionInfluxHF[3]
                    else:
                        dataXListaCultivoMedida['minimo_medido'] = '-'
                        dataXListaCultivoMedida['promedio_medido'] = '-'
                        dataXListaCultivoMedida['maximo_medido'] = '-'

                    #Verifica si Influx de Nodos tiene data de humedad
                    if 'Humedad' in medicionesInfluxNodos:
                        for medicionInfluxHN in medicionesInfluxNodos['Humedad']:
                            dataXListaCultivoMedida['data_nodos'].append(medicionInfluxHN)
                    else:
                        dataXListaCultivoMedida['data_nodos'].append(["-","-","-","-"])
                
                elif medida == 'precipitacion':
                    dataXListaCultivoMedida['tipo_medida']= 'Precipitacion'
                    dataXListaCultivoMedida['data_nodos'] = []
                    dataXListaCultivoMedida['medida_simbolo'] = 'ml'

                    data['id']  = "precipitacion"
                    data['medida'] = "precipitacion"
                    data['modo'] = "inicio"
                    dataXListaCultivoMedida['url_inicio'] = utils.get_url_grafana_by_time(data)+'&width=800&height=800'
                    data['modo'] = "historico"
                    dataXListaCultivoMedida['url_historico'] = utils.get_url_grafana_by_time(data)
                    #Verifica si Influx de Finca tiene data de humedad
                    if 'Precipitacion' in medicionesInfluxFincas and medicionesInfluxFincas['Precipitacion'] != None:
                        for medicionInfluxPF in medicionesInfluxFincas['Precipitacion']:
                            if medicionInfluxPF[0] == dataXListaCultivo['finca']['nombre']:
                                dataXListaCultivoMedida['minimo_medido'] = medicionInfluxPF[1]
                                dataXListaCultivoMedida['promedio_medido'] = medicionInfluxPF[2]
                                dataXListaCultivoMedida['maximo_medido'] = medicionInfluxPF[3]
                    else:
                        dataXListaCultivoMedida['minimo_medido'] = '-'
                        dataXListaCultivoMedida['promedio_medido'] = '-'
                        dataXListaCultivoMedida['maximo_medido'] = '-'

                    #Verifica si Influx de Nodos tiene data de humedad
                    if 'Precipitacion' in medicionesInfluxNodos:
                        for medicionInfluxPN in medicionesInfluxNodos['Precipitacion']:
                            dataXListaCultivoMedida['data_nodos'].append(medicionInfluxPN)
                    else:
                        dataXListaCultivoMedida['data_nodos'].append(["-","-","-","-"])

                elif medida == 'radiacion':
                    dataXListaCultivoMedida['tipo_medida']= 'Radiacion Solar'
                    dataXListaCultivoMedida['data_nodos'] = []
                    dataXListaCultivoMedida['medida_simbolo'] = 'lux'

                    data['id']  = "radiacion"
                    data['medida'] = "radiacion"
                    data['modo'] = "inicio"
                    dataXListaCultivoMedida['url_inicio'] = utils.get_url_grafana_by_time(data)+'&width=800&height=800'
                    data['modo'] = "historico"
                    dataXListaCultivoMedida['url_historico'] = utils.get_url_grafana_by_time(data)
                    #Verifica si Influx de Finca tiene data de humedad
                    if 'Radiación Solar' in medicionesInfluxFincas and medicionesInfluxFincas['Radiación Solar'] != None:
                        for medicionInfluxRSF in medicionesInfluxFincas['Radiación Solar']:
                            if medicionInfluxRSF[0] == dataXListaCultivo['finca']['nombre']:
                                dataXListaCultivoMedida['minimo_medido'] = medicionInfluxRSF[1]
                                dataXListaCultivoMedida['promedio_medido'] = medicionInfluxRSF[2]
                                dataXListaCultivoMedida['maximo_medido'] = medicionInfluxRSF[3]
                    else:
                        dataXListaCultivoMedida['minimo_medido'] = '-'
                        dataXListaCultivoMedida['promedio_medido'] = '-'
                        dataXListaCultivoMedida['maximo_medido'] = '-'

                    #Verifica si Influx de Nodos tiene data de humedad
                    if 'Radiación Solar' in medicionesInfluxNodos:
                        for medicionInfluxRSN in medicionesInfluxNodos['Radiación Solar']:
                            dataXListaCultivoMedida['data_nodos'].append(medicionInfluxRSN)
                    else:
                        dataXListaCultivoMedida['data_nodos'].append(["-","-","-","-"])
                
                #print("======================================")
                #print(dataXListaCultivoMedida)
                #print("======================================")
                dataXListaCultivo['dataMedida'].append(dataXListaCultivoMedida)

            dataXListaCultivo['nombre_cultivo'] = dataXListaCultivo['cultivo']['nombre']
            dataXListaCultivo['nombre_finca'] = dataXListaCultivo['finca']['nombre']
            del dataXListaCultivo['cultivo']
            del dataXListaCultivo['finca']
            del dataXListaCultivo['user']
            bodyReporte.append(dict(dataXListaCultivo))

        #print(bodyReporte)
        contexto = {
            'user_tag': user_tag,
            'fecha': current_time,
            'finca': finca,
            'logo' : constantes.LOGO,
            'usuario': usuario,
            'tiempo': constantes.TIEMPOS[tiempo]['title'],
            'bodyReporte': bodyReporte,
        }

        # Rendered
        html_string = render_to_string('reportes/reporte_detalle_finca_medidas_final.html', context=contexto)
        html = HTML(string=html_string)

        result = html.write_pdf()

        # Creating http response
        reporteCode = str(randint(0, 1000))+""+str(randint(0, 1000))+""+str(randint(0, 1000))

        response = HttpResponse(content_type='application/pdf;')
        response['Content-Disposition'] = 'inline; filename=reporte_finca_detallado_medidas_'+reporteCode+'.pdf'
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



#Reporte Notificaciones
@api_view(['POST'])
@authentication_classes([SessionAuthentication, BasicAuthentication,TokenAuthentication])
@permission_classes([AllowAny])
def generate_pdf_notificaciones_final(request):
    if request.user.is_authenticated:
        user_tag = request.data.get("user_tag")
        #tiempo = request.data.get("tiempo")
        dias_dif = request.data.get("dias_dif")
        fecha_inicio = request.data.get("fechaInicio")
        fecha_fin = request.data.get("fechafin")

        now = datetime.now()
        current_time = now.strftime("%d %b %y %H:%M:%S")

        # fecha_final = date.today()
        # fecha_inicial = fecha_final - timedelta(days=dias_dif)
        # print(fecha_final)
        # print(fecha_inicial)

        try:
            usuario = Usuario.objects.get(user_tag=user_tag)
        except Usuario.DoesNotExist:
            return Response({'message': 'Usuario no existe'},status=status.HTTP_404_NOT_FOUND)

        #Verificacion el Usuario es admin(1) o no(2-otro)
        if usuario.user_type == 1:
            try:
                notificaciones = NotificacionRespaldo.objects.filter(fecha__range=[fecha_inicio, fecha_fin])
            except NotificacionRespaldo.DoesNotExist:
                return Response({'message': 'Sin notificaciones'},status=status.HTTP_404_NOT_FOUND)
        else:
            try:
                notificaciones = NotificacionRespaldo.objects.filter(user_tag=user_tag).filter(fecha__range=[fecha_inicio, fecha_fin])
            except NotificacionRespaldo.DoesNotExist:
                return Response({'message': 'Sin notificaciones'},status=status.HTTP_404_NOT_FOUND)
        
        notificacionesReporte = []

        for rsp in notificaciones:
            data_rsp = NotificacionRespaldoSerializer(rsp).data
            data_rsp['dia'] = LISTA_DIAS_DICT[data_rsp['dia']]

            if data_rsp['fue_revisada'] == 'S':
                data_rsp['fue_revisada'] = 'Si'
            else:
                data_rsp['fue_revisada'] = 'No'
            
            if data_rsp['fecha'] is not None:
                data_rsp['fecha'] = data_rsp['fecha'].split(".")[0]
                data_rsp['fecha'] = datetime.strptime(data_rsp['fecha'], "%Y-%m-%dT%H:%M:%S").strftime("%Y-%m-%d %H:%M:%S")
         
            notificacionesReporte.append(data_rsp)
        
        contexto = {
            'user_tag': user_tag,
            'fecha': current_time,
            'fecha_inicio': fecha_inicio,
            'fecha_fin': fecha_fin,
            'logo': constantes.LOGO,
            'notificaciones': notificacionesReporte,
            'usuario': usuario,
        }

        # Rendered
        html_string = render_to_string('reportes/reporte_notificaciones_final.html', context=contexto)
        html = HTML(string=html_string)

        result = html.write_pdf()

        # Creating http response
        reporteCode = str(randint(0, 1000))+""+str(randint(0, 1000))+""+str(randint(0, 1000))

        response = HttpResponse(content_type='application/pdf;')
        response['Content-Disposition'] = 'inline; filename=reporte_notificaciones_'+reporteCode+'.pdf'
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
