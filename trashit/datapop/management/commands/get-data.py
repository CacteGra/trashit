from time import sleep
import requests
import json
import ast

from django.db.models import Q
from django.core.management.base import BaseCommand, CommandError
from datapop.models import RegisterAPI, RegisterAPIChosen, OperatedField, DataLine
from django.contrib.gis.geos import Point
from django.utils.module_loading import import_string
from django.utils import timezone
from datetime import timedelta

from trash.models import TrashSpecificities

from . import osm_call

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
        if parent and (parent.chosen.text_chosen != 'root'):
            self.get_path(parent.id, path_list, False)
        return path_list

    def iterate_data_lines(self, path_list, list_item, l_copy, line_number=0):
        list_item += 1
        n = list_item
        for path_id in path_list[list_item:]:
            n += 1
            if (type(path_id) is list):
                check_new_data = []
                for data_id in path_id:
                    base_r = RegisterAPIChosen.objects.get(id=data_id)
                    base_r_line = RegisterAPIChosen.objects.filter(chosen__text_chosen=base_r.line_id.chosen.text_chosen,chosen__value_example=base_r.line_id.chosen.value_example,children_of__isnull=False)
                    base_r_line = base_r_line[0]
                    data = l_copy[(base_r.chosen.text_chosen).replace('[0]', '')]
                    field_name = base_r.field_type
                    field_name = field_name[0].upper() + field_name[1:]
                    m = import_string('datapop.models.{}'.format(field_name))
                    if field_name == 'Pointfield':
                        data = Point(data[0], data[1], srid=4326)
                    the_field, created = m.objects.get_or_create(is_up=True,register_api_chosen=base_r)
                    if created or the_field.o_field != data:
                        the_field.o_field = data
                    the_field.save()
                    check_new_data.append(the_field)
                # Query new data line and hook each data to see if new, same or not relevant
                current_model = check_new_data[0]
                field_name = current_model._meta.model.__name__
                query = Q(**{field_name.lower(): current_model})
                for t in range(1, len(check_new_data)):
                    current_model = check_new_data[t]
                    field_name = current_model._meta.model.__name__
                    query = query & Q(**{field_name.lower(): current_model})
                print(query)
                try:
                    d = DataLine.objects.get_or_create(query)
                except DataLine.DoesNotExist:
                    last_field = None
                    create_dict = {}
                    create_list = []
                    n = 0
                    for i in query.children:
                        n += 1
                        if i[0] == last_field:
                            create_list.append(i[1])
                        elif not last_field:
                            create_list.append(i[1])
                            last_field = i[0]
                        else:
                            create_dict[last_field] = create_list
                            create_list = []
                            create_list.append(i[1])
                            last_field = i[0]
                        if n == len(query.children):
                            create_dict[last_field] = create_list
                    DataLine.objects.create(**create_dict)
                for new_data in check_new_data:
                    new_data.data_line = d
                    new_data.save()
                return True
            else:
                r = RegisterAPIChosen.objects.get(id=path_id)
                if r.is_list:
                    i = False
                    for upper_data_line in l_copy[(r.chosen.text_chosen).replace('[0]', '')]:
                        i = self.iterate_data_lines(path_list, n-1, upper_data_line, line_number)
                        line_number += 1
                    if i:
                        print("Returning True")
                        return True
                    else:
                        return False
                else:
                    l_copy_line_id = l_copy
                    l_copy = l_copy[(r.chosen.text_chosen).replace('[0]', '')]

    def handle(self, *args, **options):
        while True:
            sleep(1)
            all_apis = RegisterAPI.objects.filter(api_endpoint__isnull=False)
            for all_api in all_apis:
                other_chosens = []
                continuing = False
                c = all_api.copy_cluster()
                cluster_id_list = []
                children_id_list = []
                for i, j in enumerate(c[1]):
                    o = c[1][j]
                    cluster_id_list.append(o.chosen_id)
                if all_api.the_time > timezone.now() - timedelta(hours=24) and not all_api.first:
                    continue
                for i, j in enumerate(c[1]):
                    o = c[1][j]
                    chosen_id = o.chosen_id
                    r = RegisterAPIChosen.objects.get(id=chosen_id)
                    if not r.field_type:
                        continue
                    other_chosens = RegisterAPIChosen.objects.filter(children_of=r.children_of, id__in=cluster_id_list)
                    print(other_chosens)
                    id_list = list(other_chosens.values_list('id', flat=True))
                    print(id_list)
                    if id_list and not id_list in children_id_list:
                        children_id_list.append(list(other_chosens.values_list('id', flat=True)))
                    print(children_id_list)
                    for other_chosen in other_chosens:
                        has_field = False
                        for f in RegisterAPIChosen._meta.get_fields()[3:]:
                            field = f.name
                            if 'field' in field and field != ['operatedfield', 'field_type']:
                                try:
                                    g = getattr(other_chosen, field)
                                    has_field = True
                                except AttributeError:
                                    continue
                            if not has_field:
                                continue
                            print(has_field)
                        other_children = RegisterAPIChosen.objects.filter(children_of=other_chosen)
                        if other_children.count() > 0:
                            children_id_list[0].remove(other_chosen.id)
                            if not children_id_list[0]:
                                children_id_list.remove(children_id_list[0])
                        children = RegisterAPIChosen.objects.filter(children_of=other_chosen.id)
                        if children.count() > 0:
                            print('children count')
                            self.iterate_child(chosen_id, children_id_list)
                            print(children_id_list)
                    other_chosens = RegisterAPIChosen.objects.filter(id__in=cluster_id_list)
                if other_chosens:
                    waiting = False
                    page_number = all_api.pagination_number
                    for same_level_list in children_id_list:
                        if waiting:
                            break
                        path_list = self.get_path(same_level_list[0], [same_level_list], True)
                        while True:
                            print('page {}'.format(page_number))
                            try:
                                if all_api.is_dumb:
                                    response = requests.get("{}&{}={}&{}={}".format(all_api.api_endpoint, all_api.pagination, page_number, all_api.rows_name, all_api.rows_per_page))
                                    print(response.url)
                                else:
                                    if all_api.pagination:
                                        params = {all_api.pagination: page_number, all_api.rows_name: all_api.rows_per_page}
                                        response = requests.get("{}".format(all_api.api_endpoint), params=params)
                                    else:
                                        response = requests.get("{}".format(all_api.api_endpoint))
                            except requests.exceptions.ConnectionError:
                                waiting = True
                                break
                            if response.status_code == '404':
                                break
                            d = json.dumps(response.json(), sort_keys=True, indent=4)
                            l = json.loads(d)
                            if all_api.api_title == 'Washington D.C.' and not l['features']:
                                break
                            l_copy = l
                            iterated = self.iterate_data_lines(path_list, -1, l_copy, page_number)
                            if not iterated:
                                break
                            else:
                                all_api.pagination_number += page_number
                            if all_api.sleep:
                                sleep(all_api.sleep)
                                break
                    if not waiting:
                        all_api.pagination_number = 0
                    else:
                        all_api.pagination_number = page_number
                    if all_api.first:
                        all_api.first = False
                    all_api.save()

            data_lines = DataLine.objects.all()
            for data_line in data_lines:
                g = getattr(data_line, "{}_set".format(("Pointfield").lower()))
                if field_type == 'Textfield':
                    s = ast.literal_eval(g.all()[0].o_field)
                    lat = s['coordinates'][0]
                    long = s['coordinates'][1]
                else:
                    lat = g.all()[0].o_field
                    long = g.all()[1].o_field
                the_data.o_field = Point(lat,long)
                the_data.save()
                trash = TrashSpecificities.objects.get_or_create(pointfield__o_field=the_data)
                field_choices = OperatedField.FIELD_CHOICES
                for field_choice in field_choices:
                    field = field_choice[0]
                    if field == "Pointfield":
                        continue
                    else:
                        g = getattr(data_line, "{}_set".format(field.lower()))
                        operated = g.all()[0].operated_field
                        field_name = operated.field_name
                        the_data, created = m.objects.get_or_create(data_line=data_line,is_up=True,operated_field=operated)
                        if field_name == "thetype":
                            the_type = g.all()[0].o_field
                            trash.trash_type = TrashType.objects.get_or_create(the_type=the_type)
                            trash.save()
            
            # all_operated = OperatedField.objects.all()
            # for operated in all_operated:
            #     api_chosen_set = operated.register_api_chosen.all()
            #     api_chosen_set = RegisterAPIChosen.objects.filter(chosen__text_chosen=api_chosen_set[0].chosen.text_chosen,chosen__value_example=api_chosen_set[0].chosen.value_example,children_of__isnull=False)
            #     data_lines = api_chosen_set[0].dataline_set.all()
            #     for data_line in data_lines:
            #         if data_line.the_time > timezone.now() - timedelta(hours=24):
            #             if operated.field_type == 'Pointfield':
            #                 field_type = operated.field_type
            #                 field_type = field_type[0].upper() + field_type[1:]
            #                 m = import_string('datapop.models.{}'.format(field_type))
            #                 the_data, created = m.objects.get_or_create(data_line=data_line,is_up=True,operated_field=operated)
            #                 field_type = operated.register_api_chosen.all()[0].field_type
            #                 g = getattr(data_line, "{}_set".format(field_type.lower()))
            #                 if field_type == 'Textfield':
            #                     s = ast.literal_eval(g.all()[0].o_field)
            #                     lat = s['coordinates'][0]
            #                     long = s['coordinates'][1]
            #                 else:
            #                     lat = g.all()[0].o_field
            #                     long = g.all()[1].o_field
            #                 the_data.o_field = Point(lat,long)
            #                 the_data.save()
            #                 trash = TrashSpecificities.objects.get_or_create(pointfield__o_field=the_data)
            #             else:
            #                 field_type = operated.field_type
            #                 field_type = field_type[0].upper() + field_type[1:]
            #                 m = import_string('datapop.models.{}'.format(field_type))
            #                 the_data, created = m.objects.get_or_create(data_line=data_line,is_up=True,operated_field=operated)
            #                 field_type = operated.register_api_chosen.all()[0].field_type
            #                 g = getattr(data_line, "{}_set".format(field_type.lower()))
            #                 field_name = operated.field_name
            #                 if field_name == 'the_type':
            #                     the_type = the_type=g.all()[0].o_field
            #                     trash.trash_type = TrashType.objects.get_or_create(the_type=the_type)
            #         trash.save()
                                
            osm_call.main()