from django.db import models

class ConfiguracionCosteo(models.Model):
    gastos_fijos_por_kg = models.DecimalField(max_digits=10, decimal_places=2, default=480)
    gastos_variables_por_kg = models.DecimalField(max_digits=10, decimal_places=2, default=50)

    def __str__(self):
        return f"Costeo (fijo: {self.gastos_fijos_por_kg} | variable: {self.gastos_variables_por_kg})"
