from django.shortcuts import render
from ingresos.models import Prendas as IngresosPrendas, Clientes as IngresosClientes
from emprendimientos.models import Prendas as EmprendimientosPrendas, Clientes as EmprendimientosClientes
from django.db.models import Sum, F
from django.utils.timezone import now, timedelta
from datetime import datetime
import json
from django.utils import timezone
# from django.contrib.auth.decorators import user_passes_test
def index(request):
    return render(request, 'dashboard/index.html')

def dashboard(request):
    dias = 14
    hoy = datetime.now().date()
    inicio = hoy - timedelta(days=dias)  # Últimos 7 días

    # Recuperar las prendas de ambos modelos dentro del rango de fechas
    ingresos_prendas = IngresosPrendas.objects.filter(fecha_venta__range=[inicio, hoy]).order_by('fecha_venta')
    emprendimientos_prendas = EmprendimientosPrendas.objects.filter(fecha_venta__range=[inicio, hoy]).order_by('fecha_venta')

    # Diccionario para almacenar las diferencias por fecha
    diferencias_por_fecha = {}

    # Calcular la diferencia para cada prenda y agrupar por fecha
    def calcular_diferencias(prendas, diferencias_por_fecha):
        for prenda in prendas:
            fecha = prenda.fecha_venta
            if isinstance(prenda, IngresosPrendas):
                diferencia = prenda.ganancia_efectivo
            else:  # Es una EmprendimientosPrenda
                diferencia = prenda.precio * 0.30  # Calcular el 27% de ganancia
            if fecha in diferencias_por_fecha:
                diferencias_por_fecha[fecha] += diferencia
            else:
                diferencias_por_fecha[fecha] = diferencia

    calcular_diferencias(ingresos_prendas, diferencias_por_fecha)
    calcular_diferencias(emprendimientos_prendas, diferencias_por_fecha)

    # Crear listas para Chart.js
    labels = []
    data_diferencia = []

    # Asegurar que todos los días están en la lista
    for i in range(dias+1):
        dia = inicio + timedelta(days=i)
        labels.append(dia.strftime("%d-%m"))  # Formato DD-MM
        diferencia = diferencias_por_fecha.get(dia, 0)  # Obtener la diferencia o 0 si no existe
        data_diferencia.append(diferencia)

    # Calcular totales para ambos modelos
    total_ingresos_prendas = IngresosPrendas.objects.aggregate(Sum('precio'))['precio__sum'] or 0
    total_emprendimientos_prendas = EmprendimientosPrendas.objects.aggregate(Sum('precio'))['precio__sum'] or 0
    total_ingresos = total_ingresos_prendas + total_emprendimientos_prendas

    total_ingresos_prendas_hoy = IngresosPrendas.total_prendas_vendidas_hoy()
    total_emprendimientos_prendas_hoy = EmprendimientosPrendas.total_prendas_vendidas_hoy()
    total_prendas_vendidas_hoy = total_ingresos_prendas_hoy + total_emprendimientos_prendas_hoy
    
    total_ingresos_clientes = IngresosClientes.total_clientes()
    total_emprendimientos_clientes = EmprendimientosClientes.total_clientes()
    total_clientes = total_ingresos_clientes + total_emprendimientos_clientes
    
    # Sumar las ventas de hoy de Ingresos
    ingresos_hoy = int(round(sum(prenda.ganancia_efectivo for prenda in IngresosPrendas.objects.filter(fecha_venta=hoy)), 0))

    # Sumar las ventas de hoy de Emprendimientos y calcular el 30%
    emprendimientos_hoy = EmprendimientosPrendas.objects.filter(fecha_venta=hoy).aggregate(
        total_ventas=Sum('precio')
    )['total_ventas'] or 0
    ganancia_emprendimientos_hoy = emprendimientos_hoy * 0.30

    # Sumar las ventas de Ingresos y la ganancia de Emprendimientos
    total_hoy = ingresos_hoy + ganancia_emprendimientos_hoy
    print(total_hoy)
    context = {
        'total_prendas': IngresosPrendas.total_prendas() + EmprendimientosPrendas.total_prendas(),
        'total_prendas_vendidas_hoy': total_prendas_vendidas_hoy,
        'total_ingresos': total_ingresos,
        'total_clientes': total_clientes,
        'labels': labels,
        'data': data_diferencia,
        'total_hoy': total_hoy

    }

    print(context['labels'])

    return render(request, 'dashboard/dashboard.html', context)
