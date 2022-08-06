from django.urls import include, path
from rest_framework import routers
from . import views

# Wire up our API using automatic URL routing.
# Additionally, we include login URLs for the browsable API.
urlpatterns = [
   path('fincas', views.get_fincas),
   path('fincas2', views.get_fincas_2),
   path('finca/<int:pk>', views.finca),

   path('farms_new', views.fincas),
   path('farm_new/create', views.fincasCrear),
   path('farm_new/<int:pk>', views.finca_new)
]
router = routers.DefaultRouter()
#router.register('fincas',views.FincaViewSet,'fincas')
urlpatterns = urlpatterns + router.urls