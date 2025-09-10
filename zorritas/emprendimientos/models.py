from django.db import models
from simple_history.models import HistoricalRecords
from datetime import date
from datetime import datetime
# Create your models here.


class Clientes(models.Model):
    nombre = models.CharField(max_length=100)
    email = models.CharField(max_length=100, null=True, blank=True)
    telefono = models.CharField(max_length=20, null=True, blank=True)
    instagram = models.CharField(max_length=100, null=True, blank=True)
    alias = models.CharField(max_length=100, null=True, blank=True)
    anotaciones = models.TextField(blank=True, null=True)
    history = HistoricalRecords()  # Habilita el historial
    
    def __str__(self):
        return self.nombre
    
    @staticmethod
    def total_clientes():
        return Clientes.objects.all().count()  # Suma el número de clientes en la base de datos

    
class Prendas(models.Model):
    cliente_id = models.ForeignKey(Clientes, on_delete=models.CASCADE, related_name='prenda')
    descripcion = models.CharField(max_length=100, default=None)
    # unidades = models.IntegerField()
    # unidades_totales = models.IntegerField(default=0)
    fecha_venta = models.DateField(null=True, blank=True)
    precio = models.IntegerField()
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
    @staticmethod
    def total_prendas():
        return Prendas.objects.filter(fecha_venta__isnull=True).count()  # Suma el número de prendas en la base de datos
    
    @staticmethod
    def total_prendas_vendidas_hoy():
        hoy = datetime.now().date()
        return Prendas.objects.filter(fecha_venta=hoy).count()  # Suma el número de prendas vendidas hoy

    



    

