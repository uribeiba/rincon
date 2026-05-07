from django.db import models


# =========================================
# TIPOS DE PAGO
# =========================================
TIPOS_PAGO = (

    ('efectivo', 'Efectivo'),
    ('debito', 'Débito'),
    ('credito', 'Crédito'),
    ('transferencia', 'Transferencia'),

)


# =========================================
# VENTAS
# =========================================
class Venta(models.Model):

    fecha = models.DateField()

    tipo_pago = models.CharField(
        max_length=20,
        choices=TIPOS_PAGO
    )

    total = models.DecimalField(
        max_digits=12,
        decimal_places=2
    )

    observacion = models.TextField(
        blank=True,
        null=True
    )

    class Meta:
        verbose_name = "Venta"
        verbose_name_plural = "Ventas"
        ordering = ['-fecha', '-id']

    def __str__(self):

        return (
            f"{self.fecha} - "
            f"{self.tipo_pago} - "
            f"${self.total}"
        )