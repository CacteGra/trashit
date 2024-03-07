from django.template.loader import render_to_string

# Create your views here.
from django.http import JsonResponse
from django.core.serializers import serialize
from django.views.generic import TemplateView, ListView
from django.contrib.auth.models import User
from django.contrib.auth.mixins import LoginRequiredMixin

class MainPageView(LoginRequiredMixin, TemplateView):
    template_name = 'mapping/home.html'
    def get_context_data(self, **kwargs):
        from datapop.models import Pointfield
        context = super(MainPageView, self).get_context_data(**kwargs)
        context['trash_types'] = Pointfield.objects.values_list('trashspecificities__trash_type__trash_type', flat=True).distinct()
        return context


class FirstLoad(LoginRequiredMixin, ListView):
    from datapop.models import Pointfield
    model = Pointfield
    login_url = '/admin/'
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
        from trash.models import TrashSpecificities, TrashType

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
        farther = True
        m = 500
        trash_types = list(TrashSpecificities.objects.values_list('trash_type', flat=True).distinct())
        closest_trashes = None
        while farther:
            for trash_type in trash_types:
                print(trash_type)
                closest_trash = Pointfield.objects.filter(o_field__distance_lte=(point,D(m=m)),trashspecificities__trash_type=trash_type).annotate(distance=Distance("o_field", point)).order_by("distance").first()
                print(closest_trash)
                if closest_trash:
                    trash_types.remove(trash_type)
                    closest = Pointfield.objects.filter(pk=closest_trash.pk)
                    if not closest_trashes:
                        closest_trashes = closest
                    else:
                        print("unioning")
                        closest_trashes = closest_trashes.union(closest)
                print(closest_trashes)
            m += 500
            if m == 5000:
                break
        print("clostests: " + str(closest_trashes.count()))
        if closest_trashes:
            print(closest_trashes[0].o_field)
        # check pending/ongoing mission radius
        data_list = []
        for closest_trash in closest_trashes:
            html = render_to_string('trash/trash-presentation.html', {'trash': closest_trash}, request=request)
            data_list.append({'html': html, 'lat': closest_trash.o_field.y, 'lng': closest_trash.o_field.x, 'radius': 30, 'trash_id': closest_trash.id, 'trash_type': closest_trash.trashspecificities.trash_type.trash_type})
        return JsonResponse(data_list, safe=False)

class FilterType(LoginRequiredMixin, ListView):
    from datapop.models import Pointfield
    model = Pointfield
    login_url = '/admin/'
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
        from trash.models import TrashSpecificities

        #from .views_scripts import get_missions

        #usr_pk = self.request.user.pk
        #user = User.objects.get(pk=usr_pk)
        lat = float(request.GET['lat'])
        lng = float(request.GET['lng'])
        trash_type = request.GET['type']
        print(lat)
        print(lng)
        point = Point(lng, lat, srid=4326)
        operated = OperatedField.objects.filter(field_type='Pointfield')
        p = Pointfield.objects.all()
        print(p[0].o_field)
        farther = True
        m = 500
        trash_types = list(TashType.objects.values_list('trash_type', flat=True).distinct())
        closest_trashes = None
        if trash_type == 'all':
            while farther:
                for trash_type in trash_types:
                    closest_trash = Pointfield.objects.filter(o_field__distance_lte=(point,D(m=m)),trashspecificities__trash_type=trash_type).annotate(distance=Distance("o_field", point)).order_by("distance").first()
                    if closest_trash:
                        trash_types.remove(trash_type)
                        closest = Pointfield.objects.filter(pk=closest_trash.pk)
                        if not closest_trashes:
                            closest_trashes = closest
                        else:
                            closest_trashes = closest_trashes.union(closest)
                m += 500
                if m == 5000:
                    break
        else:
            while farther:
                closest_trash = Pointfield.objects.filter(o_field__distance_lte=(point,D(m=m)),trashspecificities__trash_type__trash_type=trash_type).annotate(distance=Distance("o_field", point)).order_by("distance").first()
                if closest_trash:
                    closest_trashes = Pointfield.objects.filter(pk=closest_trash.pk)
                    break
                m += 500
                if m == 5000:
                    break
        closest_trashes.count()
        if closest_trashes:
            print(closest_trashes[0].o_field)
        # check pending/ongoing mission radius
        data_list = []
        for closest_trash in closest_trashes:
            html = render_to_string('trash/trash-presentation.html', {'trash': closest_trash}, request=request)
            data_list.append({'html': html, 'lat': closest_trash.o_field.y, 'lng': closest_trash.o_field.x, 'radius': 30, 'trash_id': closest_trash.id, 'trash_type': closest_trash.trashspecificities.trash_type.trash_type})
        return JsonResponse(data_list, safe=False)
