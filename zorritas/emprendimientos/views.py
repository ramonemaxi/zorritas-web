import datetime

from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.urls import reverse_lazy
from django.views.generic import DeleteView, CreateView, UpdateView, ListView

from .forms import (
    ClienteForm,
    PrendasFormIngresos,
    PrendasFormUpdateEmprendimientos,
    ClienteAnotacionesForm
)
from .models import Clientes, Prendas


# Create your views here.

class CLienteDetalle(ListView):
    model = Clientes
    context_object_name = "cliente"

    def get_context_data(self, **kwargs):
        # obtener el cliente actual por ID de cliente
        context = super().get_context_data(**kwargs)
        # obtener el cliente actual por ID de cliente
        context["cliente_actual"] = Clientes.objects.get(id=self.kwargs.get("pk"))
        prendas = Prendas.objects.filter(
            cliente_id=context["cliente_actual"])

        context['total_efectivo'] = round(sum(prenda.precio for prenda in prendas
                                              if prenda.fecha_venta is not None
                                              and prenda.fecha_cobro is None), 2)
        total_ganancias_vendidas = round(sum(prenda.precio for prenda in prendas
                                             if prenda.fecha_venta is not None), 2)
        total_ganancias_sin_vender = round(sum(prenda.precio for prenda in prendas
                                               if prenda.fecha_venta is None), 2)
        context['label_ganancias'] = ['Vendidas', 'Sin Vender']
        context['data_ganancias'] = [total_ganancias_vendidas, total_ganancias_sin_vender]

        context['total_credito'] = round(sum(prenda.precio for prenda in prendas
                                             if prenda.fecha_venta is not None
                                             and prenda.fecha_cobro is None), 2)

        context['total_prendas_vendidas'] = sum(1 for prenda in prendas if prenda.fecha_venta is not None)

        context['total_prendas_sin_vender'] = sum(1 for prenda in prendas if prenda.fecha_venta is None)

        return context


class ListaEmprendimientos(LoginRequiredMixin, ListView):
    # agregar formulario de cliente
    model = Clientes
    template_name = "emprendimientos/clientes/listarClientes.html"
    context_object_name = "clientes"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Consultar directamente el historial, no solo las prendas activas
        historial_prenda = Prendas.history.filter(cliente_id=self.kwargs.get('pk'))

        # Ordenar por fecha descendente
        historial_prenda = historial_prenda.order_by('-history_date')

        # Pasar al contexto
        context["historial_prenda"] = historial_prenda

        context['fecha_predeterminada'] = datetime.date.today().strftime('%Y-%m-%d')
        pestania = self.request.session.get('pestania_activa', 'stock')  # Capturar la pestaña
        self.request.session.pop('pestania_activa', None)  # Limpiar la sesión
        context['pestania'] = pestania

        # obtener las prendas por ID de cliente
        cliente_id = self.kwargs.get('pk')
        print(cliente_id)
        context['cliente_actual'] = Clientes.objects.filter(id=self.kwargs.get('pk')).first()
        prendas = Prendas.objects.filter(cliente_id=self.kwargs.get('pk'))
        context['prendas'] = prendas
        # Agregar un formulario vacío para crear nuevos clientes
        context["cliente_form"] = ClienteForm()
        cliente = Clientes.objects.filter(id=self.kwargs.get('pk')).first()
        if cliente:
            context['hay_anotacion'] = bool(cliente.anotaciones and cliente.anotaciones.strip())

        context["cliente_form_anotaciones"] = ClienteAnotacionesForm(instance=cliente)
        context['prenda_form'] = PrendasFormIngresos(
            initial={'cliente_id': Clientes.objects.filter(id=self.kwargs.get('pk')).first()})
        context['segment'] = 'emprendimientos'

        context['prendas_en_stock'] = [prenda for prenda in prendas if prenda.fecha_venta is None]
        context['prendas_no_cobradas'] = [prenda for prenda in prendas if prenda.fecha_cobro is None
                                          and prenda.fecha_venta is not None]
        context["prendas_cobradas"] = [prenda for prenda in prendas if prenda.fecha_cobro is not None]
        context['total_efectivo'] = round(sum(prenda.precio for prenda in prendas
                                              if prenda.fecha_venta is not None
                                              and prenda.fecha_cobro is None), 2)
        context["total_prendas_en_stock"] = sum(1 for prenda in prendas if prenda.fecha_venta is None)

        context["total_prendas_a_cobrar"] = sum(1 for prenda in prendas if prenda.fecha_cobro is None
                                                and prenda.fecha_venta is not None)

        return context


# clase para crar cliente
class ClienteCreateView(CreateView):
    model = Clientes
    form_class = ClienteForm
    template_name = "emprendimientos/clientes/listarClientes.html"

    def form_valid(self, form):
        # Verifica si el formulario es válido
        if form.is_valid():
            self.object = form.save()
            # redirigir a detalle_cliente con el id del cliente creado
            return redirect("emprendimiento:emprendimientos_detalle", pk=self.object.id)
        else:
            return self.form_invalid(form)


class ClienteUpdateView(UpdateView):
    model = Clientes
    form_class = ClienteForm
    template_name = "emprendimientos/clientes/listarClientes.html"
    context_object_name = "cliente"

    def form_valid(self, form):
        # Verifica si el formulario es válido
        if form.is_valid():
            self.object = form.save()
            # redirigir a detalle_cliente con el id del cliente creado
            return redirect("emprendimiento:emprendimientos_detalle", pk=self.object.id)
        else:
            return self.form_invalid(form)


class ClienteDeleteView(DeleteView):
    model = Clientes
    success_url = reverse_lazy("emprendimiento:emprendimientos_lista")

    def form_valid(self, form):
        return super().form_valid(form)


def confirmar_venta(request, pk):
    prenda = get_object_or_404(Prendas, pk=pk)

    if request.method == 'POST':
        prenda.marcar_como_vendida()
        request.session['pestania_activa'] = 'stock'  # Almacena el estado en la sesión.
        return redirect("emprendimiento:emprendimientos_detalle", pk=prenda.cliente_id.pk)
    return render(request, 'emprendimientos/prendas/confirmar_venta.html', {'prenda': prenda})


def confirmar_desventa(request, pk):
    prenda = get_object_or_404(Prendas, pk=pk)
    if request.method == 'POST':
        prenda.marcar_como_desvendida()
        request.session['pestania_activa'] = 'no_cobrada'  # Almacena el estado en la sesión.
        return redirect("emprendimiento:emprendimientos_detalle", pk=prenda.cliente_id.pk)
    return render(request, 'emprendimientos/prendas/confirmar_desventa.html', {'prenda': prenda})


class PrendaCreateView(CreateView):
    model = Prendas
    form_class = PrendasFormIngresos
    context_object_name = "prenda"
    success_url = reverse_lazy("emprendimiento:emprendimientos_detalle")

    def form_valid(self, form):
        # Verifica si el formulario es válido
        if form.is_valid():
            cliente_id = form.cleaned_data['cliente_id']
            descripcion = form.cleaned_data['descripcion']
            unidades = form.cleaned_data['unidades']  # Obtiene la cantidad de unidades del formulario
            precio = form.cleaned_data['precio']
            fecha_ingreso = form.cleaned_data['fecha_ingreso']

            # Crea múltiples instancias de Prenda
            prendas_creadas = []  # Para luego pasar al detalle
            for _ in range(unidades):
                prenda = Prendas.objects.create(
                    cliente_id=cliente_id,
                    descripcion=descripcion,
                    precio=precio,
                    fecha_ingreso=fecha_ingreso
                    # fecha_cobro=None,  # No es necesario establecerlo aquí, puede ser null=True

                )
                prendas_creadas.append(prenda)  # Guarda la prenda creada

            # Redirige al detalle del cliente
            return redirect("emprendimiento:emprendimientos_detalle", pk=cliente_id.pk)
        else:
            return self.form_invalid(form)

    def form_invalid(self, form):
        # Esto es importante para manejar los errores del formulario.
        print("Formulario inválido:", form.errors)  # Imprime los errores en la consola
        return super().form_invalid(form)


# editar prenda
class PrendaUpdateView(UpdateView):
    model = Prendas
    form_class = PrendasFormUpdateEmprendimientos
    context_object_name = "prenda"

    def get_initial(self):
        # Establece el valor inicial de cliente_id al cliente actual de la prenda
        initial = super().get_initial()
        initial["cliente_id"] = self.object.cliente_id  # Mantiene el cliente asociado
        return initial

    def form_valid(self, form):
        # No es necesario cambiar el cliente_id, se mantiene el valor del cliente ya asociado
        self.object = form.save()
        return redirect("emprendimiento:emprendimientos_detalle", pk=self.object.cliente_id.pk)

    def form_invalid(self, form):
        print(form.errors)
        return redirect("emprendimiento:emprendimientos_detalle", pk=self.object.cliente_id.pk)


# eliminar prenda
class PrendaDeleteView(DeleteView):
    model = Prendas

    # redirigir a lista_prendas
    def get_success_url(self):
        return reverse("emprendimiento:emprendimientos_detalle", kwargs={"pk": self.object.cliente_id.pk})


# funcion para marcar como cobrada y no cobrada
def confirmar_cobro(request, pk):
    prenda = get_object_or_404(Prendas, pk=pk)
    if request.method == 'POST':
        prenda.marcar_como_cobrada()
        request.session['pestania_activa'] = 'no_cobrada'
        return redirect("emprendimiento:emprendimientos_detalle", pk=prenda.cliente_id.pk)
    return render(request, 'emprendimientos/prendas/confirmar_cobro.html', {'prenda': prenda})


def confirmar_descobro(request, pk):
    prenda = get_object_or_404(Prendas, pk=pk)
    if request.method == 'POST':
        prenda.marcar_como_descobrada()
        request.session['pestania_activa'] = 'cobrada'
        return redirect("emprendimiento:emprendimientos_detalle", pk=prenda.cliente_id.pk)
    return render(request, 'emprendimientos/prendas/confirmar_descobro.html', {'prenda': prenda})


def guardar_anotaciones(request, cliente_id):
    cliente = get_object_or_404(Clientes, id=cliente_id)
    form = ClienteAnotacionesForm(request.POST, instance=cliente)
    request.session['pestania_activa'] = 'anotaciones'
    if form.is_valid():
        form.save()
    return redirect('emprendimiento:emprendimientos_detalle', pk=cliente.id)  # o la vista que estés usando


class PrendaUpdateViewTodas(UpdateView):
    model = Prendas
    form_class = PrendasFormUpdateEmprendimientos
    context_object_name = "prenda"

    def get_initial(self):
        # Establece el valor inicial de cliente_id al cliente actual de la prenda
        initial = super().get_initial()
        initial["cliente_id"] = self.object.cliente_id  # Mantiene el cliente asociado
        return initial

    def form_valid(self, form):
        self.object = form.save()
        self.request.session['pestania_activa'] = 'todas'

        # No es necesario cambiar el cliente_id, se mantiene el valor del cliente ya asociado

        return redirect("emprendimiento:emprendimientos_detalle", pk=self.object.cliente_id.pk)

    def form_invalid(self, form):

        self.request.session['pestania_activa'] = 'todas'

        print(form.errors)
        return redirect("emprendimiento:emprendimientos_detalle", pk=self.object.cliente_id.pk)


# eliminar prenda
class PrendaDeleteViewTodas(DeleteView):
    model = Prendas

    # redirigir a lista_prendas
    def get_success_url(self):
        return reverse("emprendimiento:emprendimientos_detalle", kwargs={"pk": self.object.cliente_id.pk})
