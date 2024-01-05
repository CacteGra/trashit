import json

from django.shortcuts import render
from django.views import generic
from django.contrib.auth.mixins import LoginRequiredMixin

from datapop.models import Pointfield
from .models import TrashSpecificities

# Create your views here.

class ReportTrash(LoginRequiredMixin, generic.DetailView):
    from django.contrib.auth.models import User
    model = User
    context_object_name = 'user'
    def post(self, request, *arg, **kwargs):
        print(self.request.POST)
        print(request.POST)
        if request.method == 'POST':
            trash_point_id = request.POST['cosa']
            print(trash_point_id)
            the_trash_point = Pointfield.objects.get(id=trash_point_id)
            the_trash = TrashSpecificities.objects.get(pointfield=the_trash_point)
            the_trash.reported = True
            the_trash.save()
        return True


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
