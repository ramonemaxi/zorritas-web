from django.contrib import admin
from django.db.models import Q
from django.urls import reverse
from django.utils.html import format_html
from django.http import HttpResponse
import csv

from .models import Clientes, Prendas


class TieneAnotacionesFilter(admin.SimpleListFilter):
    title = 'Anotaciones'
    parameter_name = 'anotaciones'

    def lookups(self, request, model_admin):
        return (
            ('si', 'Con anotaciones'),
            ('no', 'Sin anotaciones'),
        )

    def queryset(self, request, queryset):
        if self.value() == 'si':
            return queryset.exclude(anotaciones__isnull=True).exclude(anotaciones__exact='')
        if self.value() == 'no':
            return queryset.filter(Q(anotaciones__isnull=True) | Q(anotaciones__exact=''))
        return queryset


class ContactoFilter(admin.SimpleListFilter):
    title = 'Contacto'
    parameter_name = 'contacto'

    def lookups(self, request, model_admin):
        return (
            ('email', 'Con email'),
            ('telefono', 'Con teléfono'),
            ('instagram', 'Con Instagram'),
            ('sin_contacto', 'Sin ningún contacto'),
        )

    def queryset(self, request, queryset):
        if self.value() == 'email':
            return queryset.exclude(email__isnull=True).exclude(email__exact='')
        if self.value() == 'telefono':
            return queryset.exclude(telefono__isnull=True).exclude(telefono__exact='')
        if self.value() == 'instagram':
            return queryset.exclude(instagram__isnull=True).exclude(instagram__exact='')
        if self.value() == 'sin_contacto':
            return queryset.filter(
                Q(email__isnull=True) | Q(email__exact=''),
                Q(telefono__isnull=True) | Q(telefono__exact=''),
                Q(instagram__isnull=True) | Q(instagram__exact=''),
            )
        return queryset


@admin.register(Clientes)
class ClientesAdmin(admin.ModelAdmin):
    # columnas visibles en la lista
    list_display = (
        "id",
        "nombre",
        "email",
        "telefono",
        "instagram",
        "alias",
        "tiene_anotaciones",
        "total_prendas",
        "ver_prendas",
    )

    # qué campos se pueden editar en línea en la lista (no pueden ser links)
    list_editable = ("email", "telefono", "instagram", "alias")

    # por qué campos buscar
    search_fields = ("nombre", "email", "telefono", "instagram", "alias")
    search_help_text = "Buscar por nombre, email, teléfono, Instagram o alias"

    # filtros laterales
    list_filter = (TieneAnotacionesFilter, ContactoFilter)

    # orden por defecto y paginación
    ordering = ("nombre", "id")
    list_per_page = 50

    # optimizaciones: si luego agregas FK a Cliente, aquí podrías usar list_select_related

    # acciones masivas
    actions = ("limpiar_anotaciones", "exportar_csv")

    # métodos auxiliares para columnas calculadas
    @admin.display(boolean=True, description="Tiene anotaciones")
    def tiene_anotaciones(self, obj: Clientes):
        return bool(obj.anotaciones and obj.anotaciones.strip())

    @admin.display(description="Total prendas")
    def total_prendas(self, obj: Clientes):
        # related_name='prenda'
        return obj.prenda.count()

    @admin.display(description="Prendas (admin)")
    def ver_prendas(self, obj: Clientes):
        url = (
            reverse("admin:ingresos_prendas_changelist")
            + f"?cliente_id__id__exact={obj.id}"
        )
        return format_html('<a class="button" href="{}">Ver prendas</a>', url)

    # acciones
    def limpiar_anotaciones(self, request, queryset):
        actualizadas = queryset.update(anotaciones="")
        self.message_user(request, f"Anotaciones limpiadas en {actualizadas} cliente(s).")
    limpiar_anotaciones.short_description = "Limpiar anotaciones seleccionadas"

    def exportar_csv(self, request, queryset):
        response = HttpResponse(content_type="text/csv")
        response["Content-Disposition"] = 'attachment; filename="clientes.csv"'
        writer = csv.writer(response)
        writer.writerow(["ID", "Nombre", "Email", "Teléfono", "Instagram", "Alias", "Tiene anotaciones", "Total prendas"])
        for c in queryset:
            writer.writerow([
                c.id,
                c.nombre,
                c.email or "",
                c.telefono or "",
                c.instagram or "",
                c.alias or "",
                "Sí" if (c.anotaciones and c.anotaciones.strip()) else "No",
                c.prenda.count(),
            ])
        return response
    exportar_csv.short_description = "Exportar a CSV (seleccionados)"


@admin.register(Prendas)
class PrendasAdmin(admin.ModelAdmin):
    list_display = ("id", "descripcion", "cliente_id", "precio", "fecha_venta", "fecha_cobro")
    search_fields = ("descripcion", "cliente_id__nombre")
    list_filter = ("fecha_venta", "fecha_cobro")
    autocomplete_fields = ("cliente_id",)
    ordering = ("-id",)
    list_per_page = 50
