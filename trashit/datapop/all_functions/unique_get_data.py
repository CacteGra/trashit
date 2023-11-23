from time import sleep

import json, requests

def main(url):

    while True:
        try:
            response = requests.get("{}".format(url))
            break
        except requests.exceptions.ConnectionError:
            sleep(5)
    d = json.dumps(response.json(), sort_keys=True, indent=4)
    l = json.loads(d)
    return l
