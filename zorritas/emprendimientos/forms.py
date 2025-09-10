from django import forms
from .models import Clientes, Prendas
import datetime
from django_summernote.widgets import SummernoteWidget

class ClienteForm(forms.ModelForm):
    class Meta:
        model = Clientes
        fields = ['nombre', 'email', 'telefono', 'instagram', 'alias']  # En vez de '__all__'
        
    alias = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'autocomplete': 'off', 
            'autofocus': True, 
            'id': 'alias', 
            'placeholder': 'Alias'}))
    email = forms.CharField(
        required=False,
        widget=forms.EmailInput(attrs={
            'class': 'form-control', 
            'autocomplete': 'off',
            'id': 'email', 
            'placeholder': 'Email'}))
    instagram = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control', 
            'autocomplete': 'off',
            'id': 'instagram',
            'placeholder': 'Instagram'}))
    telefono = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control', 
            'autocomplete': 'off',
            'id': 'telefono',
            'placeholder': 'Telefono'}))
    nombre = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control', 
            'autocomplete': 'off',
            'id': 'nombre', 
            'placeholder': 'Nombre'}))


class PrendasFormIngresos(forms.ModelForm):
    unidades = forms.IntegerField(
        label='Unidades',
        min_value=1,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'id': 'unidades',
            'placeholder': 'Cantidad de unidades'
        })
    )

    class Meta:
        model = Prendas
        fields = ['descripcion', 'precio', 'fecha_ingreso', 'cliente_id']
        widgets = {
            'descripcion': forms.Textarea(attrs={
                'class': 'form-control',
                'id': 'descripcion',
                'placeholder': 'Descripción de la prenda',
                'rows': 3,
                'autofocus': True}),
            'fecha_ingreso': forms.DateInput(attrs={
                'class': 'form-control', 'id': 'fecha_ingreso',
                'placeholder': 'Fecha de ingreso',
                'type': 'date',
                'value': datetime.date.today().strftime('%Y-%m-%d')
            })
        }

    precio = forms.IntegerField(

        label='Precio de la prenda',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'id': 'precio',
            'placeholder': 'Precio de la prenda'
        }))
    
class PrendasFormUpdateEmprendimientos(forms.ModelForm):
    class Meta:
        model = Prendas
        fields = ['descripcion', 'precio', 'fecha_ingreso']
        widgets = {
            'descripcion': forms.Textarea(attrs={
                'class': 'form-control', 
                'id': 'descripcion', 
                'placeholder': 'Descripción de la prenda', 
                'rows': 3}),
            'fecha_ingreso': forms.DateInput(attrs={
                'class': 'form-control', 'id': 'fecha_ingreso', 
                'placeholder': 'Fecha de ingreso', 
                'type': 'date'})
            }
        precio = forms.IntegerField(
        
                label='Precio de la prenda',
                widget=forms.TextInput(attrs={
                    'class': 'form-control',
                    'id': 'precio',
                    'placeholder': 'Precio de la prenda'
                })
            )

class ClienteAnotacionesForm(forms.ModelForm):
    class Meta:
        model = Clientes
        fields = ['anotaciones']
        widgets = {
            'anotaciones': SummernoteWidget(attrs={
                'summernote': {
                    'height': '200px',
                    'width': '100%',
                    'lang': None,
                    'iframe': True,
                    'toolbar': [
                        ['style', ['style']],             # Estilos de encabezado (h1, h2, etc.)
                        ['font', ['bold', 'underline', 'clear']], # Negrita, subrayado, limpiar formato
                        ['fontname', ['fontname']],       # Selección de fuente
                        ['color', ['color']],             # Selector de color de texto y fondo
                        ['para', ['ul', 'ol', 'paragraph']], # Listas y párrafo
                        ['height', ['height']],           # Altura de línea
                        ['table', ['table']],             # Insertar tabla
                        ['insert', [None]], # Insertar enlace, imagen, línea horizontal
                        ['view', ['fullscreen', 'codeview', 'help']], # Ver pantalla completa, código fuente, ayuda
                    ],
                    
                }
            })
        }