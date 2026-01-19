import os
import urllib.request, urllib.error
import json
from time import sleep
import uuid

from django.core.files import File
import kml2geojson


from . import one_list_item

from datapop.models import RegisterAPI, RegisterAPIChosen, Chosen

def main(register_api_pk):

    all_api = RegisterAPI.objects.get(pk=register_api_pk)
    url = all_api.api_endpoint
    n = 0
    PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
    PROJECT_DIR = os.path.dirname(PROJECT_DIR)
    DATAPOP_DIR = PROJECT_DIR + "/datapop-files"
    while True:
        n += 1
        try:
            response = urllib.request.urlopen(url)
            break
        except urllib.error.URLError:
            if n == 5:
                return False
            sleep(1)
    if all_api.api_type == "KML":
        json_response = kml2geojson.main.convert(response)
    else:
        json_response = json.load(response)
    with open('{}/data.json'.format(DATAPOP_DIR), 'w') as f:
        json.dump(json_response, f)
    with open('{}/data.json'.format(DATAPOP_DIR), 'r') as f:
        filename = str(uuid.uuid4())
        all_api.register_file.save('{}.json'.format(filename), File(f))
    all_api = RegisterAPI.objects.get(pk=register_api_pk)
    l = json.loads(all_api.register_file.read())
    if type(l) is list:
        l = l[0]
    one_list_item.main(l, register_api_pk)