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

    efectivo = models.IntegerField(default=0)
    debito = models.IntegerField(default=0)
    transferencia = models.IntegerField(default=0)
    credito = models.IntegerField(default=0)

    total = models.IntegerField(default=0)

    observacion = models.TextField(blank=True, null=True)

    class Meta:
        verbose_name = 'Venta'
        verbose_name_plural = 'Ventas'
        ordering = ['-fecha']

    def save(self, *args, **kwargs):

        self.total = (
            self.efectivo +
            self.debito +
            self.transferencia +
            self.credito
        )

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.fecha} - ${self.total}"