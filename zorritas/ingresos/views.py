from django.shortcuts import render, redirect, get_object_or_404
from admin_adminlte.forms import (
    LoginForm,
    RegistrationForm,
    UserPasswordResetForm,
    UserSetPasswordForm,
    UserPasswordChangeForm,
)
from django.contrib.auth import logout
from django.contrib import messages
from django.contrib.auth import views as auth_views

from django.views.generic import DeleteView, CreateView, UpdateView, ListView
from .models import Clientes, Prendas
from .forms import (
    ClienteForm,
    PrendasFormIngresos,
    PrendasFormUpdateIngresos,
    CobrarPrendasForm,
)
from django.urls import reverse_lazy
from django.urls import reverse
from django.db.models import Q, Case, When, FloatField
from django.db.models.functions import Round
import datetime

class CLienteDetalle(ListView):
    model = Clientes
    template_name = "ingresos/info_cliente.html"
    context_object_name = "cliente"

    # obtener el contexto
    def get_queryset(self):
        return Clientes.objects.filter(id=self.kwargs.get("pk"))

    # cuando metodo post capturar los cheks
    def post(self, request, *args, **kwargs):
        # capturar los cheks
        cheks = request.POST.getlist("cheks")
        print(cheks)
        if cheks:
            # Obtener las prendas seleccionadas de la base de datos
            prendas_a_cobrar = Prendas.objects.filter(pk__in=cheks)

            # Actualizar el campo 'cobrada' a True para las prendas seleccionadas
            prendas_a_cobrar.update(cobrada=True)

        return redirect("info_cliente", pk=self.kwargs.get("pk"))

    def get_context_data(self, **kwargs):
        # obtener el cliente actual por id de cliente
        context = super().get_context_data(**kwargs)
        # obtener el cliente actual por id de cliente
        context["cliente_actual"] = Clientes.objects.get(id=self.kwargs.get("pk"))
        # obtener las prendas por id de cliente
        context['prendas_en_stock'] = Prendas.objects.filter(
            cliente_id=self.kwargs.get("pk"), cobrada=False, fecha_venta__isnull=True)
        
        context["prendas"] = Prendas.objects.filter(cliente_id=self.kwargs.get("pk"))
        
        # prendas sin cobrar y con fecha_venta
        context["prendas_a_cobrar"] = Prendas.objects.filter(
            cliente_id=self.kwargs.get("pk"), cobrada=False, fecha_venta__isnull=False
        )
        # prendas con cobrada en true
        context["prendas_cobradas"] = Prendas.objects.filter(
            cliente_id=self.kwargs.get("pk"), cobrada=True
        )
        # prendas con cobrada en false
        context["prendas_no_cobradas"] = Prendas.objects.filter(
            cliente_id=self.kwargs.get("pk"), cobrada=False
        )
        # total prendas sin vender
        context["total_prendas_sin_vender"] = Prendas.objects.filter(
            cliente_id=self.kwargs.get("pk"), fecha_venta__isnull=True
        ).count()
        # total prendas vendidas
        context["total_prendas_vendidas"] = Prendas.objects.filter(
            cliente_id=self.kwargs.get("pk"), fecha_venta__isnull=False
        ).count()
        # total de prendas con fecha de venta
        context["prendas_con_fecha_venta"] = Prendas.objects.filter(
            cliente_id=self.kwargs.get("pk"), fecha_venta__isnull=False
        )
        # total de prendas sin fecha de venta
        context["prendas_sin_fecha_venta"] = Prendas.objects.filter(
            cliente_id=self.kwargs.get("pk"), fecha_venta__isnull=True
        )

        efectivo = 0
        credito = 0
        total_efectivo = 0
        total_credito = 0

        for prenda in context["prendas_no_cobradas"]:
            if prenda.fecha_venta is not None and prenda.cobrada == False:

                precio = prenda.precio

                if precio <= 10000:
                    efectivo = round(precio * 0.4, 2)
                    credito = round(precio * 0.5, 2)
                    
                elif 10500 <= precio <= 20000:
                    efectivo = round(precio * 0.5, 2)
                    credito = round(precio * 0.5, 2)
                    
                elif 20500 <= precio <= 30000:
                    efectivo = round(precio * 0.6, 2)
                    credito = round(precio * 0.6, 2)
                    
                else:  # precio >= 30000
                    efectivo = round(precio * 0.7, 2)
                    credito = round(precio * 0.7, 2)
                    

                # Sumar al total
                total_efectivo += efectivo
                total_credito += credito

        context["total_efectivo"] = total_efectivo
        context["total_credito"] = total_credito
        
        

        return context

# Create your views here.
class ListaClientes2(ListView):
    # agregar formulario de cliente
    model = Clientes
    template_name = "clientes/listarClientes.html"
    context_object_name = "clientes"
    
    def get_context_data(self, **kwargs):
        print("clientes2 view accessed")
        context = super().get_context_data(**kwargs)
        context['fecha_predeterminada'] = datetime.date.today().strftime('%Y-%m-%d')
        pestania = self.request.session.get('pestania_activa', 'todas')  # Capturar la pestaña
        self.request.session.pop('pestania_activa', None)  # Limpiar la sesión
        context['pestania'] = pestania
        #obtener las prendas por id de cliente
        context['cliente_actual'] = Clientes.objects.filter(id=self.kwargs.get('pk')).first()
        context['prendas'] = Prendas.objects.filter(cliente_id=self.kwargs.get('pk'))
        # Agregar un formulario vacío para crear nuevos clientes
        context["cliente_form"] = ClienteForm()
        context['prenda_form'] = PrendasFormIngresos(initial={'cliente_id': Clientes.objects.filter(id=self.kwargs.get('pk')).first()})
        context['segment'] = 'ingresos'
        
        context["prendas_vendidas"] = Prendas.objects.filter(
            cliente_id=self.kwargs.get("pk"), fecha_venta__isnull=False
        )
        
        context['prendas_en_stock'] = Prendas.objects.filter(
            cliente_id=self.kwargs.get("pk"), cobrada=False, fecha_venta__isnull=True)
        
        context["prendas_cobradas"] = Prendas.objects.filter(
            cliente_id=self.kwargs.get("pk"), fecha_cobro__isnull=False, fecha_venta__isnull=False)
        
        context["prendas_no_cobradas"] = Prendas.objects.filter(
            cliente_id=self.kwargs.get("pk"), fecha_cobro=None, fecha_venta__isnull=False)
        
        context["prendas_a_cobrar"] = Prendas.objects.filter(
            cliente_id=self.kwargs.get("pk"), cobrada=False, fecha_venta__isnull=False)
        
        context["total_prendas_vendidas"] = Prendas.objects.filter(
            cliente_id=self.kwargs.get("pk"), fecha_venta__isnull=False
        ).count()
        
        context["total_prendas_a_cobrar"] = Prendas.objects.filter(
            cliente_id=self.kwargs.get("pk"), cobrada=False).count()
        
        
        
        efectivo = 0
        credito = 0
        total_efectivo = 0
        total_credito = 0

        for prenda in context["prendas_no_cobradas"]:
            if prenda.fecha_venta is not None and prenda.cobrada == False:

                precio = prenda.precio

                if precio <= 10000:
                    efectivo = round(precio * 0.4, 2)
                    credito = round(precio * 0.5, 2)
                    
                elif 10500 <= precio <= 20000:
                    efectivo = round(precio * 0.5, 2)
                    credito = round(precio * 0.5, 2)
                    
                elif 20500 <= precio <= 30000:
                    efectivo = round(precio * 0.6, 2)
                    credito = round(precio * 0.6, 2)
                    
                else:  # precio >= 30000
                    efectivo = round(precio * 0.7, 2)
                    credito = round(precio * 0.7, 2)
                    

                # Sumar al total
                total_efectivo += efectivo
                total_credito += credito

        context["total_efectivo"] = total_efectivo
        context["total_credito"] = total_credito
        print(context["total_efectivo"])
        print(context["total_credito"])


        return context
    
# Create your views here.
class ListaClientes(ListView):
    # agregar formulario de cliente
    model = Clientes
    template_name = "ingresos/listar_clientes.html"
    context_object_name = "clientes"

    def get_context_data(self, **kwargs):

        context = super().get_context_data(**kwargs)
        #obtener las prendas por id de cliente
        context['cliente_actual'] = Clientes.objects.filter(id=self.kwargs.get('pk')).first()
        context['prendas'] = Prendas.objects.filter(cliente_id=self.kwargs.get('pk'))
        # Agregar un formulario vacío para crear nuevos clientes
        context["cliente_form"] = ClienteForm()
        context['prenda_form'] = PrendasFormIngresos(initial={'cliente_id': Clientes.objects.filter(id=self.kwargs.get('pk')).first()})
        context['segment'] = 'ingresos'
        return context


# clase para crar cliente
class ClienteCreateView(CreateView):
    model = Clientes
    form_class = ClienteForm
    template_name = "clientes/listarClientes.html"

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
    template_name = "clientes/listarClientes.html"
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
    template_name = "clientes/eliminarCliente.html"
    success_url = reverse_lazy("cliente_detalle")

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
            print(self.object.cliente_id_id)
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
    template_name = "prendas/listarClientes.html"

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


def register_v1(request):
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
    return render(request, "pages/examples/register.html", context)


def register_v2(request):
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
    return render(request, "pages/examples/register-v2.html", context)


class UserLoginView(auth_views.LoginView):
    template_name = "accounts/login.html"
    form_class = LoginForm
    success_url = "/clientes2"
    # agregar esto print(self.request.GET.get('next')) dentro del metodo get
    def get(self, request, *args, **kwargs):
        print(self.request.GET.get('next'))
        print(self.success_url)
        return super().get(request, *args, **kwargs) # Llamar al método get original



class UserLoginViewV1(auth_views.LoginView):
    template_name = "pages/examples/login.html"
    form_class = LoginForm
    success_url = "/clientes2"


class UserLoginViewV2(auth_views.LoginView):
    template_name = "pages/examples/login-v2.html"
    form_class = LoginForm
    success_url = "/clientes2"


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
    return redirect("/accounts/login/")


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


def examples_calendar(request):
    context = {"parent": "", "segment": "calendar"}
    return render(request, "calendar/calendar.html", context)


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


def error_404(request):
    context = {"parent": "extra", "segment": "error_404"}
    return render(request, "pages/examples/404.html", context)


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
