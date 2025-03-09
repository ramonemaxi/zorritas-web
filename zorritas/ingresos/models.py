from django.db import models
from simple_history.models import HistoricalRecords
from datetime import date
# Create your models here.


class Clientes(models.Model):
    nombre = models.CharField(max_length=100)
    email = models.CharField(max_length=100, null=True, blank=True)
    telefono = models.CharField(max_length=20, null=True, blank=True)
    instagram = models.CharField(max_length=100, null=True, blank=True)
    alias = models.CharField(max_length=100, null=True, blank=True)
    history = HistoricalRecords()  # Habilita el historial
    
    def __str__(self):
        return self.nombre
    
    def total_clientes():
        return Clientes.objects.all().count()  # Suma el número de clientes en la base de datos

    
class Prendas(models.Model):
    cliente_id = models.ForeignKey(Clientes, on_delete=models.CASCADE, related_name='prenda')
    descripcion = models.CharField(max_length=100)
    precio = models.IntegerField()
    cobrada = models.BooleanField(default=False, null=True, blank=True)
    fecha_venta = models.DateField(null=True, blank=True)
    fecha_ingreso = models.DateField(null=True, blank=True)
    fecha_cobro = models.DateField(null=True, blank=True)
    history = HistoricalRecords()
    
    def __str__(self):
        return self.descripcion
    
    def marcar_como_vendida(self):
        self.fecha_venta = date.today()
        self.save()
        
    def marcar_como_desvendida(self):
        self.fecha_venta = None
        self.save()
        
    def marcar_como_cobrada(self):
        self.fecha_cobro = date.today()
        self.save()
        
    def marcar_como_descobrada(self):
        self.fecha_cobro = None
        self.save()
    
    def fecha_venta_formateada(self):
        if self.fecha_venta:
            return self.fecha_venta.strftime("%d/%m/%Y")
        else:
            return ""  # O algún otro valor por defecto, como "Sin fecha"
    def fecha_ingreso_formateada(self):
        if self.fecha_ingreso:
            return self.fecha_ingreso.strftime("%d/%m/%Y")
        else:
            return ""  # O algún otro valor por defecto, como "Sin fecha"
    def fecha_cobro_formateada(self):
        if self.fecha_cobro:
            return self.fecha_cobro.strftime("%d/%m/%Y")
        else:
            return ""  # O algún otro valor por defecto, como "Sin fecha"
    #sumar todas las prendas
    def total_prendas():
        return Prendas.objects.all().count()  # Suma el número de prendas en la base de datos
    
    @property
    def precio_efectivo(self):
        precio = self.precio
        if precio <= 10000:
            return round(precio * 0.4, 2)
        elif 10500 <= precio <= 20000:
            return round(precio * 0.5, 2)
        elif 20500 <= precio <= 30000:
            return round(precio * 0.6, 2)
        else:  # precio >= 30000
            return round(precio * 0.7, 2)

    @property
    def precio_credito(self):
        precio = self.precio
        if precio <= 10000:
            return round(precio * 0.5, 2)
        elif 10500 <= precio <= 20000:
            return round(precio * 0.5, 2)
        elif 20500 <= precio <= 30000:
            return round(precio * 0.6, 2)
        else:  # precio >= 30000
            return round(precio * 0.7, 2)


    

