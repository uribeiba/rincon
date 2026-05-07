from django.urls import path
from .views import compras_view

urlpatterns = [
    path('', compras_view, name='compras'),
]