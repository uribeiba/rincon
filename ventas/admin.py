from django.contrib import admin
from django.db.models import Sum
from django.utils.html import format_html

from rangefilter.filters import DateRangeFilter

from .models import Venta


@admin.register(Venta)
class VentaAdmin(admin.ModelAdmin):

    # =====================================
    # TABLA ADMIN
    # =====================================

    list_display = (
        'fecha',
        'efectivo_formateado',
        'debito_formateado',
        'transferencia_formateado',
        'credito_formateado',
        'total_formateado',
    )

    list_filter = (
        ('fecha', DateRangeFilter),
    )

    search_fields = (
        'observacion',
    )

    ordering = ('-fecha',)

    date_hierarchy = 'fecha'

    # =====================================
    # FORMULARIO
    # =====================================

    fields = (
        'fecha',
        ('efectivo', 'debito'),
        ('transferencia', 'credito'),
        'total',
        'observacion',
    )

    # IMPORTANTE:
    # quitamos readonly_fields
    # para que JS pueda actualizar total
    #
    # readonly_fields = ('total',)

    class Media:
        js = ('admin/js/ventas.js',)
        css = {
            'all': ('admin/css/ventas.css',)
        }

    # =====================================
    # FORMATO CHILENO
    # =====================================

    def formato_clp(self, valor):

        valor = valor or 0

        return "$ {:,}".format(
            int(valor)
        ).replace(",", ".")

    # =====================================
    # COLUMNAS FORMATEADAS
    # =====================================

    def efectivo_formateado(self, obj):
        return self.formato_clp(obj.efectivo)

    def debito_formateado(self, obj):
        return self.formato_clp(obj.debito)

    def transferencia_formateado(self, obj):
        return self.formato_clp(obj.transferencia)

    def credito_formateado(self, obj):
        return self.formato_clp(obj.credito)

    def total_formateado(self, obj):
        return format_html(
            "<strong style='color:green;font-size:15px'>{}</strong>",
            self.formato_clp(obj.total)
        )

    efectivo_formateado.short_description = "Efectivo"
    debito_formateado.short_description = "Débito"
    transferencia_formateado.short_description = "Transferencia"
    credito_formateado.short_description = "Crédito"
    total_formateado.short_description = "TOTAL"

    # =====================================
    # RESUMEN SUPERIOR
    # =====================================

    def changelist_view(self, request, extra_context=None):

        response = super().changelist_view(
            request,
            extra_context=extra_context,
        )

        try:

            qs = response.context_data['cl'].queryset

            totales = qs.aggregate(

                efectivo=Sum('efectivo'),
                debito=Sum('debito'),
                transferencia=Sum('transferencia'),
                credito=Sum('credito'),
                total=Sum('total'),

            )

            response.context_data['totales'] = {

                'efectivo': self.formato_clp(
                    totales['efectivo']
                ),

                'debito': self.formato_clp(
                    totales['debito']
                ),

                'transferencia': self.formato_clp(
                    totales['transferencia']
                ),

                'credito': self.formato_clp(
                    totales['credito']
                ),

                'total': self.formato_clp(
                    totales['total']
                ),

            }

        except Exception as e:

            print(e)

        return response