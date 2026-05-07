from django.contrib import admin
from .models import Venta


@admin.register(Venta)
class VentaAdmin(admin.ModelAdmin):

    list_display = (
        'id',
        'fecha',
        'tipo_pago',
        'total',
    )

    list_filter = (
        'fecha',
        'tipo_pago',
    )

    search_fields = (
        'observacion',
    )

    date_hierarchy = 'fecha'

    ordering = (
        '-fecha',
        '-id',
    )

    fieldsets = (

        (
            'Información venta',
            {
                'fields': (
                    'fecha',
                    'tipo_pago',
                    'total',
                    'observacion'
                )
            }
        ),

    )