from django.shortcuts import render
from ingresos.models import Prendas, Clientes
from django.db.models import Sum
from django.utils.timezone import now, timedelta
import json
# from django.contrib.auth.decorators import user_passes_test

# def es_superadmin(user):
#     return user.is_superuser

# #crar vista de index
# @user_passes_test(es_superadmin)
def index(request):
    
    hoy = now().date()
    hoy = hoy - timedelta(days=62)
    inicio = hoy - timedelta(days=56)  # Últimos 7 días

    # Agrupar por fecha_venta y sumar los precios
    ventas = (
        Prendas.objects.filter(fecha_venta__range=[inicio, hoy])
        .values("fecha_venta")
        .annotate(total_ventas=Sum("precio"))
        .order_by("fecha_venta")
    )

    # Crear listas para Chart.js
    labels = []
    data = []

    # Asegurar que todos los días están en la lista
    for i in range(7):
        dia = inicio + timedelta(days=i)
        labels.append(dia.strftime("%d-%m"))  # Formato DD-MM
        total = next((v["total_ventas"] for v in ventas if v["fecha_venta"] == dia), 0)
        data.append(total)

    context = {
        'total_prendas': Prendas.total_prendas() ,
        'total_ingresos': Prendas.objects.aggregate(Sum('precio'))['precio__sum'] or 0,
        'total_clientes': Clientes.total_clientes(),
        'labels': labels,
        'data': data

    }
    print(context['labels'])
    #renderizar la plantilla con los datos
    return render(request, 'dashboard/index.html', context)


