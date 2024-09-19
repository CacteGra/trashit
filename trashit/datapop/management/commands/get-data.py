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

from trash.models import TrashSpecificities, TrashType, TheType

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
        if parent and (parent.chosen.text_chosen != 'root'):
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
                    base_r_line = RegisterAPIChosen.objects.filter(chosen__text_chosen=base_r.line_id.chosen.text_chosen,chosen__value_example=base_r.line_id.chosen.value_example,children_of__isnull=False)
                    base_r_line = base_r_line[0]
                    data = l_copy[(base_r.chosen.text_chosen).replace('[0]', '')]
                    field_name = base_r.field_type
                    field_name = field_name[0].upper() + field_name[1:]
                    m = import_string('datapop.models.{}'.format(field_name))
                    if field_name == 'Pointfield':
                        data = Point(data[0], data[1], srid=4326)
                    the_field, created = m.objects.get_or_create(is_up=True,register_api_chosen=base_r,o_field=data)
                    check_new_data.append(the_field)
                # Query new data line and hook each data to see if new, same or not relevant
                if not check_new_data:
                    continue
                all_api = RegisterAPI.objects.get(pk=all_api_pk)
                current_model = check_new_data[0]
                field_name = current_model._meta.model.__name__
                query = Q(**{field_name.lower(): current_model})
                query_to_create = Q(**{field_name.lower(): current_model})
                data_line = DataLine.objects.filter(register_api=all_api)
                data_line = data_line.filter(query)
                for t in range(1, len(check_new_data)):
                    current_model = check_new_data[t]
                    field_name = current_model._meta.model.__name__
                    query = Q(**{field_name.lower(): current_model})
                    data_line = data_line.filter(query)
                    query_to_create = query_to_create & Q(**{field_name.lower(): current_model})
                print("data line result")
                print(data_line)
                if not data_line:
                    d = DataLine.objects.create(register_api=all_api)
                    for i in query_to_create.children:
                        g = getattr(d, "{}_set".format(i[0]))
                        g.add(i[1])
                else:
                    data_line.update(the_time=timezone.now())
                # try:
                #     DataLine.objects.get(Q(register_api=all_api) & query)
                # except DataLine.DoesNotExist:
                #     d = DataLine.objects.create(register_api=all_api)
                #     for i in query.children:
                #         g = getattr(d, "{}_set".format(i[0]))
                #         print('set {}'.format(i[0]))
                #         g.add(i[1])
                #         print('object {}'.format(i[1].o_field))
                # print(check_new_data)
                # if not check_new_data:
                #     continue
                # for t in range(1, len(check_new_data)):
                #     current_model = check_new_data[t]
                #     field_name = current_model._meta.model.__name__
                #     query = query & Q(**{field_name.lower(): current_model})
                # try:
                #     d = DataLine.objects.get(query)
                #     for data_object in check_new_data:
                #         data_object.delete()
                #     print('exists already')
                # except DataLine.DoesNotExist:
                #     d = DataLine.objects.create(register_api=all_api)
                #     for i in query.children:
                #         g = getattr(d, "{}_set".format(i[0]))
                #         print('set {}'.format(i[0]))
                #         g.add(i[1])
                #         print('object {}'.format(i[1].o_field))
                #     print(d.textfield_set.count())
                return True
            else:
                r = RegisterAPIChosen.objects.get(id=path_id)
                if r.is_list:
                    i = False
                    for upper_data_line in l_copy[(r.chosen.text_chosen).replace('[0]', '')]:
                        i = self.iterate_data_lines(path_list, n-1, upper_data_line, all_api_pk, line_number)
                        line_number += 1
                        try:
                            where_line += 1
                        except NameError:
                            pass
                    if i:
                        print("Returning True")
                        try:
                            r = RegisterAPI.objects.get(pk=all_api_pk)
                            r.where_line += where_line
                            r.save()
                            return True
                        except NameError:
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
                if all_api.the_time < timezone.now() - timedelta(hours=24) or all_api.first:
                    if all_api.api_type == "CSV":
                        if cluster_id_list:
                            get_csv_data.main(all_api.pk, cluster_id_list)
                            all_api.save()
                    else:
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
                            empty_type_chosens = other_chosens.filter(field_type__isnull=True)
                        else:
                            empty_type_chosens = None
                        if other_chosens and not empty_type_chosens:
                            waiting = False
                            page_number = all_api.pagination_number
                            all_api.where_line = 0
                            all_api.save()
                            for same_level_list in children_id_list:
                                if waiting:
                                    break
                                path_list = self.get_path(same_level_list[0], [same_level_list], True)
                                while True:
                                    print('page {}'.format(page_number))
                                    try:
                                        if all_api.is_dumb:
                                            print("{}&{}={}&{}={}".format(all_api.api_endpoint, all_api.pagination, page_number, all_api.rows_name, all_api.rows_per_page))
                                            response = requests.get("{}&{}={}&{}={}".format(all_api.api_endpoint, all_api.pagination, page_number, all_api.rows_name, all_api.rows_per_page), timeout=10)
                                        else:
                                            params = {all_api.pagination: page_number, all_api.rows_name: all_api.rows_per_page}
                                            response = requests.get("{}".format(all_api.api_endpoint), params=params, timeout=10)
                                    except requests.exceptions.ConnectionError or requests.exceptions.ReadTimeout:
                                        waiting = True
                                        break
                                    if response.status_code == '404':
                                        break
                                    d = json.dumps(response.json(), sort_keys=True, indent=4)
                                    l = json.loads(d)
                                    if all_api.json_limit:
                                        try:
                                            l[all_api.json_limit]
                                            if not l[all_api.json_limit]:
                                                break
                                        except KeyError:
                                            break
                                    else:
                                        r = RegisterAPI.objects.get(pk=all_api.pk)
                                        print(r.where_line)
                                        if all_api.until_line and all_api.until_line <= r.where_line:
                                            break
                                        elif not all_api.until_line:
                                            if int(l[all_api.results]) < r.where_line:
                                                break
                                        # counting = DataLine.objects.filter(register_api=all_api, the_time__gte=timezone.now() - timedelta(hours=24)).count()
                                        # if int(l[all_api.results]) < counting:
                                        #     print(l[all_api.results])
                                        #     break
                                    l_copy = l
                                    iterated = self.iterate_data_lines(path_list, -1, l_copy, all_api.pk, page_number)
                                    page_number += 1
                                    print('next page {}'.format(page_number))
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
                other_chosens = RegisterAPIChosen.objects.filter(id__in=cluster_id_list)
                no_operated = RegisterAPIChosen.objects.filter(id__in=cluster_id_list, operatedfield__isnull=True)
                if other_chosens and not no_operated:
                # if other_chosens:
                    data_lines = DataLine.objects.all()
                    for data_line in data_lines:
                        field_types = [i[0].lower() for i in OperatedField.FIELD_CHOICES]
                        for field_type in field_types:
                            the_type = None
                            trash_type = None
                            trash = None
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
                                            chosens = operated.register_api_chosen.filter(field_name='lat')
                                            m = import_string('datapop.models.{}'.format(field_type))
                                            lat = m.objects.get(data_line=data_line,register_api_chosen__in=chosens)
                                            lat = lat.o_field
                                            chosens = operated.register_api_chosen.filter(field_name='lng')
                                            lng = m.objects.get(data_line=data_line,register_api_chosen__in=chosens)
                                            lng = lng.o_field
                                            point = Point(lng,lat)
                                        m = import_string('datapop.models.{}'.format(field_type))
                                        try:
                                            point_field = m.objects.get(o_field=point, data_line__in=[data_line])
                                        except m.DoesNotExist:
                                            point_field = m.objects.create(o_field=point)
                                            point_field.data_line.add(data_line)
                                        # point_fields = m.objects.filter(o_field=point, data_line__in=data_line)
                                        # if not point_fields:
                                        #     point_field = m.objects.create(o_field=point)
                                        #     point_field.data_line.add(data_line)
                                        trash, created = TrashSpecificities.objects.get_or_create(point_field=point_field)
                            if trash_type and trash:
                                trash.trash_type = trash_type
                                trash.save()

                osm_call.main()