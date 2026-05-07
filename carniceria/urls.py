from django.contrib import admin
from django.urls import path, include
from reportes.views import dashboard

urlpatterns = [
    path('admin/', admin.site.urls),

    path('', dashboard, name='dashboard'),

    path('ventas/', include('ventas.urls')),
    path('compras/', include('compras.urls')),
    path('gastos/', include('gastos.urls')),

    path('', include('usuarios.urls')),  # 👈 ESTA LÍNEA SOLUCIONA TODO
]