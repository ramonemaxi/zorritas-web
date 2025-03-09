
from django.urls import path
from admin_adminlte import views
from. import views


urlpatterns = [
path('ventas/', views.listar_clientes, name='listar_clientes'),
path('ventas/<int:cliente_id>', views.listar_clientes, name='listar_clientes_prendas'),
path('registrar_venta/', views.registrar_venta, name='registrar_venta')
]