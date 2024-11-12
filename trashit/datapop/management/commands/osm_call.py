from datapop.models import RegisterAPI, Pointfield
from trash.models import TrashSpecificities, TrashType, TheType, ContainerType
from django.contrib.gis.geos import Point

from OSMPythonTools.nominatim import Nominatim
from OSMPythonTools.overpass import overpassQueryBuilder, Overpass

def main():
    register_apis = RegisterAPI.objects.filter(api_type='OSM')
    nominatim = Nominatim()
    overpass = Overpass()
    print("osm")
    for register_api in register_apis:
        areaId = nominatim.query('{}, {}'.format(register_api.city, register_api.country)).areaId()
        query = overpassQueryBuilder(area=areaId, elementType='node', selector='"amenity"="waste_basket"', out='body')
        result = overpass.query(query)
        r = result.elements()
        for i in r:
            point = Point(i.lon(), i.lat(), srid=4326)
            point_field, created = Pointfield.objects.get_or_create(o_field=point)
            d = i.tags()
            try:
                waste_type = d['waste']
            except KeyError:    
                waste_type = "waste"
                continue
            the_type, created = TheType.objects.get_or_create(the_type=waste_type)
            container, created = ContainerType.objects.get_or_create(container_type='waste_basket')
            trash_type, created = TrashType.objects.get_or_create(the_type=the_type, container_type=container)
            try:
                t = TrashSpecificities.objects.get(point_field=point_field)
                if not t.trash_type:
                    t.trash_type.add(trash_type)
            except TrashSpecificities.DoesNotExist:
                t = TrashSpecificities.objects.create(point_field=point_field)
                t.trash_type.add(trash_type)
        query = overpassQueryBuilder(area=areaId, elementType='node', selector='"amenity"="waste_disposal"', out='body')
        result = overpass.query(query)
        r = result.elements()
        for i in r:
            point = Point(i.lon(), i.lat(), srid=4326)
            point_field, created = Pointfield.objects.get_or_create(o_field=point)
            d = i.tags()
            try:
                waste_type = d['waste']
            except KeyError:
                waste_type = "waste"
                continue
            the_type, created = TheType.objects.get_or_create(the_type=waste_type)
            container, created = ContainerType.objects.get_or_create(container_type='waste_basket')
            trash_type, created = TrashType.objects.get_or_create(the_type=the_type, container_type=container)
            try:
                t = TrashSpecificities.objects.get(point_field=point_field)
                if not t.trash_type:
                    t.trash_type.add(trash_type)
            except TrashSpecificities.DoesNotExist:
                t = TrashSpecificities.objects.create(point_field=point_field)
                t.trash_type.add(trash_type)
        query = overpassQueryBuilder(area=areaId, elementType='node', selector='"amenity"="recycling"', out='body')
        result = overpass.query(query)
        r = result.elements()
        for i in r:
            point = Point(i.lon(), i.lat(), srid=4326)
            point_field, created = Pointfield.objects.get_or_create(o_field=point)
            d = i.tags()
            waste_type = None
            for key, value in d.items():
                underground = False
                if "location:" in key and value == 'underground':
                    underground = True
                if ("recycling:" in key and value == 'yes'):
                    waste_type = key.replace("recycling:", '') 
            if waste_type == None:
                try:
                    waste_type = d['name']
                except KeyError:
                    try:
                        waste_type = d['operator']
                    except:
                        continue
                the_type, created = TheType.objects.get_or_create(the_type=waste_type)
                container, created = ContainerType.objects.get_or_create(container_type='waste_basket')
                trash_type, created = TrashType.objects.get_or_create(the_type=the_type, container_type=container)
            else:
                the_type, created = TheType.objects.get_or_create(the_type=waste_type)
                container, created = ContainerType.objects.get_or_create(container_type='waste_basket')
                trash_type, created = TrashType.objects.get_or_create(the_type=the_type, container_type=container)
            try:
                t = TrashSpecificities.objects.get(point_field=point_field)
                if not t.trash_type:
                    t.trash_type.add(trash_type)
            except TrashSpecificities.DoesNotExist:
                t = TrashSpecificities.objects.create(point_field=point_field)
                t.trash_type.add(trash_type)
    register_api.first = False
    register_api.save()