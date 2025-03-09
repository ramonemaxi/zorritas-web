from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, PasswordChangeForm, SetPasswordForm, PasswordResetForm, UsernameField
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _
import datetime

from .models import Clientes, Prendas

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
    class Meta:
        model = Prendas
        fields = ['descripcion', 'precio', 'fecha_ingreso', 'cliente_id']
        widgets = {
            'descripcion': forms.Textarea(attrs={
                'class': 'form-control', 
                'id': 'descripcion', 
                'placeholder': 'Descripción de la prenda', 
                'rows': 3}),
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
        })

        
    )
    
class PrendasFormUpdateIngresos(forms.ModelForm):
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
        

            
class CobrarPrendasForm(forms.Form):
    
    
    
    prendas = forms.ModelMultipleChoiceField(
        #dar formato de form control
        label='Prendas a cobrar',  # Cambia el nombre del campo en el formulario

        queryset=Prendas.objects.none(),  # Se llenará dinámicamente
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'multiple-checkbox', 
                                                   'id': 'prendas', 
                                                    'placeholder': 'Selecciona las prendas a cobrar',
                                                     'type': 'checkbox',
                                                     'multiple': 'true',
                                                     'name': 'prendas',
                                                     
}),
        required=True
    )
    def __init__(self, *args, cliente=None, **kwargs):
        super().__init__(*args, **kwargs)
        if cliente:
            self.fields['prendas'].queryset = Prendas.objects.filter(fecha_venta__isnull=False, cobrada=False, cliente_id=cliente.id)
























class RegistrationForm(UserCreationForm):
  password1 = forms.CharField(
      label=_("Password"),
      widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Password'}),
  )
  password2 = forms.CharField(
      label=_("Password Confirmation"),
      widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Retype password'}),
  )

  class Meta:
    model = User
    fields = ('username', 'email', )

    widgets = {
      'username': forms.TextInput(attrs={
          'class': 'form-control',
          'placeholder': 'Username'
      }),
      'email': forms.EmailInput(attrs={
          'class': 'form-control',
          'placeholder': 'Email'
      })
    }

class LoginForm(AuthenticationForm):
    username = UsernameField(widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'Username'
    }))
    password = forms.CharField(max_length=50, widget=forms.PasswordInput(attrs={
        'class': 'form-control',
        'placeholder': 'Password'
    }))


class UserPasswordResetForm(PasswordResetForm):
  email = forms.EmailField(widget=forms.EmailInput(attrs={
    'class': 'form-control',
    'placeholder': 'Email'
  }))

class UserSetPasswordForm(SetPasswordForm):
    new_password1 = forms.CharField(max_length=50, widget=forms.PasswordInput(attrs={
        'class': 'form-control',
        'placeholder': 'New Password'
    }), label="New Password")
    new_password2 = forms.CharField(max_length=50, widget=forms.PasswordInput(attrs={
        'class': 'form-control',
        'placeholder': 'Confirm New Password'
    }), label="Confirm New Password")
    

class UserPasswordChangeForm(PasswordChangeForm):
    old_password = forms.CharField(max_length=50, widget=forms.PasswordInput(attrs={
        'class': 'form-control',
        'placeholder': 'Old Password'
    }), label='Old Password')
    new_password1 = forms.CharField(max_length=50, widget=forms.PasswordInput(attrs={
        'class': 'form-control',
        'placeholder': 'New Password'
    }), label="New Password")
    new_password2 = forms.CharField(max_length=50, widget=forms.PasswordInput(attrs={
        'class': 'form-control',
        'placeholder': 'Confirm New Password'
    }), label="Confirm New Password")