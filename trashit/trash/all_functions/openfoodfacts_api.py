import requests
from datetime import datetime

from trash.models import Wrapper, TheType


def main(code):

    wrapper = Wrapper.objects.get_or_create(code=code)

    if (wrapper.date_create < datetime.utcnow() - timedelta(days=60)) or (not wrapper.packaging):

        # Set the product ID (e.g., 1234567890123) or search query
        product_id = code

        # Construct the API request URL
        url = f"https://world.openfoodfacts.org/api/v0/product/{product_id}"

        # Send the GET request and retrieve the response
        response = requests.get(url)

        # Check if the response was successful (200 OK)
        if response.status_code == 200:
            # Parse the JSON response into a Python dictionary
            product_data = response.json()

            packagings = product_data['product']["packagings"]

            for packaging in packagings:
                material = packaging['material']
                material = material.split(':')[1]
                the_type = TheType.objects.get_or_create(the_type=material)
                wrapper.the_type = the_type
                wrapper.save()

        else:
            print("Error:", response.status_code)
            
    
    return wrapper.pk