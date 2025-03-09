
from django.urls import path
from admin_adminlte import views
from. import views


urlpatterns = [
path('', views.index, name='index')
]