from django.contrib import admin
from django.db.models import Sum
from django.utils.html import format_html
from rangefilter.filters import DateRangeFilter

from .models import Compra, DetalleCompra, Proveedor


class DetalleCompraInline(admin.TabularInline):
    model = DetalleCompra
    extra = 1


@admin.register(Compra)
class CompraAdmin(admin.ModelAdmin):
    list_display = (
        'fecha',
        'proveedor',
        'tipo_documento',
        'numero_documento',
        'total_formateado',
    )
    list_filter = (
        ('fecha', DateRangeFilter),   # filtro por rango de fechas
        'proveedor',
        'tipo_documento',
    )
    search_fields = ('observacion', 'proveedor__nombre', 'numero_documento')
    ordering = ('-fecha', '-id')
    date_hierarchy = 'fecha'
    inlines = [DetalleCompraInline]

    fields = (
        'fecha',
        'proveedor',
        'tipo_documento',
        'numero_documento',
        'total',
        'observacion',
    )
    # Si quieres que total sea solo lectura (calculado desde inlines), descomenta:
    # readonly_fields = ('total',)

    # =====================================
    # Formato chileno
    # =====================================
    def formato_clp(self, valor):
        valor = valor or 0
        return "$ {:,}".format(int(valor)).replace(",", ".")

    def total_formateado(self, obj):
        return format_html(
            "<strong style='color:green'>{}</strong>",
            self.formato_clp(obj.total)
        )
    total_formateado.short_description = "TOTAL"

    # =====================================
    # Resumen superior (suma total de compras filtradas)
    # =====================================
    def changelist_view(self, request, extra_context=None):
        response = super().changelist_view(request, extra_context=extra_context)
        try:
            qs = response.context_data['cl'].queryset
            total_general = qs.aggregate(total=Sum('total'))['total'] or 0
            response.context_data['totales'] = {
                'total': self.formato_clp(total_general),
            }
        except Exception as e:
            print(e)
        return response


admin.site.register(Proveedor)