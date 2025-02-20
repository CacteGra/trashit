import urllib.request
import json

from . import one_list_item

from datapop.models import RegisterAPI, RegisterAPIChosen, Chosen

def main(register_api_pk):

    all_api = RegisterAPI.objects.get(pk=register_api_pk)
    url = all_api.api_endpoint
    response = urllib.request.urlopen(url)
    json_response = json.load(response)
    one_list_item.main(json_response, register_api_pk)