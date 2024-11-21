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
        from trash.models import TheType
        context = super(MainPageView, self).get_context_data(**kwargs)
        context['trash_types'] = TheType.objects.values_list('the_type', flat=True).distinct()
        return context


class FirstLoad(LoginRequiredMixin, ListView):
    from datapop.models import Pointfield
    model = Pointfield
    login_url = '/admin/'
    redirect_field_name = 'redirect_to'

    def distribute_points(self, latlng, num_points):
        import numpy as np
        lat = latlng.y
        lng = latlng.x
        angles = np.linspace(0, 2 * np.pi, num_points, endpoint=False)
        points = [(np.cos(angle), np.sin(angle)) for angle in angles]
        return points

    def spread(self, types_count, latlng):
        num_points = types_count
        evenly_distributed_points = self.distribute_points(latlng, num_points)
        lat = latlng.y
        lng = latlng.x
        lngs = [(((x[0]*100)/2)*0.000144)/100+(lng) for x in evenly_distributed_points]

        lats = [(((x[1]*100)/2)*0.000144)/100+(lat) for x in evenly_distributed_points]

        return lngs, lats

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
        trash_types = TrashType.objects.all()
        closest_trashes = None
        for trash_type in trash_types:
            m = 1000
            type_locale = None
            closest_trash = None
            while True:
                c = trash_type.the_type.copy_cluster()
                for i, j in enumerate(c[1]):
                    type_locale = c[1][j]
                if type_locale:
                    locale_trash_types = TrashType.objects.filter(the_type__the_type=type_locale.locale)
                    closest_trash = Pointfield.objects.filter(o_field__distance_lte=(point,D(m=m)),trashspecificities__trash_type__in=locale_trash_types,trashspecificities__from_local_api=True).annotate(distance=Distance("o_field", point)).order_by("distance").first()
                    print("local {}".format(type_locale))
                if not closest_trash:
                    print(trash_type.the_type.the_type)
                    closest_trash = Pointfield.objects.filter(o_field__distance_lte=(point,D(m=m)),trashspecificities__trash_type__in=[trash_type]).annotate(distance=Distance("o_field", point)).order_by("distance").first()
                    print(closest_trash)
                if closest_trash:
                    trash_types.exclude(pk=trash_type.pk)
                    closest = Pointfield.objects.filter(pk=closest_trash.pk)
                    if not closest_trashes:
                        closest_trashes = closest
                    else:
                        print("unioning")
                        closest_trashes = closest_trashes.union(closest)
                    break
                m += 1000
                if m == 5000:
                    break
        # check pending/ongoing mission radius
        response = []
        if closest_trashes:
            for closest_trash in closest_trashes:
                data_list = []
                all_trash_types = closest_trash.trashspecificities.trash_type
                types_count = all_trash_types.all().count()
                n = -1
                if types_count == 1:
                    lngs, lats = [closest_trash.o_field.x], [closest_trash.o_field.y]
                else:
                    lngs, lats = self.spread(types_count, closest_trash.o_field)
                for all_trash_type in all_trash_types.all():
                    html = None
                    type_locale = None
                    n += 1
                    c = all_trash_type.the_type.copy_cluster()
                    for i, j in enumerate(c[1]):
                        type_locale = c[1][j]
                    if not type_locale:
                        trash_type = all_trash_type.the_type.the_type
                    else:
                        trash_type = type_locale.locale
                    html = render_to_string('trash/trash-presentation.html', {'trash': closest_trash, 'trash_type': trash_type}, request=request)
                    data_list.append({'html': html, 'lat': lats[n], 'lng': lngs[n], 'trash_id': closest_trash.id, 'trash_type': trash_type})
                response.append({'lng': closest_trash.o_field.x, 'lat': closest_trash.o_field.y, 'radius': 30, 'data_list': data_list})
        return JsonResponse(response, safe=False)

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
        from trash.models import TrashSpecificities, TrashType

        #from .views_scripts import get_missions

        #usr_pk = self.request.user.pk
        #user = User.objects.get(pk=usr_pk)
        lat = float(request.GET['lat'])
        lng = float(request.GET['lng'])
        get_type = request.GET['type']
        print(lat)
        print(lng)
        point = Point(lng, lat, srid=4326)
        operated = OperatedField.objects.filter(field_type='Pointfield')
        p = Pointfield.objects.all()
        print(p[0].o_field)
        farther = True
        m = 1000
        trash_types = TrashType.objects.all()
        closest_trashes = None
        if get_type == 'all':
            while farther:
                for trash_type in trash_types:
                    closest_trash = Pointfield.objects.filter(o_field__distance_lte=(point,D(m=m)),trashspecificities__trash_type=trash_type,trashspecificities__from_local_api=True).annotate(distance=Distance("o_field", point)).order_by("distance").first()
                    if not closest_trash:
                        closest_trash = Pointfield.objects.filter(o_field__distance_lte=(point,D(m=m)),trashspecificities__trash_type=trash_type).annotate(distance=Distance("o_field", point)).order_by("distance").first()
                    if closest_trash:
                        trash_types.exclude(pk=trash_type.pk)
                        closest = Pointfield.objects.filter(pk=closest_trash.trashspecificities.point_field.pk)
                        if not closest_trashes:
                            closest_trashes = closest
                        else:
                            closest_trashes = closest_trashes.union(closest)
                m += 1000
                if m == 5000:
                    break
        else:
            trash_type = TrashType.objects.get(the_type__the_type=get_type)
            while farther:
                closest_trash = Pointfield.objects.filter(o_field__distance_lte=(point,D(m=m)),trashspecificities__trash_type=trash_type,trashspecificities__from_local_api=True).annotate(distance=Distance("o_field", point)).order_by("distance").first()
                if not closest_trash:
                    closest_trash = Pointfield.objects.filter(o_field__distance_lte=(point,D(m=m)),trashspecificities__trash_type=trash_type).annotate(distance=Distance("o_field", point)).order_by("distance").first()
                if closest_trash:
                    closest = Pointfield.objects.filter(pk=closest_trash.trashspecificities.point_field.pk)
                    closest_trashes = closest
                    break
                m += 1000
                if m == 5000:
                    break
        closest_trashes.count()
        # check pending/ongoing mission radius
        data_list = []
        for closest_trash in closest_trashes:
            html = render_to_string('trash/trash-presentation.html', {'trash': closest_trash}, request=request)
            if closest_trash.trashspecificities.from_local_api:
                trash_type = closest_trash.trashspecificities.trash_type.the_type.type_locale.get(language=closest_trash.data_line.register_api.language)
            else:
                trash_type = closest_trash.trashspecificities.trash_type.the_type.related_local.type_locale.get(language=closest_trash.data_line.register_api.language)
            data_list.append({'html': html, 'lat': closest_trash.o_field.y, 'lng': closest_trash.o_field.x, 'radius': 30, 'trash_id': closest_trash.id, 'trash_type': trash_type})
        return JsonResponse(data_list, safe=False)
