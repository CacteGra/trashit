from datapop.models import RegisterAPI, Pointfield
from trash.models import TrashSpecificities
from django.contrib.gis.geos import Point

from OSMPythonTools.nominatim import Nominatim
from OSMPythonTools.overpass import overpassQueryBuilder, Overpass

def main():
    register_apis = RegisterAPI.objects.filter(api_type='OSM')
    nominatim = Nominatim()
    for register_api in register_apis:
        areaId = nominatim.query('{}, {}'.format(register_api.city, register_api.country)).areaId()
        nominatim = Nominatim()
        overpass = Overpass()
        query = overpassQueryBuilder(area=areaId, elementType='node', selector='"amenity"="waste_basket"', out='body')
        result = overpass.query(query)
        r = result.elements()
        for i in r:
            point = Point(i.lat(), i.lon(), srid=4326)
            PointField.objects.get_or_create(o_field=point)
            TrashSpecificities.objects.get_or_create(point_field=point_field)
        query = overpassQueryBuilder(area=areaId, elementType='node', selector='"amenity"="recycling"', out='body')
        result = overpass.query(query)
        r = result.elements()
        for i in r:
            point = Point(i.lat(), i.lon(), srid=4326)
            d = i.tags()
            for key, value in d.items():
                if "recycling:" in key and value == 'yes':
                    waste_type = key.replace("recycling:", '')
            point = Point(i.lat(), i.lon(), srid=4326)
            point_field = PointField.objects.get_or_create(o_field=point)
            TrashSpecificities.objects.get_or_create(point_field=point_field, trash_type=waste_type)
                    
