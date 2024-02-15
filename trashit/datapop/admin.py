from django.contrib import admin
from django.contrib.gis.admin import OSMGeoAdmin
from .models import Pointfield

@admin.register(Pointfield)
class PointfieldAdmin(OSMGeoAdmin):
    list_display = ('o_field', 'trash_type')

    def trash_type(self, obj):
        return obj.trashspecificities.trash_type

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        print(queryset.count())
        queryset = queryset.filter(trashspecificities__reported=True)
        print(queryset.count())
        return queryset
