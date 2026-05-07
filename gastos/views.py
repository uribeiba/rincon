from django.shortcuts import render

def gastos_view(request):
    return render(request, 'gastos/gastos.html')