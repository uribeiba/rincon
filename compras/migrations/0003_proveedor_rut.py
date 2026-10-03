# Generated manually for the first intelligent invoice integration.
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('compras', '0002_alter_compra_options_alter_detallecompra_options_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='proveedor',
            name='rut',
            field=models.CharField(
                blank=True,
                max_length=12,
                null=True,
                unique=True,
                verbose_name='RUT',
            ),
        ),
    ]
