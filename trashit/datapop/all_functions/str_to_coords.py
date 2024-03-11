from django.contrib.gis.geos import Point
from django.contrib.gis.geos import GEOSGeometry

from datapop.models import Polygonfield
from trash.models import CollectArea

def main(pk):
    collect_area = CollectArea.objects.get(pk=pk)
    raw_data = collect_area.raw_data.replace(' ', '/')
    raw_data = raw_data.replace(',', ' ')
    raw_data = raw_data.replace('/', ', ')
    polygon = 'POLYGON (({}))'.format(raw_data)
    print(polygon)
    polygon_field, created = Polygonfield.objects.get_or_create(o_field=GEOSGeometry(polygon, srid=4326))
    collect_area.polygon_field = polygon_field
    collect_area.save()