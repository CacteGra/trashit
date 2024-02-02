import json
import re
import base64
from django.shortcuts import render
from django.views import generic
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.files.base import ContentFile
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from datapop.models import Pointfield
from .models import TrashSpecificities

# Create your views here.

class ReportTrash(LoginRequiredMixin, generic.DetailView):
    model = User
    context_object_name = 'user'
    def post(self, request, *arg, **kwargs):
        print(self.request.POST)
        print(request.POST)
        if request.method == 'POST':
            response_json = request.POST
            response_json = json.dumps(response_json)
            data = json.loads(response_json)
            trash_id = data['id']
            dataUrlPattern = re.compile('data:image/(png|jpeg);base64,(.*)$')
            ImageData = data['imageBase64']
            ImageData = dataUrlPattern.match(ImageData).group(2)
            if (ImageData == None or len(ImageData) == 0):
                pass
            ImageData = base64.b64decode(ImageData)
            trash_image = ContentFile(ImageData, name='trash-image-' + str(id))
            trash = TrashSpecificities.objects.get(id=trash_id)
            trash.photo = trash_image
            trash.save()
            data = {'status': 'Reported'}
        return JsonResponse(data, safe=False)


class ReportDump(LoginRequiredMixin, generic.DetailView):
    from django.contrib.auth.models import User
    model = User
    context_object_name = 'user'
    def post(self, request, *arg, **kwargs):
        lat = int(request.POST['lat'])
        lng = int(request.POST['lng'])
        trash_point = Pointfield.objects.get_or_create(o_field=Point(lat,long))
        TrashSpecificities.objects.get_or_create(pointfield=trash_point)
        return True
