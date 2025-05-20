import urllib.request
import csv

from django.db.models import Q
from django.utils.module_loading import import_string
from django.utils import timezone

from datapop.models import RegisterAPI, RegisterAPIChosen, DataLine

def main(register_api_pk, cluster_id_list):

    all_api = RegisterAPI.objects.get(pk=register_api_pk)
    f = all_api.register_file.open('r')
    csv_reader = csv.DictReader(f)
    header = csv_reader.fieldnames
    registerapichosens = RegisterAPIChosen.objects.filter(id__in=cluster_id_list)
    for row in csv_reader:
        check_new_data = []
        for registerapichosen in registerapichosens:
            field_name = registerapichosen.field_type
            field_name = field_name[0].upper() + field_name[1:]
            m = import_string('datapop.models.{}'.format(field_name))
            data = row[registerapichosen.the_chosen.text_chosen]
            the_field, created = m.objects.get_or_create(is_up=True,register_api_chosen=registerapichosen,o_field=data)
            check_new_data.append(the_field)
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