import pandas as pd
from django.core.management.base import BaseCommand

from productos.models import Producto, Categoria
from gastos.models import Gasto, TipoGasto
from compras.models import Compra, DetalleCompra, Proveedor
from ventas.models import Venta, DetalleVenta


class Command(BaseCommand):
    help = 'Importar datos desde Excel'

    def handle(self, *args, **kwargs):
        archivo = 'RAFA.xlsx'  # pon tu ruta real

        xls = pd.ExcelFile(archivo)

        self.importar_productos(xls)
        self.importar_gastos(xls)
        self.importar_compras(xls)
        self.importar_ventas(xls)

        self.stdout.write(self.style.SUCCESS('✅ Importación completada'))

    # -------------------------
    # PRODUCTOS (centro de costo)
    # -------------------------
    def importar_productos(self, xls):
        try:
            df = xls.parse('centro_costos')

            for _, row in df.iterrows():
                categoria, _ = Categoria.objects.get_or_create(
                    nombre=row.get('categoria', 'General')
                )

                Producto.objects.get_or_create(
                    nombre=row['producto'],
                    defaults={
                        'categoria': categoria,
                        'costo': row.get('costo', 0),
                        'precio_venta': row.get('precio', 0),
                    }
                )

            print("✔ Productos importados")
        except Exception as e:
            print("⚠ Error productos:", e)

    # -------------------------
    # GASTOS
    # -------------------------
    def importar_gastos(self, xls):
        try:
            df = xls.parse('gastos')

            for _, row in df.iterrows():
                tipo, _ = TipoGasto.objects.get_or_create(
                    nombre=row.get('tipo', 'General'),
                    tipo='fijo' if 'fijo' in row.get('tipo', '').lower() else 'variable'
                )

                Gasto.objects.create(
                    tipo_gasto=tipo,
                    monto=row['monto'],
                    fecha=row['fecha'],
                    descripcion=row.get('descripcion', ''),
                    tiene_factura=row.get('factura', False)
                )

            print("✔ Gastos importados")
        except Exception as e:
            print("⚠ Error gastos:", e)

    # -------------------------
    # COMPRAS
    # -------------------------
    def importar_compras(self, xls):
        try:
            df = xls.parse('compras')

            for _, row in df.iterrows():
                proveedor, _ = Proveedor.objects.get_or_create(
                    nombre=row.get('proveedor', 'General')
                )

                compra = Compra.objects.create(
                    proveedor=proveedor,
                    fecha=row['fecha'],
                    total=row.get('total', 0)
                )

                producto = Producto.objects.filter(nombre=row['producto']).first()

                if producto:
                    DetalleCompra.objects.create(
                        compra=compra,
                        producto=producto,
                        cantidad=row.get('cantidad', 1),
                        costo=row.get('costo', 0)
                    )

            print("✔ Compras importadas")
        except Exception as e:
            print("⚠ Error compras:", e)

    # -------------------------
    # VENTAS
    # -------------------------
    def importar_ventas(self, xls):
        try:
            df = xls.parse('ventas')

            for _, row in df.iterrows():
                venta = Venta.objects.create(
                    fecha=row['fecha'],
                    total=row.get('total', 0)
                )

                producto = Producto.objects.filter(nombre=row['producto']).first()

                if producto:
                    DetalleVenta.objects.create(
                        venta=venta,
                        producto=producto,
                        cantidad=row.get('cantidad', 1),
                        precio=row.get('precio', 0)
                    )

            print("✔ Ventas importadas")
        except Exception as e:
            print("⚠ Error ventas:", e)