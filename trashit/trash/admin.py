from django.contrib.gis.admin import OSMGeoAdmin
from .models import TrashSpecificities

@admin.register(Shop)
class ShopAdmin(OSMGeoAdmin):
    list_display = ('trash_type', 'point_field')
