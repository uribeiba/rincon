# productos/models.py

from django.db import models


# =========================================
# CATEGORÍAS
# =========================================
class Categoria(models.Model):

    nombre = models.CharField(
        max_length=100
    )

    class Meta:
        verbose_name = "Categoría"
        verbose_name_plural = "Categorías"

    def __str__(self):
        return self.nombre


# =========================================
# CONFIGURACIÓN GLOBAL
# =========================================
class ConfiguracionCosteo(models.Model):

    gastos_fijos_por_kg = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=480.00
    )

    gastos_variables_por_kg = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=50.00
    )

    iva_por_defecto = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=19.00
    )

    # 🔥 NUEVO
    margen_objetivo = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=25.00,
        help_text="Margen esperado (%)"
    )

    class Meta:
        verbose_name = "Configuración de costeo"
        verbose_name_plural = "Configuraciones de costeo"

    def __str__(self):
        return (
            f"GF ${self.gastos_fijos_por_kg} | "
            f"GV ${self.gastos_variables_por_kg}"
        )


# =========================================
# PRODUCTOS
# =========================================
class Producto(models.Model):

    nombre = models.CharField(
        max_length=150
    )

    categoria = models.ForeignKey(
        Categoria,
        on_delete=models.CASCADE
    )

    # 🔥 ÚNICO VALOR QUE INGRESA EL USUARIO
    costo = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="Costo compra/kg"
    )

    class Meta:
        verbose_name = "Producto"
        verbose_name_plural = "Productos"

    def __str__(self):
        return self.nombre

    # =========================================
    # CONFIG
    # =========================================
    def config(self):
        return ConfiguracionCosteo.objects.first()

    # =========================================
    # GASTOS FIJOS
    # =========================================
    def gastos_fijos(self):

        config = self.config()

        if not config:
            return 0

        return float(config.gastos_fijos_por_kg)

    # =========================================
    # GASTOS VARIABLES
    # =========================================
    def gastos_variables(self):

        config = self.config()

        if not config:
            return 0

        return float(config.gastos_variables_por_kg)

    # =========================================
    # IVA %
    # =========================================
    def iva_porcentaje(self):

        config = self.config()

        if not config:
            return 0

        return float(config.iva_por_defecto)

    # =========================================
    # MARGEN OBJETIVO
    # =========================================
    def margen_objetivo(self):

        config = self.config()

        if not config:
            return 25

        return float(config.margen_objetivo)

    # =========================================
    # COSTO REAL
    # =========================================
    def costo_real(self):

        return (
            float(self.costo)
            + self.gastos_fijos()
            + self.gastos_variables()
        )

    # =========================================
    # IVA $
    # =========================================
    def iva_monto(self):

        return (
            self.costo_real()
            * (self.iva_porcentaje() / 100)
        )

    # =========================================
    # COSTO + IVA
    # =========================================
    def costo_con_iva(self):

        return (
            self.costo_real()
            + self.iva_monto()
        )

    # =========================================
    # PRECIO SUGERIDO
    # =========================================
    def precio_sugerido(self):

        margen = self.margen_objetivo() / 100

        if margen >= 1:
            return self.costo_con_iva()

        return (
            self.costo_con_iva()
            / (1 - margen)
        )

    # =========================================
    # GANANCIA $
    # =========================================
    def ganancia_pesos(self):

        return (
            self.precio_sugerido()
            - self.costo_con_iva()
        )

    # =========================================
    # GANANCIA %
    # =========================================
    def ganancia_porcentaje(self):

        precio = self.precio_sugerido()

        if precio <= 0:
            return 0

        return (
            self.ganancia_pesos()
            / precio
        ) * 100