from django import forms
from ingresos.models import Prendas
from django.utils.translation import gettext_lazy as _

#crear formulario de venta de una prenda
class VentaPrendaForm(forms.ModelForm):
    class Meta:
        model = Prendas
        fields = ['fecha_venta']
        
    fecha_venta  = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'type': 'date',
            'class': 'form-control',
            'autocomplete': 'off', 
            'autofocus': True, 
            'id': 'fecha_venta', 
        })
    )
    