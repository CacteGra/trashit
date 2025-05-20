import os
from django.core.files import File
import urllib.request
import csv
import uuid

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
    csv_data = response.read().decode("utf-8")
    csv_reader = csv.reader(csv_data.splitlines())
    header = next(csv_reader)
    rows = list(csv_reader)
    with open('{}/data.csv'.format(DATAPOP_DIR), 'w', newline="") as csvfile:
        csv_writer = csv.writer(csvfile)
        # Write the header
        csv_writer.writerow(header)
        # Write the rows
        csv_writer.writerows(rows)
    with open('{}/data.csv'.format(DATAPOP_DIR), 'r') as f:
        filename = str(uuid.uuid4())
        all_api.register_file.save('{}.csv'.format(filename), File(f))
    with open('{}/data.csv'.format(DATAPOP_DIR), 'r') as f:
        csv_reader = csv.DictReader(f)
        print(f)
        header = csv_reader.fieldnames
        for row in csv_reader:
            for head in header:
                chosen, created = Chosen.objects.get_or_create(text_chosen=head, value_example=row[head])
                r, exists = RegisterAPIChosen.objects.get_or_create(register_api_foreign=all_api, the_chosen=chosen, is_list=True)
            break