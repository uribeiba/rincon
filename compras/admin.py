from django.contrib import admin
from .models import Compra, DetalleCompra, Proveedor

class DetalleCompraInline(admin.TabularInline):
    model = DetalleCompra
    extra = 1



@admin.register(Compra)
class CompraAdmin(admin.ModelAdmin):
    list_display = ('id', 'proveedor', 'fecha', 'total')
    inlines = [DetalleCompraInline]
    
    list_display = (
    'id',
    'fecha',
    'proveedor',
    'tipo_documento',
    'total',
)
    list_filter = (
    'tipo_documento',
    'fecha',
    'proveedor',
)

admin.site.register(Proveedor)