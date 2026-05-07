# productos/admin.py

from django.contrib import admin
from .models import (
    Producto,
    Categoria,
    ConfiguracionCosteo
)


# =========================================
# PRODUCTOS
# =========================================
@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):

    list_display = (
        'nombre',
        'categoria',
        'costo',

        'mostrar_gastos_fijos',
        'mostrar_gastos_variables',

        'mostrar_costo_real',
        'mostrar_iva',
        'mostrar_costo_con_iva',

        'mostrar_precio_sugerido',

        'mostrar_ganancia',
        'mostrar_margen',
    )

    search_fields = (
        'nombre',
    )

    list_filter = (
        'categoria',
    )

    readonly_fields = (
        'mostrar_gastos_fijos',
        'mostrar_gastos_variables',

        'mostrar_costo_real',
        'mostrar_iva',
        'mostrar_costo_con_iva',

        'mostrar_precio_sugerido',

        'mostrar_ganancia',
        'mostrar_margen',
    )

    fields = (
        'nombre',
        'categoria',
        'costo',

        'mostrar_gastos_fijos',
        'mostrar_gastos_variables',

        'mostrar_costo_real',
        'mostrar_iva',
        'mostrar_costo_con_iva',

        'mostrar_precio_sugerido',

        'mostrar_ganancia',
        'mostrar_margen',
    )

    # =========================================
    # GASTOS FIJOS
    # =========================================
    def mostrar_gastos_fijos(self, obj):

        if not obj.pk:
            return "-"

        return f"${obj.gastos_fijos():,.0f}"

    mostrar_gastos_fijos.short_description = "Gastos fijos"

    # =========================================
    # GASTOS VARIABLES
    # =========================================
    def mostrar_gastos_variables(self, obj):

        if not obj.pk:
            return "-"

        return f"${obj.gastos_variables():,.0f}"

    mostrar_gastos_variables.short_description = "Gastos variables"

    # =========================================
    # COSTO REAL
    # =========================================
    def mostrar_costo_real(self, obj):

        if not obj.pk:
            return "-"

        return f"${obj.costo_real():,.0f}"

    mostrar_costo_real.short_description = "Costo real"

    # =========================================
    # IVA
    # =========================================
    def mostrar_iva(self, obj):

        if not obj.pk:
            return "-"

        return f"${obj.iva_monto():,.0f}"

    mostrar_iva.short_description = "IVA"

    # =========================================
    # COSTO + IVA
    # =========================================
    def mostrar_costo_con_iva(self, obj):

        if not obj.pk:
            return "-"

        return f"${obj.costo_con_iva():,.0f}"

    mostrar_costo_con_iva.short_description = "Costo + IVA"

    # =========================================
    # PRECIO SUGERIDO
    # =========================================
    def mostrar_precio_sugerido(self, obj):

        if not obj.pk:
            return "-"

        return f"${obj.precio_sugerido():,.0f}"

    mostrar_precio_sugerido.short_description = "Precio sugerido"

    # =========================================
    # GANANCIA $
    # =========================================
    def mostrar_ganancia(self, obj):

        if not obj.pk:
            return "-"

        return f"${obj.ganancia_pesos():,.0f}"

    mostrar_ganancia.short_description = "Ganancia $"

    # =========================================
    # MARGEN %
    # =========================================
    def mostrar_margen(self, obj):

        if not obj.pk:
            return "-"

        return f"{obj.ganancia_porcentaje():.1f}%"

    mostrar_margen.short_description = "% Ganancia"


# =========================================
# CATEGORÍAS
# =========================================
@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):

    search_fields = (
        'nombre',
    )


# =========================================
# CONFIG COSTEO
# =========================================
@admin.register(ConfiguracionCosteo)
class ConfiguracionCosteoAdmin(admin.ModelAdmin):

    list_display = (
        'gastos_fijos_por_kg',
        'gastos_variables_por_kg',
        'iva_por_defecto',
        'margen_objetivo'
    )