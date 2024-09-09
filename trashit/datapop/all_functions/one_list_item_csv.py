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
    for head in header:
        chosen = Chosen.objects.get_or_create(text_chosen=k, value_example=csv_reader[0][head])
        RegisterAPIChosen.objects.get_or_create(register_api_foreign=all_api, chosen=chosen, is_list=True)