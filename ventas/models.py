# ventas/models.py

from django.db import models
from productos.models import Producto


# =========================================
# VENTA
# =========================================
class Venta(models.Model):

    fecha = models.DateField(
        auto_now_add=True
    )

    total = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0
    )

    class Meta:
        verbose_name = "Venta"
        verbose_name_plural = "Ventas"

    def __str__(self):

        return f"Venta #{self.id}"

    # =========================================
    # RECALCULAR TOTAL
    # =========================================
    def recalcular_total(self):

        total = 0

        for detalle in self.detalles.all():

            total += detalle.subtotal()

        self.total = total

        self.save()


# =========================================
# DETALLE VENTA
# =========================================
class DetalleVenta(models.Model):

    venta = models.ForeignKey(
        Venta,
        on_delete=models.CASCADE,
        related_name='detalles'
    )

    producto = models.ForeignKey(
        Producto,
        on_delete=models.CASCADE
    )

    cantidad = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    # 🔥 PRECIO AUTOMÁTICO
    precio = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        blank=True,
        null=True
    )

    class Meta:
        verbose_name = "Detalle venta"
        verbose_name_plural = "Detalles venta"

    # =========================================
    # SAVE AUTOMÁTICO
    # =========================================
    def save(self, *args, **kwargs):

        # 🔥 TOMAR PRECIO DEL MOTOR FINANCIERO
        if self.producto:

            self.precio = (
                self.producto.precio_sugerido()
            )

        super().save(*args, **kwargs)

        # 🔥 RECALCULAR TOTAL VENTA
        self.venta.recalcular_total()

    # =========================================
    # SUBTOTAL
    # =========================================
    def subtotal(self):

        return (
            float(self.cantidad)
            * float(self.precio or 0)
        )

    def __str__(self):

        return (
            f"{self.producto.nombre}"
        )