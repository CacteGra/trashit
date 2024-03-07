from django.contrib.gis.geos import GEOSGeometry

from datapop.models import Polygonfield
from trash.models import CollectArea

def main(pk):
    collect_area = CollectArea.objects.get(pk=pk)
    polygon_field = collect_area.polygonfield
    raw_data = polygon_field.raw_data.replace(' ', '-')
    raw_data = raw_data.replace(',', ' ')
    raw_data = raw_data.replace('-', ',')
    polygon_field.o_field = GEOSGeometry('POLYGON ({})'.format(raw_data), srid=4326)
    polygon_field.save()