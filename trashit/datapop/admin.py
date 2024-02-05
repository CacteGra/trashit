from django.contrib import admin
from django.contrib.gis.admin import OSMGeoAdmin
from .models import Pointfield

@admin.register(Pointfield)
class IssueAdmin(OSMGeoAdmin):
    list_display = ('trashpecificities', 'o_field')
