from time import sleep
import requests
import json
import ast

from django.db.models import Q
from django.contrib.gis.measure import D
from django.core.management.base import BaseCommand, CommandError
from datapop.models import RegisterAPI, RegisterAPIChosen, OperatedField, DataLine, Polygonfield, Textfield
from trash.models import CollectArea
from django.contrib.gis.geos import Point, GEOSGeometry, Polygon, MultiPolygon
from django.utils.module_loading import import_string
from django.utils import timezone
from datetime import timedelta

from trash.models import TrashSpecificities, TrashType, TheType, CollectArea

from . import osm_call, get_csv_data

class Command(BaseCommand):

    def iterate_child(self, parent_pk, children_id_list):
        parent = RegisterAPIChosen.objects.get(pk=parent_pk)
        children = RegisterAPIChosen.objects.filter(children_of=parent_pk)
        for child in children:
            r = RegisterAPIChosen.objects.filter(children_of=child.pk)
            print(r.count())
            if r.count() > 0:
                for child_r in r:
                    self.iterate_child(parent_pk, children_id_list)
                children.exclude(id=child.pk)
        children_id_list.append([list(children.values_list('id', flat=True))])
        return children_id_list

    def get_path(self, child_id, path_list, first_off):
        r = RegisterAPIChosen.objects.get(pk=child_id)
        if not first_off:
            path_list.insert(0, r.pk)
        parent = r.children_of
        if parent and (parent.the_chosen.text_chosen != 'root'):
            self.get_path(parent.id, path_list, False)
        return path_list

    def iterate_data_lines(self, path_list, list_item, l_copy, all_api_pk, line_number=0):
        list_item += 1
        n = list_item
        for path_id in path_list[list_item:]:
            if list_item == 0:
                where_line = 1
            n += 1
            if (type(path_id) is list):
                check_new_data = []
                for data_id in path_id:
                    base_r = RegisterAPIChosen.objects.get(id=data_id)
                    print(base_r.pk)
                    # base_r_line = RegisterAPIChosen.objects.filter(the_chosen__text_chosen=base_r.line_id.the_chosen.text_chosen,the_chosen__value_example=base_r.line_id.the_chosen.value_example,children_of__isnull=False)
                    # base_r_line = base_r_line[0]
                    data = l_copy[(base_r.the_chosen.text_chosen).replace('[0]', '')]
                    field_name = base_r.field_type
                    field_name = field_name[0].upper() + field_name[1:]
                    m = import_string('datapop.models.{}'.format(field_name))
                    print(field_name)
                    if field_name == 'Pointfield':
                        data = Point(data[0], data[1], srid=4326)
                    elif field_name == 'Polygonfield':
                        data = Polygon(data[0])
                    the_field, created = m.objects.get_or_create(is_up=True,register_api_chosen=base_r,o_field=data)
                    check_new_data.append(the_field)
                # Query new data line and hook each data to see if new, same or not relevant
                if not check_new_data:
                    continue
                return True, check_new_data
            else:
                r = RegisterAPIChosen.objects.get(id=path_id)
                if r.is_list:
                    i = False
                    for upper_data_line in l_copy[(r.the_chosen.text_chosen).replace('[0]', '')]:
                        i = self.iterate_data_lines(path_list, n-1, upper_data_line, all_api_pk, line_number)
                        line_number += 1
                        try:
                            where_line += 1
                        except NameError:
                            pass
                    if i:
                        try:
                            r = RegisterAPI.objects.get(pk=all_api_pk)
                            r.where_line += where_line
                            r.save()
                            return True, None
                        except NameError:
                            return True, None
                    else:
                        return False, None
                else:
                    l_copy_line_id = l_copy
                    l_copy = l_copy[(r.the_chosen.text_chosen).replace('[0]', '')]

    def check_or_create_data(self, all_api_pk, check_new_data):
        all_api = RegisterAPI.objects.get(pk=all_api_pk)
        current_model = check_new_data[0]
        print(current_model.id)
        print('after current model')
        field_name = current_model._meta.model.__name__
        query = Q(**{field_name.lower(): current_model})
        query_to_create = Q(**{field_name.lower(): current_model})
        data_line = DataLine.objects.filter(register_api=all_api)
        data_line = data_line.filter(query)
        for t in range(1, len(check_new_data)):
            current_model = check_new_data[t]
            field_name = current_model._meta.model.__name__
            print(field_name)
            query = Q(**{field_name.lower(): current_model})
            data_line = data_line.filter(query)
            query_to_create = query_to_create & Q(**{field_name.lower(): current_model})
        if not data_line:
            print('not data line')
            print(query_to_create.children)
            d = DataLine.objects.create(register_api=all_api)
            for i in query_to_create.children:
                g = getattr(d, "{}_set".format(i[0]))
                g.add(i[1])
        else:
            data_line.update(the_time=timezone.now())
        return True

    def handle(self, *args, **options):
        while True:
            sleep(1)
            all_apis = RegisterAPI.objects.all()

            for all_api in all_apis:
                # Skip if already processed recently
                if all_api.the_time >= timezone.now() - timedelta(hours=24) and not all_api.first:
                    continue
                
                # Get cluster data
                other_chosens = []
                continuing = False
                c = all_api.copy_cluster()
                cluster_id_list = []
                children_id_list = []
                json_list = None

                # Process cluster items
                for i, j in enumerate(c[1]):
                    o = c[1][j]
                    register_api_chosen_id = o.the_chosen.choosing.get(register_api_foreign__isnull=False)

                    # Update field type if needed
                    if not register_api_chosen_id.field_type or register_api_chosen_id.field_type != o.field_type:
                        register_api_chosen_id.field_type = o.field_type
                        register_api_chosen_id.save()

                    if not o.json_list:
                        cluster_id_list.append(register_api_chosen_id.id)
                    else:
                        json_list =  register_api_chosen_id.pk

                # Handle API type specific operations
                if all_api.api_type == "OSM":
                    osm_call.main()
                elif all_api.api_type in ["KML", "JSON"] or not all_api.api_type:
                    self._process_json_kml_api(all_api, c, cluster_id_list, json_list)
                elif all_api.api_type == "CSV":
                    get_csv_data.main(all_api.pk, cluster_id_list)
                    all_api.first = False
                    all_api.save()
                other_chosens = RegisterAPIChosen.objects.filter(id__in=cluster_id_list)
                no_operated = RegisterAPIChosen.objects.filter(id__in=cluster_id_list, operatedfield__isnull=True, json_list=False)
                if other_chosens and not no_operated:
                    data_lines = DataLine.objects.all()
                    linked_pointfield = data_lines.values("pointfield__pk").filter(pointfield__pk__isnull=False)
                    linked_polygonfield = data_lines.values("polygonfield__pk").filter(polygonfield__pk__isnull=False)
                    if all_api.the_time < timezone.now() - timedelta(hours=24) or not (linked_pointfield and linked_polygonfield):
                        for data_line in data_lines:
                            if all_api.api_trash == "TRASHSPECIFICITIES":
                                field_types = [i[0].lower() for i in OperatedField.FIELD_CHOICES]
                                the_type = None
                                trash_type = None
                                trash = None
                                for field_type in field_types:
                                    g = getattr(data_line, "{}_set".format(field_type))
                                    if g.all().count() == 0:
                                        continue
                                    for g_object in g.all():
                                        if not g_object.register_api_chosen:
                                            continue
                                        o_field = g_object.o_field
                                        created = False
                                        operated_fields = g_object.register_api_chosen.operatedfield_set.all()
                                        for operated in operated_fields:
                                            field_type = operated.field_type
                                            if field_type == 'Textfield':
                                                the_type, the_type_created = TheType.objects.get_or_create(the_type=o_field)
                                                trash_type, trash_type_created = TrashType.objects.get_or_create(the_type=the_type)
                                            else:
                                                if created:
                                                    continue
                                                # Three choices for the pointfield: either a list, a string or integers be combined
                                                elif field_type == 'Pointfield' and not operated.operation:
                                                    if type(o_field) is list:
                                                        lat = o_field[0]
                                                        lng = o_field[1]
                                                        point = Point(lng,lat)
                                                    else:
                                                        s = ast.literal_eval(o_field)
                                                        lat = s[0]
                                                        lng = s[1]
                                                        point = Point(lng,lat)
                                                elif field_type == 'Pointfield' and operated.operation == 'COMBINE':
                                                    chosen = operated.register_api_chosen.get(field_name='lat')
                                                    data_chosen = chosen.the_chosen.choosing.filter(register_api_foreign__isnull=False)
                                                    chosen_field_type = chosen.field_type
                                                    m = import_string('datapop.models.{}'.format(chosen_field_type))
                                                    lat = m.objects.get(data_line__in=[data_line],register_api_chosen__in=data_chosen)
                                                    lat = lat.o_field
                                                    chosen = operated.register_api_chosen.get(field_name='lng')
                                                    data_chosen = chosen.the_chosen.choosing.filter(register_api_foreign__isnull=False)
                                                    chosen_field_type = chosen.field_type
                                                    m = import_string('datapop.models.{}'.format(chosen_field_type))
                                                    lng = m.objects.get(data_line__in=[data_line],register_api_chosen__in=data_chosen)
                                                    lng = lng.o_field
                                                    point = Point(lng,lat)
                                                m = import_string('datapop.models.{}'.format(field_type))
                                                try:
                                                    # point_field = m.objects.get(o_field=point, data_line__in=[data_line])
                                                    point_field = m.objects.get(o_field=point)
                                                    data_line_point_field = m.objects.filter(pk=point_field.pk,data_line__in=[data_line])
                                                    if not data_line_point_field:
                                                        point_field.data_line.add(data_line)
                                                except m.DoesNotExist:
                                                    point_field = m.objects.create(o_field=point)
                                                    point_field.data_line.add(data_line)
                                                trash, created = TrashSpecificities.objects.get_or_create(point_field=point_field,from_local_api=True)
                                                # Find closest OSM trash points and hook them to local API trashes
                                                close_osms = m.objects.filter(o_field__distance_lte=(point,D(m=20))).exclude(pk=point_field.pk)
                                                trash.osm_trash_spec.add(*close_osms)
                                        if trash_type and trash:
                                            trash.trash_type.add(trash_type)
                                            trash.save()
                            elif all_api.api_trash == "COLLECTAREA":
                                polygon_field = Polygonfield.objects.get(data_line=data_line)
                                collect_area, created = CollectArea.objects.get_or_create(polygon_field=polygon_field)
                                description = Textfield.objects.get(data_line=data_line)
                                collect_area.description = description
                                collect_area.save()


    def _process_json_kml_api(self, all_api, c, cluster_id_list, json_list):
        """Process JSON/KML API data."""
        other_chosens = []
        children_id_list = []
        
        # Setup register API chosen
        for i, j in enumerate(c[1]):
            o = c[1][j]
            r = o.the_chosen.choosing.get(register_api_foreign__isnull=False)
            r.field_type = o.field_type
            r.field_name = o.field_name
            r.line_id = o.line_id
            r.json_list = o.json_list
            r.save()
            
            if not r.field_type:
                continue
                
            other_chosens = RegisterAPIChosen.objects.filter(
                children_of=r.children_of, 
                id__in=cluster_id_list
            )
            id_list = list(other_chosens.values_list('id', flat=True))
            
            if id_list and id_list not in children_id_list:
                children_id_list.append(id_list)
                
            # Handle child processing
            other_chosens = RegisterAPIChosen.objects.filter(id__in=cluster_id_list)
            for other_chosen in other_chosens:
                if not self._has_valid_field(other_chosen):
                    continue
                    
                other_children = RegisterAPIChosen.objects.filter(children_of=other_chosen)
                if other_children.exists():
                    children_id_list[0].remove(other_chosen.id)
                    if not children_id_list[0]:
                        children_id_list.remove(children_id_list[0])
            
            # Process children
            children = RegisterAPIChosen.objects.filter(children_of=other_chosen.id)
            if children.exists():
                self.iterate_child(other_chosen.id, children_id_list)
        
        # Process data if needed
        if other_chosens:
            empty_type_chosens = other_chosens.filter(field_type__isnull=True)
            if not empty_type_chosens.exists():
                # Handle pagination
                page_number = 0
                self._process_api_data(all_api, page_number, children_id_list, json_list)
    
    def _has_valid_field(self, other_chosen):
        """Check if the chosen object has a valid field."""
        for field in RegisterAPIChosen._meta.get_fields()[3:]:
            field_name = field.name
            if 'field' in field_name and field_name not in ['operatedfield', 'field_type']:
                try:
                    getattr(other_chosen, field_name)
                    return True
                except AttributeError:
                    continue
        return False

    def _process_api_data(self, all_api, page_number, children_id_list, json_list):