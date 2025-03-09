from django.shortcuts import get_object_or_404, redirect, render
from ingresos.models import Clientes, Prendas
from django.http import JsonResponse
from django.shortcuts import render
from ingresos.models import Clientes, Prendas
from django.http import JsonResponse
from ingresos.models import Clientes, Prendas
from django.http import JsonResponse
from .froms import VentaPrendaForm
import datetime as dt

def listar_clientes(request, cliente_id=None):
    fecha_actual = dt.datetime.now().date()
    fecha_formateada = fecha_actual.strftime('%Y-%m-%d')  # Formato de fecha para el input HTML
    query = request.GET.get('q', '')  # Obtiene la consulta de búsqueda

    # Si hay una búsqueda de clientes, filtramos por nombre
    clientes = Clientes.objects.filter(nombre__icontains=query) if query else []
    
    #obtener el cliente actual si se proporciona el id en la URL o en un parámetro GET
    cliente_actual = Clientes.objects.filter(id=cliente_id).first() if cliente_id else None
    
    # Si hay un cliente_id (ya sea en la URL o en un parámetro GET), buscamos sus prendas
    if cliente_id:
        prendas = Prendas.objects.filter(cliente_id=cliente_id)
    else:
        prendas = Prendas.objects.none()  # No mostrar prendas hasta seleccionar un cliente

    venta = VentaPrendaForm()  # Crear una instancia del formulario de venta
    
    # Si la petición es AJAX, devolvemos JSON
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        if cliente_id:
            return JsonResponse({'prendas': list(prendas.values('id', 'nombre', 'descripcion', 'precio'))})
        else:
            return JsonResponse({'clientes': list(clientes.values('id', 'nombre'))})

    # Pasamos los datos al template
    context = {
        'clientes': clientes,
        'cliente_actual': cliente_actual,
        'prendas': prendas,  # Contiene prendas solo si hay cliente_id
        'query': query,
        'venta': venta,
        'cliente_id': cliente_id,
        'fecha_actual': fecha_actual,
        'segment': 'ventas'

    }
    return render(request, 'ventas/listar_clientes.html', context=context)

#registrar venta

def registrar_venta(request):
    if request.method == 'POST':
        #obtener el id del cliente 
        cliente_id = request.POST.get('cliente_id')  # Obtener el ID del cliente desde la solicitud POST
        
        print(cliente_id)  # Imprimir para verificar que se obtiene correctamente

        #instancial la prenda que estoy editando en el formulario y actualizar fecha_venta
        prenda_id = request.POST.get('prenda_id')
        prenda = Prendas.objects.get(id=prenda_id)
        # Actualizar la fecha de venta de la prenda con la fecha_venta que se envia en el form
        fecha_venta = request.POST.get('fecha_venta')
        prenda.fecha_venta = fecha_venta
        if 'borrar_fecha' in request.POST:  # Si se presionó el botón "Eliminar Fecha"
            prenda.fecha_venta = None
            prenda.save()
            return redirect('listar_clientes_prendas', cliente_id=cliente_id)
            
        prenda.save()
        #retornar a listar_clientes con el id del cliente
        return redirect('listar_clientes_prendas', cliente_id=cliente_id)
    
        
            
        
        
            

        
    
    
            


