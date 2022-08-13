from django.urls import path
from rest_framework import routers
from . import views

# Wire up our API using automatic URL routing.
# Additionally, we include login URLs for the browsable API.
urlpatterns = [
   path('getCultivos', views.crops),           #Original
   path('crops', views.crops),                     #Nombre de endpoint mejorado
   path('crop/create', views.cultivosCrear),       #Api para crear cultivo
   path('crop/<int:pk>',views.cultivo),


   path('cultivos_user',views.cultivos_user),                  #APIS VIEJAS
   path('fincas_cultivo_user',views.fincas_cultivo_user),      #APIS VIEJAS

   #path('crops_user_new',views.cultivos_user_new),
   #path('farms_user_new',views.fincas_user_new),
   #path('farms_crop_user_new',views.finca_cultivo_user_new),
   path('farm_crop_user_create',views.farms_crop_user_create),
   path('farm_crop_user/<int:pk>',views.finca_cultivo_user),
   path('farms_crops_users',views.farms_crops_users),
]
router = routers.DefaultRouter()
#router.register('crops',views.CultivoViewSet,'crops')
#router.register('listacultivos',views.ListaCultivoViewSet,'listacultivos')
urlpatterns = urlpatterns + router.urls