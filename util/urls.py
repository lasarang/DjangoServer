from django.urls import path
from rest_framework import routers
from . import views

# Wire up our API using automatic URL routing.
# Additionally, we include login URLs for the browsable API.
urlpatterns = [
   path('reporte_general', views.generate_pdf_general),
   path('reporte_detalle_finca', views.generate_pdf_detalle_finca),
   path('reporte_detalle_sensor', views.generate_pdf_detalle_sensor),

   path('general_report', views.generate_pdf_general_final),
   path('farm_detail_report', views.generate_pdf_detalle_finca_final),
   path('sensor_detail_report', views.generate_pdf_detalle_sensor),
]
router = routers.DefaultRouter()
urlpatterns = urlpatterns + router.urls