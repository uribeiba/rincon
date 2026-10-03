# compras/models.py

from django.db import models
from productos.models import Producto


# =========================================
# PROVEEDORES
# =========================================
class Proveedor(models.Model):

    nombre = models.CharField(
        max_length=150
    )

    # RUT del proveedor. Se usa para identificar automáticamente
    # al emisor cuando leemos el timbre PDF417 del SII.
    # Se permite vacío para no romper proveedores históricos.
    rut = models.CharField(
        max_length=12,
        unique=True,
        blank=True,
        null=True,
        verbose_name="RUT"
    )

    telefono = models.CharField(
        max_length=50,
        blank=True,
        null=True
    )

    email = models.EmailField(
        blank=True,
        null=True
    )

    direccion = models.TextField(
        blank=True,
        null=True
    )

    class Meta:
        verbose_name = "Proveedor"
        verbose_name_plural = "Proveedores"
        ordering = ['nombre']

    def __str__(self):

        return self.nombre


# =========================================
# COMPRAS
# =========================================
class Compra(models.Model):

    TIPO_DOCUMENTO = (

        ('factura', 'Factura'),
        ('boleta', 'Boleta'),

    )

    proveedor = models.ForeignKey(
        Proveedor,
        on_delete=models.CASCADE
    )

    fecha = models.DateField()

    total = models.DecimalField(
        max_digits=12,
        decimal_places=2
    )

    tipo_documento = models.CharField(
        max_length=20,
        choices=TIPO_DOCUMENTO,
        default='factura'
    )

    numero_documento = models.CharField(
        max_length=100,
        blank=True,
        null=True
    )

    observacion = models.TextField(
        blank=True,
        null=True
    )

    class Meta:
        verbose_name = "Compra"
        verbose_name_plural = "Compras"
        ordering = ['-fecha', '-id']

    def __str__(self):

        return (
            f"{self.fecha} - "
            f"{self.proveedor.nombre} - "
            f"${self.total}"
        )


# =========================================
# DETALLE COMPRA
# =========================================
class DetalleCompra(models.Model):

    compra = models.ForeignKey(
        Compra,
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

    costo = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    class Meta:
        verbose_name = "Detalle compra"
        verbose_name_plural = "Detalles compra"

    def __str__(self):

        return (
            f"{self.producto.nombre} "
            f"- {self.cantidad} kg"
        )