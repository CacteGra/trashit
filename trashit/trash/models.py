from django.db import models
from datapop.models import Pointfield

# Create your models here.

class TrashSpecificities(models.Model):
    id = models.AutoField(primary_key=True, editable=False)
    trash_type = models.ForeignKey('TrashType', on_delete=models.CASCADE, null=True, blank=True)
    point_field = models.OneToOneField(Pointfield, on_delete=models.CASCADE)
    photo = models.ImageField(upload_to="media", null=True, blank=True)
    reported = models.BooleanField(default=False)

class TrashType(models.model):
    collect_area = models.ForeignKey('CollectArea', on_delete=models.CASCADE, null=True, blank=True)
    trash_type = models.CharField(max_length=1000, null=True, blank=True)
    container_type = models.CharField(max_length=1000, null=True, blank=True)
    underground = models.BooleanField(default=False)
    area = models.BooleanField(default=False)
    name = models.CharField(max_length=1000, null=True, blank=True)
    operator = models.CharField(max_length=1000, null=True, blank=True)
    DAYS_CHOICES = [
        ("Monday", "Monday"),
        ("Tuesday", "Tuesday"),
        ("Wednesday", "Wednesday"),
        ("Thursday", "Thursday"),
        ("Friday", "Friday"),
        ("Saturday", "Saturday"),
        ("Sunday", "Sunday"),
    ]
    days = models.CharField(
        max_length=23,
        choices=DAYS_CHOICES,
        null=True, blank=True
    )
    hours = models.TimeField(null=True, blank=True)

class CollectArea(models.Model):
    id = models.AutoField(primary_key=True, editable=False)
    raw_data = models.CharField(max_length=1000, null=True, blank=True)
    polygon_field = models.OneToOneField(Pointfield, on_delete=models.CASCADE)
