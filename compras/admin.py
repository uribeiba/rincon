from django.contrib import admin
from .models import Compra, DetalleCompra, Proveedor

class DetalleCompraInline(admin.TabularInline):
    model = DetalleCompra
    extra = 1

@admin.register(Compra)
class CompraAdmin(admin.ModelAdmin):
    list_display = ('id', 'proveedor', 'fecha', 'total')
    inlines = [DetalleCompraInline]

admin.site.register(Proveedor)