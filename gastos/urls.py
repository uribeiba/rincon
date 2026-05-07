from django.urls import path
from .views import gastos_view

urlpatterns = [
    path('', gastos_view, name='gastos'),
]