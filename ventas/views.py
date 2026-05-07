from django.shortcuts import render, redirect
from .forms import VentaForm


def crear_venta(request):
    form = VentaForm(request.POST or None)

    if form.is_valid():
        form.save()
        return redirect('/')

    return render(request, 'ventas/crear_venta.html', {'form': form})