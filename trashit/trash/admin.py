from django.contrib import admin
from django.contrib.gis.admin import OSMGeoAdmin
from .models import TrashSpecificities, TheType
from modeltranslation.admin import TranslationAdmin


@admin.register(TrashSpecificities)
class TrashIssueAdmin(OSMGeoAdmin):
    list_display = ('trash_type', 'map_point')

    def map_point(self, obj):
        return obj.point_field.o_field

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        print(queryset.count())
        queryset = queryset.filter(reported=True)
        print(queryset.count())
        return queryset


class TheTypeAdmin(TranslationAdmin):
    pass
admin.site.register(TheType, TheTypeAdmin)