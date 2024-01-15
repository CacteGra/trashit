from django.template.loader import render_to_string

# Create your views here.
from django.http import JsonResponse
from django.core.serializers import serialize
from django.views.generic import TemplateView, ListView
from django.contrib.auth.models import User
from django.contrib.auth.mixins import LoginRequiredMixin

class MainPageView(LoginRequiredMixin, TemplateView):
    template_name = 'mapping/home.html'

class FirstLoad(LoginRequiredMixin, ListView):
    from datapop.models import Pointfield
    model = Pointfield
    login_url = '/accounts/login/'
    redirect_field_name = 'redirect_to'
    def get(self, request, *arg, **kwargs):
        from django.contrib.gis.geos import Point
        from django.contrib.gis.measure import D
        from django.contrib.gis.db.models.functions import Distance
        from django.core.exceptions import ObjectDoesNotExist
        from django.db.models import Q

        from datetime import datetime, timedelta
        import random
        from pytz import utc

        from datapop.models import OperatedField, Pointfield

        #from .views_scripts import get_missions

        #usr_pk = self.request.user.pk
        #user = User.objects.get(pk=usr_pk)
        lat = float(request.GET['lat'])
        lng = float(request.GET['lng'])
        print(lat)
        print(lng)
        point = Point(lng, lat, srid=4326)
        operated = OperatedField.objects.filter(field_type='Pointfield')
        p = Pointfield.objects.all()
        print(p[0].o_field)
        if not operated:
            closest_trashes = Pointfield.objects.filter(o_field__distance_lte=(point,D(m=100)))
        else:
            closest_trashes = Pointfield.objects.filter(o_field__distance_lte=(point,D(m=100)))
        closest_trashes.count()
        if closest_trashes:
            print(closest_trashes[0].o_field)
        # check pending/ongoing mission radius
        data_list = []
        for closest_trash in closest_trashes:
            html = render_to_string('trash/trash-presentation.html', {'trash': closest_trash}, request=request)
            data_list.append({'html': html, 'lat': closest_trash.o_field.y, 'lng': closest_trash.o_field.x, 'radius': 30, 'trash_id': closest_trash.id})
        return JsonResponse(data_list, safe=False)
