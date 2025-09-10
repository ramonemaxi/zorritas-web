from. import views
from django.urls import path

app_name = 'emprendimiento'

urlpatterns = [
    # Emprendimientos URLs
    path('clientes/', views.ListaEmprendimientos.as_view(), name='emprendimientos_lista'),
    path('clientes/<int:pk>/', views.ListaEmprendimientos.as_view(), name='emprendimientos_detalle'),
    path('crear/', views.ClienteCreateView.as_view(), name='crear_emprendimiento'),
    path('editar/<int:pk>/', views.ClienteUpdateView.as_view(), name='editar_emprendimiento'),
    path('eliminar/<int:pk>/', views.ClienteDeleteView.as_view(), name='eliminar_emprendimiento'),
    
    path('crear-prenda/', views.PrendaCreateView.as_view(), name='crear_prenda'),
    path('editar-prenda/<int:pk>/', views.PrendaUpdateView.as_view(), name='editar_prenda'),
    path('eliminar-prenda/<int:pk>/', views.PrendaDeleteView.as_view(), name='eliminar_prenda'),
    
    path('editar-prenda-todas/<int:pk>/', views.PrendaUpdateViewTodas.as_view(), name='editar_prenda_todas'),
    path('eliminar-prenda-todas/<int:pk>/', views.PrendaDeleteViewTodas.as_view(), name='eliminar_prenda_todas'),
    
    path('vender-prenda/<int:pk>/', views.confirmar_venta, name='confirmar_venta'),
    path('desvender-prenda/<int:pk>/', views.confirmar_desventa, name='confirmar_desventa'),
    
    path('cobrar-prenda/<int:pk>/', views.confirmar_cobro, name='confirmar_cobro'),
    path('descobrar-prenda/<int:pk>/', views.confirmar_descobro, name='confirmar_descobro'),
    
    path('clientes/<int:cliente_id>/anotaciones/', views.guardar_anotaciones, name='guardar_anotaciones'),
    ]