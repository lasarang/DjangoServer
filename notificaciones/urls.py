from django.urls import path
from rest_framework import routers
from . import views

# Wire up our API using automatic URL routing.
# Additionally, we include login URLs for the browsable API.
urlpatterns = [
   path('notifications', views.notificaciones),
   path('notifications/<int:pk>', views.notificacionUpdate),
]
router = routers.DefaultRouter()
urlpatterns = urlpatterns + router.urls