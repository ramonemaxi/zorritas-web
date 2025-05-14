from django.shortcuts import render
from .models import Event
import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import datetime
from django.utils import timezone

# Create your views here.
def examples_calendar(request):
    context = {"parent": "", "segment": "calendar"}
    return render(request, "calendario/calendar.html", context)
# Create your views here.
def event_list(request):
    events = list(Event.objects.values("id", "title", "start", "end", "backgroundColor", "borderColor", "allDay"))
    print(events)
    return JsonResponse(events, safe=False)

@csrf_exempt
def save_event(request):
    if request.method == "POST":
        data = json.loads(request.body)

        # Verificamos si hay un id en los datos para saber si es un evento nuevo o uno que hay que actualizar
        event_id = data.get("id", None)

        # Intentamos parsear el campo "start"
        try:
            start = datetime.datetime.strptime(data["start"], "%Y-%m-%dT%H:%M:%S%z")
        except ValueError:
            start = datetime.datetime.strptime(data["start"], "%Y-%m-%d").date()

        end = None
        if data.get("end"):
            try:
                end = datetime.datetime.strptime(data["end"], "%Y-%m-%dT%H:%M:%S%z")
            except ValueError:
                end = datetime.datetime.strptime(data["end"], "%Y-%m-%d").date()

        # Convertir a aware si es necesario
        if isinstance(start, datetime.datetime) and start.tzinfo is None:
            start = timezone.make_aware(start)
        if end and isinstance(end, datetime.datetime) and end.tzinfo is None:
            end = timezone.make_aware(end)

        # Si tenemos un id, intentamos actualizar el evento existente
        if event_id:
            try:
                event = Event.objects.get(id=event_id)  # Buscamos el evento por su id
                event.title = data["title"]
                event.start = start
                event.end = end
                event.allDay = data["allDay"]
                event.save()  # Guardamos los cambios
                return JsonResponse({"message": "Evento actualizado", "id": event.id}, status=200)
            except Event.DoesNotExist:
                return JsonResponse({"error": "Evento no encontrado"}, status=404)
        else:
            # Si no tiene id, significa que es un nuevo evento, así que lo creamos
            event = Event.objects.create(
                title=data["title"],
                start=start,
                end=end,
                allDay=data["allDay"],
                backgroundColor=data.get("backgroundColor"),
                borderColor=data.get("borderColor")
            )
            return JsonResponse({"message": "Evento creado", "id": event.id}, status=201)


@csrf_exempt
def delete_event(request):
    if request.method == "POST":
        try:
            # Obtén los datos enviados en el body
            data = json.loads(request.body)
            print("Data received:", data)  # Para ver qué datos estás recibiendo
            
            event_id = data.get("id", None)
            if not event_id:
                return JsonResponse({"error": "No event ID provided"}, status=400)

            try:
                # Intenta obtener el evento con el ID proporcionado
                event = Event.objects.get(id=event_id)
                event.delete()
                return JsonResponse({"message": "Evento eliminado con éxito"}, status=200)
            except Event.DoesNotExist:
                return JsonResponse({"error": "Evento no encontrado"}, status=404)

        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON format"}, status=400)