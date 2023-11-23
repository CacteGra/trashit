from time import sleep
import requests
import json
import ast

from django.core.management.base import BaseCommand, CommandError
from datapop.models import RegisterAPI, RegisterAPIChosen, OperatedField, DataLine
from django.contrib.gis.geos import Point
from django.utils.module_loading import import_string
from django.utils import timezone
from datetime import timedelta

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
                just_one = RegisterAPIChosen.objects.get(id=path_id[0])
                for data_id in path_id:
                    base_r = RegisterAPIChosen.objects.get(id=data_id)
                    base_r_line = RegisterAPIChosen.objects.filter(chosen__text_chosen=base_r.line_id.chosen.text_chosen,chosen__value_example=base_r.line_id.chosen.value_example,children_of__isnull=False)
                    base_r_line = base_r_line[0]
                    try:
                        line_id = l_copy_line_id[base_r_line.chosen.text_chosen]
                    except KeyError:
                        line_id = l_copy_line_id[base_r_line.children_of.chosen.text_chosen][base_r.line_id.chosen.text_chosen]
                    data_line, created = DataLine.objects.get_or_create(line_number=line_number,register_api=r.register_api_foreign)
                    if created:
                        data_line.line_id = line_id
                        data_line.save()
                    data_line.register_api_chosen.add(base_r)
                    data_line.save()
                    data = l_copy[(base_r.chosen.text_chosen).replace('[0]', '')]
                    field_name = base_r.field_type
                    field_name = field_name[0].upper() + field_name[1:]
                    m = import_string('datapop.models.{}'.format(field_name))
                    if field_name == 'Pointfield':
                        data = Point(data[0], data[1], srid=4326)
                    the_field, created = m.objects.get_or_create(is_up=True,data_line=data_line,register_api_chosen=base_r)
                    if created or the_field.o_field != data:
                        the_field.o_field = data
                        data_line.the_time = timezone.now()
                    the_field.save()
                return True
            else:
                r = RegisterAPIChosen.objects.get(id=path_id)
                if r.is_list:
                    for upper_data_line in l_copy[(r.chosen.text_chosen).replace('[0]', '')]:
                        i = self.iterate_data_lines(path_list, n-1, upper_data_line, line_number)
                        line_number += 1
                    if i:
                        print("Returning True")
                        return True
                else:
                    l_copy_line_id = l_copy
                    l_copy = l_copy[(r.chosen.text_chosen).replace('[0]', '')]
                    if isinstance(l_copy, str):
                        l_copy = ast.literal_eval(l_copy)

    def handle(self, *args, **options):
        while True:
            all_apis = RegisterAPI.objects.all()
            for all_api in all_apis:
                c = all_api.copy_cluster()
                cluster_id_list = []
                children_id_list = []
                for i, j in enumerate(c[1]):
                    o = c[1][j]
                    cluster_id_list.append(o.chosen_id)
                for i, j in enumerate(c[1]):
                    o = c[1][j]
                    chosen_id = o.chosen_id
                    r = RegisterAPIChosen.objects.get(id=chosen_id)
                    other_chosens = RegisterAPIChosen.objects.filter(children_of=r.children_of, id__in=cluster_id_list)
                    other_chosens = other_chosens.filter(line_id__isnull=False)
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
                    other_chosens = RegisterAPIChosen.objects.filter(id__in=cluster_id_list,line_id__isnull=False)
                    if other_chosens:
                        for same_level_list in children_id_list:
                            path_list = self.get_path(same_level_list[0], [same_level_list], True)
                            page_number = 0
                            while True:
                                print('page {}'.format(page_number))
                                if all_api.pagination:
                                    params = {all_api.pagination: page_number}
                                    response = requests.get("{}".format(all_api.api_endpoint), params=params)
                                else:
                                    response = requests.get("{}".format(all_api.api_endpoint))
                                d = json.dumps(response.json(), sort_keys=True, indent=4)
                                l = json.loads(d)
                                if all_api.api_title == 'Washington D.C.' and not l['features']:
                                    break
                                l_copy = l
                                self.iterate_data_lines(path_list, -1, l_copy, page_number)
                                if not all_api.pagination:
                                    break
                                page_number += all_api.once_every
                                if all_api.sleep:
                                    sleep(all_api.sleep)
                                else:
                                    sleep(4)
            all_operated = OperatedField.objects.all()
            for operated in all_operated:
                api_chosen_set = operated.register_api_chosen.all()
                api_chosen_set = RegisterAPIChosen.objects.filter(chosen__text_chosen=api_chosen_set[0].chosen.text_chosen,chosen__value_example=api_chosen_set[0].chosen.value_example,children_of__isnull=False)
                data_lines = api_chosen_set[0].dataline_set.all()
                for data_line in data_lines:
                    if data_line.the_time < timezone.now() - timedelta(hours=24):
                        print('updated')
                        if operated.field_type == 'Pointfield':
                            field_name = operated.field_type
                            field_name = field_name[0].upper() + field_name[1:]
                            m = import_string('datapop.models.{}'.format(field_name))
                            the_data, created = m.objects.get_or_create(data_line=data_line,is_up=True,operated_field=operated)
                            field_type = operated.register_api_chosen.all()[0].field_type
                            g = getattr(data_line, "{}_set".format(field_type.lower()))
                            print(g)
                            the_data.o_field = Point(g.all()[0].o_field,g.all()[1].o_field)
                            the_data.save()
            sleep(3600)
