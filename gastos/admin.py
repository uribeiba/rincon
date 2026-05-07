from django.contrib import admin
from .models import Gasto, TipoGasto

@admin.register(Gasto)
class GastoAdmin(admin.ModelAdmin):
    list_display = ('tipo_gasto', 'monto', 'fecha', 'tiene_factura')
    list_filter = ('tipo_gasto', 'tiene_factura')

admin.site.register(TipoGasto)