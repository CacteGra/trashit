import urllib.request
import csv

from datapop.models import RegisterAPI, RegisterAPIChosen, DataLine

def main(register_api_pk, cluster_id_list):

    all_api = RegisterAPI.objects.get(pk=register_api_pk)
    url = all_api.api_endpoint
    response = urllib.request.urlopen(url)
    content = response.read().decode("utf-8")
    csv_reader = csv.reader(content.splitlines())
    header = next(csv_reader)
    csv_reader = csv.DictReader(content.splitlines())
    chosens = RegisterAPIChosen.objects.filter(id__in=cluster_id_list)
    for row in csv_reader:
        check_new_data = []
        for chosen in chosens:
            field_name = chosen.chosen.text_chosen
            field_name = field_name[0].upper() + field_name[1:]
            m = import_string('datapop.models.{}'.format(field_name))
            the_field, created = m.objects.get_or_create(is_up=True,register_api_chosen=base_r,o_field=data)
            check_new_data[chosen.chosen.text_chosen] = row[chosen.chosen.text_chosen]
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