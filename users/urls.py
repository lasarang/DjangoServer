from django.urls import include, path
from rest_framework import routers
from . import views
from fcm_django.api.rest_framework import FCMDeviceAuthorizedViewSet

# Wire up our API using automatic URL routing.
# Additionally, we include login URLs for the browsable API.
urlpatterns = [
   path('login', views.login),
   path('devices', FCMDeviceAuthorizedViewSet.as_view({'post': 'create'}), name='create_fcm_device'),
   path('devices/delete/<int:pk>',views.DeleteFCMDevice.as_view(), name ='delete_fcm_device'),
   path('notificacion',views.NotificationFCM.as_view(), name ='NotificationFCM'),
   path('notificacion_single',views.NotificationSingleFCM.as_view(), name ='NotificationSingleFCM'),
   path('users', views.users),
]
router = routers.DefaultRouter()
router.register('usuarios',views.UsuarioViewSet,'usuarios')
urlpatterns = urlpatterns + router.urls