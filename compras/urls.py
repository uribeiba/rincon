from django.urls import path

from .views import (
    compras_view,
    procesar_pdf417,
    guardar_compra_factura,
    diagnostico_lector,
)

urlpatterns = [
    path('', compras_view, name='compras'),
    path('api/procesar-pdf417/', procesar_pdf417, name='procesar_pdf417'),
    path('api/guardar-factura/', guardar_compra_factura, name='guardar_compra_factura'),
    path('diagnostico/', diagnostico_lector, name='diagnostico_lector'),
]