from django.db import models

class TipoGasto(models.Model):
    TIPOS = (
        ('fijo', 'Fijo'),
        ('variable', 'Variable'),
    )

    nombre = models.CharField(max_length=100)
    tipo = models.CharField(max_length=10, choices=TIPOS)

    def __str__(self):
        return self.nombre


class Gasto(models.Model):
    tipo_gasto = models.ForeignKey(TipoGasto, on_delete=models.CASCADE)
    monto = models.DecimalField(max_digits=10, decimal_places=2)
    fecha = models.DateField()
    descripcion = models.TextField(blank=True)
    tiene_factura = models.BooleanField(default=False)