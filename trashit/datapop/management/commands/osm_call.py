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
        waste_type = "trash"
        areaId = nominatim.query('{}, {}, {}'.format(register_api.city, register_api.state, register_api.country)).areaId()
        query = overpassQueryBuilder(area=areaId, elementType='node', selector='"amenity"="waste_basket"', out='body')
        result = overpass.query(query)
        r = result.elements()
        for i in r:
            type_list = []
            point = Point(i.lon(), i.lat(), srid=4326)
            point_field, created = Pointfield.objects.get_or_create(o_field=point)
            d = i.tags()
            try:
                waste_type = d['waste']
            except KeyError:    
                waste_type = "trash"
            if ";" in waste_type:
                for w in waste_type.split(";"):
                    the_type, created = TheType.objects.get_or_create(the_type=w, is_osm=True)
                    trash_type, created = TrashType.objects.get_or_create(the_type=the_type)
                    type_list.append(trash_type)
            else:
                the_type, created = TheType.objects.get_or_create(the_type=waste_type, is_osm=True)
                trash_type, created = TrashType.objects.get_or_create(the_type=the_type)
            if created:
                if not any(x in waste_type for x in ['waste', 'trash']):
                    the_type.icon = "special-bin"
                    the_type.save()
            try:
                t = TrashSpecificities.objects.get(point_field=point_field)
                if not t.trash_type:
                    if type_list:
                        for a_trash_type in type_list:
                            t.trash_type.add(a_trash_type)
                    else:
                        t.trash_type.add(trash_type)
            except TrashSpecificities.DoesNotExist:
                t = TrashSpecificities.objects.create(point_field=point_field)
                if type_list:
                    for a_trash_type in type_list:
                        t.trash_type.add(a_trash_type)
                else:
                    t.trash_type.add(trash_type)
        query = overpassQueryBuilder(area=areaId, elementType='node', selector='"amenity"="waste_disposal"', out='body')
        result = overpass.query(query)
        r = result.elements()
        for i in r:
            type_list = []
            point = Point(i.lon(), i.lat(), srid=4326)
            point_field, created = Pointfield.objects.get_or_create(o_field=point)
            d = i.tags()
            try:
                waste_type = d['waste']
            except KeyError:
                waste_type = "trash"
            if ";" in waste_type:
                for w in waste_type.split(";"):
                    the_type, created = TheType.objects.get_or_create(the_type=w, is_osm=True)
                    trash_type, created = TrashType.objects.get_or_create(the_type=the_type)
                    type_list.append(trash_type)
            else:
                the_type, created = TheType.objects.get_or_create(the_type=waste_type, is_osm=True)
                trash_type, created = TrashType.objects.get_or_create(the_type=the_type)
            if created:
                if not any(x in waste_type for x in ['waste', 'trash']):
                    the_type.icon = "special-bin"
                    the_type.save()
            try:
                t = TrashSpecificities.objects.get(point_field=point_field)
                if not t.trash_type:
                    if type_list:
                        for a_trash_type in type_list:
                            t.trash_type.add(a_trash_type)
                    else:
                        t.trash_type.add(trash_type)
            except TrashSpecificities.DoesNotExist:
                t = TrashSpecificities.objects.create(point_field=point_field)
                if type_list:
                    for a_trash_type in type_list:
                        t.trash_type.add(a_trash_type)
                else:
                    t.trash_type.add(trash_type)
        query = overpassQueryBuilder(area=areaId, elementType='node', selector='"amenity"="recycling"', out='body')
        result = overpass.query(query)
        r = result.elements()
        for i in r:
            type_list = []
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
                    type_list.append(waste_type)
            if not type_list:
                try:
                    waste_type = d['name']
                except KeyError:
                    try:
                        waste_type = d['operator']
                    except:
                        waste_type = 'recycle'
                the_type, created = TheType.objects.get_or_create(the_type=waste_type, is_osm=True)
                if created:
                    if 'plastic' in waste_type:
                        the_type.icon = 'plastic-bottle'
                        the_type.save()
                    elif 'paper' in waste_type:
                        the_type.icon = 'paper'
                        the_type.save()
                    elif 'magazines' in waste_type:
                        the_type.icon = 'paper'
                        the_type.save()
                    elif 'shoes' in waste_type:
                        the_type.icon = 'shirt'
                        the_type.save()
                    elif 'clothes' in waste_type:
                        the_type.icon = 'shirt'
                        the_type.save()
                    elif 'cans' in waste_type:
                        the_type.icon = 'can'
                        the_type.save()
                    elif 'cardboard' in waste_type:
                        the_type.icon = 'cardboard'
                        the_type.save()
                    elif 'glass' in waste_type:
                        the_type.icon = 'glass-bottle'
                        the_type.save()
                    elif 'oil' in waste_type:
                        the_type.icon = 'special-bin'
                        the_type.save()
                    else:
                        the_type.icon = 'recycle'
                        the_type.save()
                trash_type, created = TrashType.objects.get_or_create(the_type=the_type)
                try:
                    t = TrashSpecificities.objects.get(point_field=point_field)
                    if not t.trash_type:
                        t.trash_type.add(trash_type)
                except TrashSpecificities.DoesNotExist:
                    t = TrashSpecificities.objects.create(point_field=point_field)
                    t.trash_type.add(trash_type)
            else:
                recycle_type = None
                for recycle_type in type_list:
                    the_type, created = TheType.objects.get_or_create(the_type=recycle_type, is_osm=True)
                    if created:
                        if 'plastic' in recycle_type:
                            the_type.icon = 'plastic-bottle'
                            the_type.save()
                        elif 'paper' in recycle_type:
                            the_type.icon = 'paper'
                            the_type.save()
                        elif 'magazines' in recycle_type:
                            the_type.icon = 'paper'
                            the_type.save()
                        elif 'shoes' in recycle_type:
                            the_type.icon = 'shirt'
                            the_type.save()
                        elif 'clothes' in recycle_type:
                            the_type.icon = 'shirt'
                            the_type.save()
                        elif 'cans' in recycle_type:
                            the_type.icon = 'can'
                            the_type.save()
                        elif 'cardboard' in recycle_type:
                            the_type.icon = 'cardboard'
                            the_type.save()
                        elif 'glass' in recycle_type:
                            the_type.icon = 'glass-bottle'
                            the_type.save()
                        elif 'oil' in recycle_type:
                            the_type.icon = 'special-bin'
                            the_type.save()
                        else:
                            the_type.icon = 'recycle'
                            the_type.save()
                    trash_type, created = TrashType.objects.get_or_create(the_type=the_type)
                    try:
                        t = TrashSpecificities.objects.get(point_field=point_field)
                        t.trash_type.add(trash_type)
                    except TrashSpecificities.DoesNotExist:
                        t = TrashSpecificities.objects.create(point_field=point_field)
                        t.trash_type.add(trash_type)
    register_api.first = False
    register_api.save()