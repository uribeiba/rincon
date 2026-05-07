from django.urls import path
from .views import crear_venta

urlpatterns = [
    path('', crear_venta, name='ventas'),
]