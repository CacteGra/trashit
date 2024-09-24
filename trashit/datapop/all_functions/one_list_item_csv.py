import urllib.request
import csv

from datapop.models import RegisterAPI, RegisterAPIChosen, Chosen

def main(register_api_pk):

    all_api = RegisterAPI.objects.get(pk=register_api_pk)
    url = all_api.api_endpoint
    response = urllib.request.urlopen(url)
    content = response.read().decode("utf-8")
    csv_reader = csv.reader(content.splitlines())
    header = next(csv_reader)
    chosen_list = []
    csv_reader = csv.DictReader(content.splitlines())
    first_line = next(csv_reader)
    for head in header:
        print(head)
        chosen, created = Chosen.objects.get_or_create(text_chosen=head, value_example=first_line[head])
        r, exists = RegisterAPIChosen.objects.get_or_create(register_api_foreign=all_api, the_chosen=chosen, is_list=True)
        print(exists)