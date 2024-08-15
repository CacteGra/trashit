from django.contrib.gis.db import models
from datapop.models import Pointfield, Polygonfield

# Create your models here.

class TrashSpecificities(models.Model):
    id = models.AutoField(primary_key=True, editable=False)
    the_type = models.ForeignKey('TheType', on_delete=models.CASCADE, null=True, blank=True)
    trash_type = models.ForeignKey('TrashType', on_delete=models.CASCADE, null=True, blank=True)
    point_field = models.OneToOneField(Pointfield, on_delete=models.CASCADE)
    photo = models.ImageField(upload_to="media", null=True, blank=True)
    from_local_api = models.BooleanField(default=False)
    reported = models.BooleanField(default=False)

class Weekday(models.Model):
    day = models.CharField(max_length=15, null=True, blank=True)

    def __str__(self):
        return "%s" % (self.day)

class TrashType(models.Model):
    id = models.AutoField(primary_key=True, editable=False)
    collect_area = models.ForeignKey('CollectArea', on_delete=models.CASCADE, null=True, blank=True)
    the_type = models.ForeignKey('TheType', on_delete=models.CASCADE, null=True, blank=True)
    container_type = models.ForeignKey('ContainerType', on_delete=models.CASCADE, null=True, blank=True)
    underground = models.BooleanField(default=False)
    area = models.BooleanField(default=False)
    name = models.CharField(max_length=1000, null=True, blank=True)
    operator = models.CharField(max_length=1000, null=True, blank=True)
    day = models.ManyToManyField(Weekday, blank=True)
    hour = models.TimeField(null=True, blank=True)

class Packaging(models.Model):
    id = models.AutoField(primary_key=True, editable=False)
    component = models.CharField(max_length=1000, null=True, blank=True)
    the_type = models.OneToOneField('TheType', on_delete=models.CASCADE, null=True, blank=True)

class Wrapper(models.Model):
    id = models.AutoField(primary_key=True, editable=False)
    the_time = models.DateTimeField(auto_now_add=True)
    code = models.CharField(max_length=1000, null=True, blank=True)
    packaging = models.ManyToManyField(Packaging, blank=True)

class TheType(models.Model):
    the_type = models.CharField(max_length=100, null=True, blank=True)
    
    def __str__(self):
        return "%s" % (self.the_type)

class ContainerType(models.Model):
    container_type = models.CharField(max_length=100, null=True, blank=True)
    def __str__(self):
        return "%s" % (self.container_type)

class CollectArea(models.Model):
    id = models.AutoField(primary_key=True, editable=False)
    raw_data = models.CharField(max_length=10000, null=True, blank=True)
    quarter = models.CharField(max_length=50, null=True, blank=True)
    polygon_field = models.OneToOneField(Polygonfield, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return "%s" % (self.quarter)
