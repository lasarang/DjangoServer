from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.authentication import SessionAuthentication, BasicAuthentication, TokenAuthentication
from rest_framework.permissions import AllowAny
from rest_framework import status
from notificaciones.models import NotificacionRespaldo
from notificaciones.serializers import NotificacionRespaldoSerializer
from rest_framework.response import Response


from datetime import datetime

LISTA_DIAS_DICT = {0:'LUNES',1:'MARTES',2:'MIÉRCOLES',3:'JUEVES',4:'VIERNES',5:'SÁBADO',6:'DOMINGO'}
# Create your views here.

# Obtener las notificaciones por user_tag y si fueron o no revisadas
@api_view(['GET'])
@authentication_classes([SessionAuthentication, BasicAuthentication, TokenAuthentication])
@permission_classes([AllowAny])
def notificaciones(request):
   if request.user.is_authenticated:

      print(request.GET)

      #Obtener params de un url
      user_tag = request.GET["user_tag"]

      response = []
      if "was_reviewed" in request.GET:
         fue_revisada = request.GET["was_reviewed"]
         response = NotificacionRespaldo.objects.filter(user_tag=user_tag).filter(fue_revisada=fue_revisada).distinct()
      else:
         response = NotificacionRespaldo.objects.filter(user_tag=user_tag).distinct()

      responseFinal = []
      for rsp in response:
         data_rsp = NotificacionRespaldoSerializer(rsp).data
         data_rsp['dia'] = LISTA_DIAS_DICT[data_rsp['dia']]
         
         if data_rsp['fecha'] is not None:
            data_rsp['fecha'] = data_rsp['fecha'].split(".")[0]
            data_rsp['fecha'] = datetime.strptime(data_rsp['fecha'], "%Y-%m-%dT%H:%M:%S").strftime("%Y-%m-%d %H:%M:%S")
         
         responseFinal.append(data_rsp)
      return Response(responseFinal, status=status.HTTP_200_OK)

   msg = {
      'error': 'Permission Denied!'
   }
   return Response(msg, status=status.HTTP_403_FORBIDDEN)

# Actualizar la notificación
@api_view(['PUT'])
@authentication_classes([SessionAuthentication, BasicAuthentication, TokenAuthentication])
@permission_classes([AllowAny])
def notificacionUpdate(request, pk):

   #Valida que exista la relación
   if request.user.is_authenticated:
      try:
         data = NotificacionRespaldo.objects.get(pk=pk)
      except NotificacionRespaldo.DoesNotExist:
         return Response({'message': 'La notificación no existe'},status=status.HTTP_404_NOT_FOUND)

   #Actualiza el registro por pk, se puede actualizar por partes
   if request.method == 'PUT' and request.user.is_authenticated:
      requestFinal = {}
      requestFinal['fue_revisada'] = request.data['was_reviewed']
      serializer = NotificacionRespaldoSerializer(data, data=requestFinal, partial=True)
      if serializer.is_valid():
         serializer.save()
         return Response(serializer.data, status=status.HTTP_200_OK)
      return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

   else:
      msg = {
         'error': 'Permission Denied!'
      }
      return Response(msg, status=status.HTTP_403_FORBIDDEN)