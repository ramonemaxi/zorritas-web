from django.urls import path
from. import views

urlpatterns = [
    path("calendario/", views.examples_calendar, name='examples_calendar'),
    path("events/", views.event_list, name="event_list"),
    path("events/save/", views.save_event, name="save_event"),
    path('events/delete/', views.delete_event, name='delete_event')
]