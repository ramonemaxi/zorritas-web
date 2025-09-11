import datetime

from admin_adminlte.forms import (
    LoginForm,
    RegistrationForm,
    UserPasswordResetForm,
    UserSetPasswordForm,
    UserPasswordChangeForm,
)
from django.contrib import messages
from django.contrib.auth import logout
from django.contrib.auth import views as auth_views
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.urls import reverse_lazy
from django.views.generic import DeleteView, CreateView, UpdateView, ListView

from .forms import (
    ClienteForm,
    PrendasFormIngresos,
    PrendasFormUpdateIngresos,
    CobrarPrendasForm,
    ClienteAnotacionesForm
)
from .models import Clientes, Prendas


class CLienteDetalle(ListView):
    model = Clientes
    template_name = "ingresos/info_cliente.html"
    context_object_name = "cliente"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["cliente_actual"] = self._obtener_cliente_actual()
        prendas = self._obtener_prendas(context["cliente_actual"])

        # Calcular totales monetarios
        context.update(self._calcular_totales_monetarios(prendas))

        # Calcular estadísticas de ganancias
        context.update(self._calcular_estadisticas_ganancias(prendas))

        # Calcular estadísticas mensuales
        context.update(self._calcular_estadisticas_mensuales(prendas))

        # Calcular estadísticas de prendas
        context.update(self._calcular_estadisticas_prendas(prendas))

        # Calcular tiempo desde última venta
        context['tiempo_desde_ultima_venta'] = self._calcular_tiempo_ultima_venta(prendas)

        return context

    def _obtener_cliente_actual(self):
        return Clientes.objects.get(id=self.kwargs.get("pk"))

    @staticmethod
    def _obtener_prendas(cliente):
        return Prendas.objects.filter(cliente_id=cliente)

    @staticmethod
    def _calcular_totales_monetarios(prendas):
        prendas_pendientes = [p for p in prendas if p.fecha_venta and not p.fecha_cobro]
        return {
            'total_efectivo': round(sum(p.precio_efectivo for p in prendas_pendientes), 2),
            'total_credito': round(sum(p.precio_credito for p in prendas_pendientes), 2)
        }

    @staticmethod
    def _calcular_estadisticas_ganancias(prendas):
        total_vendidas = round(sum(p.precio - p.precio_efectivo for p in prendas if p.fecha_venta), 2)
        total_sin_vender = round(sum(p.precio - p.precio_efectivo for p in prendas if not p.fecha_venta), 2)
        total_cobradas = round(sum(p.precio_efectivo for p in prendas if p.fecha_cobro), 2)
        total_sin_cobrar = round(sum(p.precio_efectivo for p in prendas if not p.fecha_cobro), 2)
        return {
            'label_zorritas': ['Vendido', 'Por Vender'],
            'data_zorritas': [total_vendidas, total_sin_vender],
            'label_cliente': ['Cobrado', 'Por Cobrar'],
            'data_cliente': [total_cobradas, total_sin_cobrar]
        }

    def _calcular_estadisticas_mensuales(self, prendas):
        anio_actual = datetime.date.today().year
        return {
            'label_mes': ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio',
                          'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre'],
            'año_actual': anio_actual,
            'año_anterior': anio_actual - 1,
            'dos_años': anio_actual - 2,
            'data_mes': self._ventas_por_año(prendas, anio_actual),
            'data_mes_anio_pasado': self._ventas_por_año(prendas, anio_actual - 1),
            'data_mes_2_años': self._ventas_por_año(prendas, anio_actual - 2)
        }

    # noinspection NonAsciiCharacters
    @staticmethod
    def _ventas_por_año(prendas, año):
        return [sum(1 for p in prendas if p.fecha_venta and
                    p.fecha_venta.month == mes and
                    p.fecha_venta.year == año)
                for mes in range(1, 13)]

    @staticmethod
    def _calcular_estadisticas_prendas(prendas):
        total = sum(1 for _ in prendas)
        vendidas = sum(1 for p in prendas if p.fecha_venta)
        sin_vender = total - vendidas
        return {
            'total_prendas': total,
            'total_prendas_vendidas': vendidas,
            'total_prendas_sin_vender': sin_vender,
            'porcentaje_prendas_vendidas': round(vendidas / total * 100, 2) if total else 0,
            'porcentaje_prendas_sin_vender': round(sin_vender / total * 100, 2) if total else 0,
            'porcentaje': [
                round(vendidas / total * 100, 2) if total else 0,
                round(sin_vender / total * 100, 2) if total else 0
            ]
        }

    @staticmethod
    def _calcular_tiempo_ultima_venta(prendas):
        prendas_vendidas = [p for p in prendas if p.fecha_venta]
        if prendas_vendidas:
            return max(prendas_vendidas, key=lambda p: p.fecha_venta).tiempo_desde_ultima_venta()
        return None

# Create your views here.

class ListaClientes(LoginRequiredMixin, ListView):
    model = Clientes
    template_name = "ingresos/clientes/listarClientes.html"
    context_object_name = "clientes"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        cliente_id = self.kwargs.get('pk')
        cliente = self.get_cliente(cliente_id)
        prendas = self.get_prendas(cliente_id)

        context.update({
            'historial_prenda': self.get_historial_prendas(cliente_id),
            'fecha_predeterminada': datetime.date.today().strftime('%Y-%m-%d'),
            'pestania': self.get_pestania_activa(),
            'cliente_actual': cliente,
            'prendas': prendas,
            'cliente_form': ClienteForm(),
            'prenda_form': self.get_prenda_form(cliente),
            'segment': 'ingresos',
            'hay_anotacion': self.tiene_anotaciones(cliente),
            'cliente_form_anotaciones': ClienteAnotacionesForm(instance=cliente),
        })

        # Agregar métricas de prendas
        metricas_prendas = self.calcular_metricas_prendas(prendas)
        context.update(metricas_prendas)

        return context

    @staticmethod
    def get_cliente(cliente_id):
        return Clientes.objects.filter(id=cliente_id).first()

    @staticmethod
    def get_prendas(cliente_id):
        return Prendas.objects.filter(cliente_id=cliente_id)

    @staticmethod
    def get_historial_prendas(cliente_id):
        return (Prendas.history.filter(cliente_id=cliente_id)
                .order_by('-history_date'))

    def get_pestania_activa(self):
        pestania = self.request.session.get('pestania_activa', 'stock')
        self.request.session.pop('pestania_activa', None)
        return pestania

    @staticmethod
    def get_prenda_form(cliente):
        return PrendasFormIngresos(initial={'cliente_id': cliente})

    @staticmethod
    def tiene_anotaciones(cliente):
        return bool(cliente and cliente.anotaciones and cliente.anotaciones.strip())

    @staticmethod
    def calcular_metricas_prendas(prendas):
        prendas_vendidas = [p for p in prendas if p.fecha_venta is not None]
        prendas_no_cobradas = [p for p in prendas_vendidas if p.fecha_cobro is None]

        return {
            'prendas_en_stock': [p for p in prendas if p.fecha_venta is None],
            'prendas_cobradas': [p for p in prendas if p.fecha_cobro is not None],
            'prendas_no_cobradas': prendas_no_cobradas,
            'total_prendas_vendidas': len(prendas_vendidas),
            'total_prendas_a_cobrar': len(prendas_no_cobradas),
            'total_efectivo': round(sum(p.precio_efectivo for p in prendas_no_cobradas), 2),
            'total_credito': round(sum(p.precio_credito for p in prendas_no_cobradas), 2)
        }


# clase para crar cliente
class ClienteCreateView(CreateView):
    model = Clientes
    form_class = ClienteForm
    template_name = "ingresos/clientes/listarClientes.html"

    def form_valid(self, form):
        # Verifica si el formulario es válido
        if form.is_valid():
            self.object = form.save()
            # redirigir a detalle_cliente con el id del cliente creado
            return redirect("cliente_detalle", pk=self.object.id)
        else:
            return self.form_invalid(form)


class ClienteUpdateView(UpdateView):
    model = Clientes
    form_class = ClienteForm
    template_name = "ingresos/clientes/listarClientes.html"
    context_object_name = "cliente"

    def form_valid(self, form):
        # Verifica si el formulario es válido
        if form.is_valid():
            self.object = form.save()
            # redirigir a detalle_cliente con el id del cliente creado
            return redirect("cliente_detalle", pk=self.object.id)
        else:
            return self.form_invalid(form)


class ClienteDeleteView(DeleteView):
    model = Clientes
    success_url = reverse_lazy("clientes_lista")

    def form_valid(self, form):
        print(messages.error)
        return super().form_valid(form)


# crear prenda
class PrendaCreateView(CreateView):
    model = Prendas
    form_class = PrendasFormIngresos
    template_name = "clientes/listarClientes.html"
    context_object_name = "prenda"
    success_url = reverse_lazy("cliente_detalle")

    def form_valid(self, form):
        # Verifica si el formulario es válido
        if form.is_valid():
            self.object = form.save()
            
            # redirigir a detalle_cliente con el id del cliente creado
            return redirect("cliente_detalle", pk=self.object.cliente_id_id)
        else:
            return self.form_invalid(form)



# editar prenda
class PrendaUpdateView(UpdateView):
    model = Prendas
    form_class = PrendasFormUpdateIngresos
    context_object_name = "prenda"

    def get_initial(self):
        # Establece el valor inicial de cliente_id al cliente actual de la prenda
        initial = super().get_initial()
        initial["cliente_id"] = self.object.cliente_id  # Mantiene el cliente asociado
        return initial

    def form_valid(self, form):
        # No es necesario cambiar el cliente_id, se mantiene el valor del cliente ya asociado
        self.object = form.save()
        return redirect("cliente_detalle", pk=self.object.cliente_id.pk)

    def form_invalid(self, form):
        print(form.errors)
        return redirect("cliente_detalle", pk=self.object.cliente_id.pk)


# eliminar prenda
class PrendaDeleteView(DeleteView):
    model = Prendas

    # redirigir a lista_prendas
    def get_success_url(self):
        return reverse("cliente_detalle", kwargs={"pk": self.object.cliente_id.pk})



def cobrar_prendas(request, cliente_id):

    cliente = get_object_or_404(Clientes, id=cliente_id)
    if request.method == "POST":
        form = CobrarPrendasForm(request.POST, cliente=cliente)
        if form.is_valid():
            prendas_cobradas = form.cleaned_data["prendas"]
            total = sum(prenda.precio for prenda in prendas_cobradas)

            # Marcar como cobradas en la base de datos
            prendas_cobradas.update(cobrada=True)

            return render(
                request,
                "clientes/confirmacion.html",
                {"total": total, "cliente_actual": cliente},
            )

    else:
        form = CobrarPrendasForm(cliente=cliente)

    return render(
        request, "clientes/cobrar_prendas.html", {"form": form, "cliente": cliente}
    )

def confirmar_venta(request, pk):
    prenda = get_object_or_404(Prendas, pk=pk)
    
    if request.method == 'POST':
        prenda.marcar_como_vendida()
        request.session['pestania_activa'] = 'stock' #Almacena el estado en la sesión.
        return redirect("cliente_detalle", pk=prenda.cliente_id.pk)
    return render(request, 'ingresos/prendas/confirmar_venta.html', {'prenda': prenda})

def confirmar_desventa(request, pk):
    prenda = get_object_or_404(Prendas, pk=pk)
    if request.method == 'POST':
        prenda.marcar_como_desvendida()
        request.session['pestania_activa'] = 'no_cobrada' #Almacena el estado en la sesión.
        return redirect("cliente_detalle", pk=prenda.cliente_id.pk)
    return render(request, 'ingresos/prendas/confirmar_desventa.html', {'prenda': prenda})

#funcion para marcar como cobrada y no cobrada
def confirmar_cobro(request, pk):
    prenda = get_object_or_404(Prendas, pk=pk)
    if request.method == 'POST':
        prenda.marcar_como_cobrada()
        request.session['pestania_activa'] = 'no_cobrada'
        return redirect("cliente_detalle", pk=prenda.cliente_id.pk)
    return render(request, 'ingresos/prendas/confirmar_cobro.html', {'prenda': prenda})

def confirmar_descobro(request, pk):
    prenda = get_object_or_404(Prendas, pk=pk)
    if request.method == 'POST':
        prenda.marcar_como_descobrada()
        request.session['pestania_activa'] = 'cobrada'
        return redirect("cliente_detalle", pk=prenda.cliente_id.pk)
    return render(request, 'ingresos/prendas/confirmar_descobro.html', {'prenda': prenda})

def guardar_anotaciones(request, cliente_id):
    cliente = get_object_or_404(Clientes, id=cliente_id)
    form = ClienteAnotacionesForm(request.POST, instance=cliente)
    if form.is_valid():
        request.session['pestania_activa'] = 'anotaciones'
        form.save()
    return redirect('cliente_detalle', pk=cliente.id)

class PrendaUpdateViewTodas(UpdateView):
    model = Prendas
    form_class = PrendasFormUpdateIngresos
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
        
        return redirect("cliente_detalle", pk=self.object.cliente_id.pk)

    def form_invalid(self, form):
        self.request.session['pestania_activa'] = 'todas'
        
        print(form.errors)
        return redirect("cliente_detalle", pk=self.object.cliente_id.pk)


# eliminar prenda
class PrendaDeleteViewTodas(DeleteView):
    model = Prendas
    
    # redirigir a lista_prendas
    def get_success_url(self):
        self.request.session['pestania_activa'] = 'todas'
        return redirect("cliente_detalle", kwargs={"pk": self.object.cliente_id.pk})

# Authentication
def register(request):
    if request.method == "POST":
        form = RegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            print("Account created successfully!")
            return redirect("/accounts/login/")
        else:
            print("Registration failed!")
    else:
        form = RegistrationForm()

    context = {"form": form}
    return render(request, "accounts/register.html", context)

class UserLoginView(auth_views.LoginView):
    template_name = "accounts/login.html"
    form_class = LoginForm
    def get_success_url(self):
        redirect_to = self.get_redirect_url()
        if redirect_to:
            return redirect_to
        return reverse_lazy("clientes_lista")



class UserPasswordResetView(auth_views.PasswordResetView):
    template_name = "accounts/forgot-password.html"
    form_class = UserPasswordResetForm


class UserPasswordResetViewV1(auth_views.PasswordResetView):
    template_name = "pages/examples/forgot-password.html"
    form_class = UserPasswordResetForm


class UserPasswordResetViewV2(auth_views.PasswordResetView):
    template_name = "pages/examples/forgot-password-v2.html"
    form_class = UserPasswordResetForm


class UserPasswordResetConfirmView(auth_views.PasswordResetConfirmView):
    template_name = "accounts/recover-password.html"
    form_class = UserSetPasswordForm


class UserPasswordChangeView(auth_views.PasswordChangeView):
    template_name = "accounts/password_change.html"
    form_class = UserPasswordChangeForm


class UserPasswordChangeViewV1(auth_views.PasswordChangeView):
    template_name = "pages/examples/recover-password.html"
    form_class = UserPasswordChangeForm


class UserPasswordChangeViewV2(auth_views.PasswordChangeView):
    template_name = "pages/examples/recover-password-v2.html"
    form_class = UserPasswordChangeForm


def user_logout_view(request):
    logout(request)
    return redirect("index")


# pages
# def index(request):
#   context = {
#     'parent': 'dashboard',
#     'segment': 'dashboardv1'
#   }
#   return render(request, 'pages/index.html', context)


def index2(request):
    context = {"parent": "dashboard", "segment": "dashboardv2"}
    return render(request, "pages/index2.html", context)


def index3(request):
    context = {"parent": "dashboard", "segment": "dashboardv3"}
    return render(request, "pages/index3.html", context)


def widgets(request):
    context = {"parent": "", "segment": "widgets"}
    return render(request, "pages/widgets.html", context)


# EXAMPLES





def examples_gallery(request):
    context = {"parent": "", "segment": "gallery"}
    return render(request, "pages/gallery.html", context)


def examples_kanban(request):
    context = {"parent": "", "segment": "kanban_board"}
    return render(request, "pages/kanban.html", context)


# Mailbox


def mailbox_inbox(request):
    context = {"parent": "mailbox", "segment": "inbox"}
    return render(request, "pages/mailbox/mailbox.html", context)


def mailbox_compose(request):
    context = {"parent": "mailbox", "segment": "compose"}
    return render(request, "pages/mailbox/compose.html", context)


def mailbox_read_mail(request):
    context = {"parent": "mailbox", "segment": "read_mail"}
    return render(request, "pages/mailbox/read-mail.html", context)


# Pages -- Examples


def examples_invoice(request):
    context = {"parent": "pages", "segment": "invoice"}
    return render(request, "pages/examples/invoice.html", context)


def invoice_print(request):
    context = {"parent": "pages", "segment": "invoice_print"}
    return render(request, "pages/examples/invoice-print.html", context)


def examples_profile(request):
    context = {"parent": "pages", "segment": "profile"}
    return render(request, "pages/examples/profile.html", context)


def examples_e_commerce(request):
    context = {"parent": "pages", "segment": "ecommerce"}
    return render(request, "pages/examples/e-commerce.html", context)


def examples_projects(request):
    context = {"parent": "pages", "segment": "projects"}
    return render(request, "pages/examples/projects.html", context)


def examples_project_add(request):
    context = {"parent": "pages", "segment": "project_add"}
    return render(request, "pages/examples/project-add.html", context)


def examples_project_edit(request):
    context = {"parent": "pages", "segment": "project_edit"}
    return render(request, "pages/examples/project-edit.html", context)


def examples_project_detail(request):
    context = {"parent": "pages", "segment": "project_detail"}
    return render(request, "pages/examples/project-detail.html", context)


def examples_contacts(request):
    context = {"parent": "pages", "segment": "contacts"}
    return render(request, "pages/examples/contacts.html", context)


def examples_faq(request):
    context = {"parent": "pages", "segment": "faq"}
    return render(request, "pages/examples/faq.html", context)


def examples_contact_us(request):
    context = {"parent": "pages", "segment": "contact_us"}
    return render(request, "pages/examples/contact-us.html", context)


# Extra -- login & Registration v1
# def login_v1(request):
#   context = {
#     'parent': '',
#     'segment': ''
#   }
#   return render(request, 'pages/examples/login.html', context)

# def login_v2(request):
#   context = {
#     'parent': '',
#     'segment': ''
#   }
#   return render(request, 'pages/examples/login-v2.html', context)

# def registration_v1(request):
#   context = {
#     'parent': '',
#     'segment': ''
#   }
#   return render(request, 'pages/examples/register.html', context)

# def registration_v2(request):
#   context = {
#     'parent': '',
#     'segment': ''
#   }
#   return render(request, 'pages/examples/register-v2.html', context)

# def forgot_password_v1(request):
#   context = {
#     'parent': '',
#     'segment': ''
#   }
#   return render(request, 'pages/examples/forgot-password.html', context)

# def forgot_password_v2(request):
#   context = {
#     'parent': '',
#     'segment': ''
#   }
#   return render(request, 'pages/examples/forgot-password-v2.html', context)

# def recover_password_v1(request):
#   context = {
#     'parent': '',
#     'segment': ''
#   }
#   return render(request, 'pages/examples/recover-password.html', context)

# def recover_password_v2(request):
#   context = {
#     'parent': '',
#     'segment': ''
#   }
#   return render(request, 'pages/examples/recover-password-v2.html', context)


def lockscreen(request):
    context = {"parent": "", "segment": ""}
    return render(request, "pages/examples/lockscreen.html", context)


def legacy_user_menu(request):
    context = {"parent": "extra", "segment": "legacy_user"}
    return render(request, "pages/examples/legacy-user-menu.html", context)


def language_menu(request):
    context = {"parent": "extra", "segment": "legacy_menu"}
    return render(request, "pages/examples/language-menu.html", context)


def error_404(request, exception=None):
    context = {"parent": "extra", "segment": "error_404"}
    return render(request, "pages/404.html", context, status=404)


def error_500(request):
    context = {"parent": "extra", "segment": "error_500"}
    return render(request, "pages/examples/500.html", context)


def pace(request):
    context = {"parent": "extra", "segment": "pace"}
    return render(request, "pages/examples/pace.html", context)


def blank_page(request):
    context = {"parent": "extra", "segment": "blank_page"}
    return render(request, "pages/examples/blank.html", context)


def starter_page(request):
    context = {"parent": "extra", "segment": "starter_page"}
    return render(request, "pages/examples/starter.html", context)


# Search


def search_simple(request):
    context = {"parent": "search", "segment": "search_simple"}
    return render(request, "pages/search/simple.html", context)


def search_enhanced(request):
    context = {"parent": "search", "segment": "search_enhanced"}
    return render(request, "pages/search/enhanced.html", context)


def simple_results(request):
    context = {"parent": "", "segment": ""}
    return render(request, "pages/search/simple-results.html", context)


def enhanced_results(request):
    context = {"parent": "", "segment": ""}
    return render(request, "pages/search/enhanced-results.html", context)


# MISCELLANEOUS


def iframe(request):
    context = {"parent": "", "segment": ""}
    return render(request, "pages/search/iframe.html", context)


# Charts


def chartjs(request):
    context = {"parent": "charts", "segment": "chartjs"}
    return render(request, "pages/charts/chartjs.html", context)


def flot(request):
    context = {"parent": "charts", "segment": "flot"}
    return render(request, "pages/charts/flot.html", context)


def inline(request):
    context = {"parent": "charts", "segment": "inline"}
    return render(request, "pages/charts/inline.html", context)


def uplot(request):
    context = {"parent": "charts", "segment": "uplot"}
    return render(request, "pages/charts/uplot.html", context)


def profile(request):
    context = {"parent": "pages", "segment": "profile"}
    return render(request, "pages/examples/profile.html", context)


# Layout
def top_navigation(request):
    context = {"parent": "layout", "segment": "top_navigation"}
    return render(request, "pages/layout/top-nav.html", context)


def top_nav_sidebar(request):
    context = {"parent": "layout", "segment": "top navigation with sidebar"}
    return render(request, "pages/layout/top-nav-sidebar.html", context)


def boxed(request):
    context = {"parent": "layout", "segment": "boxed_layout"}
    return render(request, "pages/layout/boxed.html", context)


def fixed_sidebar(request):
    context = {"parent": "layout", "segment": "fixed_layout"}
    return render(request, "pages/layout/fixed-sidebar.html", context)


def fixed_sidebar_custom(request):
    context = {"parent": "layout", "segment": "layout_cuastom"}
    return render(request, "pages/layout/fixed-sidebar-custom.html", context)


def fixed_topnav(request):
    context = {"parent": "layout", "segment": "fixed_topNav"}
    return render(request, "pages/layout/fixed-topnav.html", context)


def fixed_footer(request):
    context = {"parent": "layout", "segment": "fixed_footer"}
    return render(request, "pages/layout/fixed-footer.html", context)


def collapsed_sidebar(request):
    context = {"parent": "layout", "segment": "collapsed_sidebar"}
    return render(request, "pages/layout/collapsed-sidebar.html", context)


# UI Elements


def ui_general(request):
    context = {"parent": "ui", "segment": "general"}
    return render(request, "pages/UI/general.html", context)


def ui_icons(request):
    context = {"parent": "ui", "segment": "icons"}
    return render(request, "pages/UI/icons.html", context)


def ui_buttons(request):
    context = {"parent": "ui", "segment": "buttons"}
    return render(request, "pages/UI/buttons.html", context)


def ui_sliders(request):
    context = {"parent": "ui", "segment": "sliders"}
    return render(request, "pages/UI/sliders.html", context)


def ui_modals_alerts(request):
    context = {"parent": "ui", "segment": "modals_alerts"}
    return render(request, "pages/UI/modals.html", context)


def ui_navbar_tabs(request):
    context = {"parent": "ui", "segment": "navbar_tabs"}
    return render(request, "pages/UI/navbar.html", context)


def ui_timeline(request):
    context = {"parent": "ui", "segment": "timeline"}
    return render(request, "pages/UI/timeline.html", context)


def ui_ribbons(request):
    context = {"parent": "ui", "segment": "ribbons"}
    return render(request, "pages/UI/ribbons.html", context)


# Forms


def form_general(request):
    context = {"parent": "forms", "segment": "form_general"}
    return render(request, "pages/forms/general.html", context)


def form_advanced(request):
    context = {"parent": "forms", "segment": "advanced_form"}
    return render(request, "pages/forms/advanced.html", context)


def form_editors(request):
    context = {"parent": "forms", "segment": "text_editors"}
    return render(request, "pages/forms/editors.html", context)


def form_validation(request):
    context = {"parent": "forms", "segment": "validation"}
    return render(request, "pages/forms/validation.html", context)


# Table


def table_simple(request):
    context = {"parent": "tables", "segment": "simple_table"}
    return render(request, "pages/tables/simple.html", context)


def table_data(request):
    context = {"parent": "tables", "segment": "data_table"}
    return render(request, "pages/tables/data.html", context)


def table_jsgrid(request):
    context = {"parent": "tables", "segment": "jsGrid"}
    return render(request, "pages/tables/jsgrid.html", context)
