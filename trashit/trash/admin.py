from django.contrib import admin
from django.contrib.gis.admin import OSMGeoAdmin
from .models import TrashSpecificities

@admin.register(TrashSpecificities)
class TrashIssueAdmin(OSMGeoAdmin):
    list_display = ('trash_type', 'point_field')
