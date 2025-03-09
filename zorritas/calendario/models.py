from django.db import models

# Create your models here.

class Event(models.Model):
    title = models.CharField(max_length=200)
    start = models.DateTimeField(null=True, blank=True)
    end = models.DateTimeField(null=True, blank=True)
    allDay = models.BooleanField(default=True)
    backgroundColor = models.CharField(max_length=7, default="#0073b7")  # Color por defecto
    borderColor = models.CharField(max_length=7, default="#0073b7")
    text_color = models.CharField(max_length=7, blank=True)

    def __str__(self):
        return self.title