from django import forms
from .models import Venta

class VentaForm(forms.ModelForm):
    class Meta:
        model = Venta
        fields = ['total']
        widgets = {
            'total': forms.NumberInput(attrs={'class': 'form-control'})
        }