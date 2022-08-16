from django.urls import path
from rest_framework import routers
from . import views

# Wire up our API using automatic URL routing.
# Additionally, we include login URLs for the browsable API.
urlpatterns = [
   path('raspberryAll/<str:user_tag>',views.raspberryAll),
   path('fincas_cultivo/<str:user_tag>/<str:cultivo>',views.fincas_cultivo),
   path('raspberry/<str:id>',views.rapsberry),
   path('raspberry_umbrales/<str:id>',views.rapsberryUmbrales),
]
router = routers.DefaultRouter()
router.register('raspberry',views.RaspBerryViewSet,'raspberry')

urlpatterns = urlpatterns + router.urls