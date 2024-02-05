from django.contrib.gis.admin import OSMGeoAdmin
from .models import Pointfield

@admin.register(Shop)
class IssueAdmin(OSMGeoAdmin):
    list_display = ('trashpecificities', 'o_field')
