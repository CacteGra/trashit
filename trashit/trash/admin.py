from django.contrib.gis.admin import OSMGeoAdmin
from .models import TrashSpecificities

@admin.register(Shop)
class IssueAdmin(OSMGeoAdmin):
    list_display = ('trash_type', 'point_field')
