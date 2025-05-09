from wagtail.snippets.models import register_snippet
from wagtail import hooks
from wagtail import blocks
from wagtail.snippets.views.snippets import SnippetViewSet, IndexView
from django.core.exceptions import ImproperlyConfigured
from django.forms.models import ModelChoiceIterator
from django.forms.widgets import (CheckboxSelectMultiple, RadioSelect, Select,
                                  SelectMultiple)
from django.utils.translation import gettext_lazy as _
from wagtail.admin.panels import FieldPanel, MultipleChooserPanel, InlinePanel, Panel

from wagtail.admin.filters import WagtailFilterSet
from django.utils.module_loading import import_string
from django import forms

from wagtail.telepath import JSContext

import requests

from wagtailgeowidget.panels import LeafletPanel

from .all_functions import unique_get_data, one_list_item, str_to_coords, one_list_item_csv, one_list_item_json

from .models import RegisterAPI, RegisterAPIChosen, Chosen, OperatedField, Pointfield, Polygonfield, DataLine

from trash.models import CollectArea, TrashType, TheType, TypeLocale, TrashSpecificities

from .views import chosen_chooser_viewset, operated_chooser_viewset, trash_type_chooser_viewset

from .widgets import OperatedChooserWidget, TrashTypeChooserWidget

from django.db.models import Count

@hooks.register("register_admin_viewset")
def register_viewsets():
    return [chosen_chooser_viewset]

@hooks.register('after_create_snippet')
def first_connection(request, instance):
    if isinstance(instance, RegisterAPI):
        r = RegisterAPI.objects.get(pk=instance.pk)
        if r.api_endpoint and r.api_type == "CSV":
            one_list_item_csv.main(r.pk)
        elif r.api_endpoint and r.api_type in ["JSON", "KML"]:
            one_list_item_json.main(r.pk)
        elif r.api_endpoint and r.api_type not in ["CSV", "JSON", "KML"]:
            try:
                if r.is_dumb:
                    print("{}&{}={}&{}={}".format(r.api_endpoint, r.pagination, 1, r.rows_name, r.rows_per_page))
                    response = requests.get("{}&{}={}&{}={}".format(r.api_endpoint, r.pagination, 1, r.rows_name, r.rows_per_page), timeout=10)
                else:
                    params = {r.pagination: 1, r.rows_name: r.rows_per_page}
                    response = requests.get("{}".format(r.api_endpoint), params=params, timeout=10)
            except requests.exceptions.ConnectionError or requests.exceptions.ReadTimeout:
                print(False)
            l = unique_get_data.main(r.api_endpoint)
            one_list_item.main(l, r.pk)
    elif isinstance(instance, CollectArea):
        c = CollectArea.objects.get(pk=instance.pk)
        str_to_coords.main(instance.pk)
    elif isinstance(instance, TrashType):
        t = TrashType.objects.get(pk=instance.pk)
        t.area = True
        t.save()
    return True

# @hooks.register('before_create_snippet')
# def first_connection(request, register_api):
#     r = RegisterAPI.objects.get(pk=register_api.pk)
#     l = unique_get_data.main(r.api_endpoint)
#     one_list_item.main(l, r.pk)
#     return True

@hooks.register('after_edit_snippet')
def first_connection(request, connection_object):
    from OSMPythonTools.nominatim import Nominatim
    if isinstance(instance, RequestLocalWaste):
        r = RequestLocalWaste.objects.get(pk=instance.pk)
        if r.allow_request and not r.register_api:
            latlng = r.coordinates
            lat = latlng.y
            lng = latlng.x
            nominatim = Nominatim()
            h = nominatim.query(lat, lng, reverse=True, zoom=10)
            if h.address():
                d = h.address()
                if d['town']:
                    register_api = RegisterAPI.objects.get_or_create(city=d['town'],state=d['state'],country=d['country'])
                    r.register_api = register_api
                    r.save()
    return True

@hooks.register('before_delete_snippet')
def after_snippet_delete(request, instances):
    for instance in instances:
        if isinstance(instance, RegisterAPI):
            r = RegisterAPI.objects.get(pk=instance.pk)
            all_apis = RegisterAPI.objects.all().exclude(pk=r.pk)
            other_data_lines = DataLine.objects.filter(register_api__in=all_apis)
            if r.api_type == 'OSM':
                trash_specificities = TrashSpecificities.objects.filter(from_local_api=False)
                points = Pointfield.objects.filter(trashspecificities__in=trash_specificities).exclude(data_line__in=other_data_lines)
            else:
                data_lines = DataLine.objects.filter(register_api=r)
                points = Pointfield.objects.filter(data_line__in=data_lines).exclude(data_line__in=other_data_lines)
                polygon_fields = Polygonfield.objects.filter(data_line__in=data_lines).exclude(data_line__in=other_data_lines)
                trash_specificities = TrashSpecificities.objects.filter(point_field__in=points)
                CollectArea.objects.filter(polygon_field__in=polygon_fields).delete()
                points.delete()
                polygon_fields.delete()
            trash_types = TrashType.objects.filter(trashspecificities__in=trash_specificities)
            c = r.copy_cluster()
            cluster_id_list = []
            for i, j in enumerate(c[1]):
                o = c[1][j]
                register_api_chosen_id = o.the_chosen.choosing.get(register_api__isnull=False)
                cluster_id_list.append(register_api_chosen_id.id)
            OperatedField.objects.filter(id__in=cluster_id_list).delete()
            trash_types.delete()
            trash_specificities.delete()
            if r.api_type != 'OSM':
                data_lines.delete()
            register_api_chosen = RegisterAPIChosen.objects.filter(register_api_foreign__pk=r.pk)
            Chosen.objects.filter(choosing__in=register_api_chosen).delete()
            register_api_chosen.delete()
            register_api_chosen = RegisterAPIChosen.objects.filter(register_api__pk=r.pk)
            Chosen.objects.filter(choosing__in=register_api_chosen).delete()
            register_api_chosen.delete()

class RegisterAPITemplate(SnippetViewSet):
    model = RegisterAPI
    panels = [
        FieldPanel('api_title'),
        FieldPanel('api_endpoint'),
        FieldPanel('first'),
        FieldPanel('city'),
        FieldPanel('state'),
        FieldPanel('country'),
        FieldPanel('api_type'),
        FieldPanel('api_trash'),
        FieldPanel('is_dumb'),
        FieldPanel('pagination'),
        FieldPanel('pagination_number'),
        FieldPanel('rows_name'),
        FieldPanel('rows_per_page'),
        FieldPanel('once_every'),
        FieldPanel('json_limit'),
        FieldPanel('results'),
        FieldPanel('until_line'),
        FieldPanel('sleep'),
        # MultipleChooserPanel("the_api",
        #     chooser_field_name="the_chosen",
        #     label="API Key(s)", min_num=0)
        MultipleChooserPanel('the_api', chooser_field_name='the_chosen', label="API Key(s)", min_num=0),
    ]

class RegisterAPIChosenIndex(IndexView):
    def get_base_queryset(self):
        # Allow the queryset to be a callable that takes a request
        # so that it can be evaluated in the context of the request
        if callable(self.queryset):
            self.queryset = self.queryset(self.request)
            cluster_id_list = []
            all_apis = RegisterAPI.objects.all()
            for all_api in all_apis:
                c = all_api.copy_cluster()
                for i, j in enumerate(c[1]):
                    o = c[1][j]
                    register_api_chosen_id = o.the_chosen.choosing.get(register_api__isnull=False)
                    cluster_id_list.append(register_api_chosen_id.id)
            self.queryset = RegisterAPIChosen.objects.filter(id__in=cluster_id_list)
        return super().get_base_queryset()

class NoSameField(FieldPanel):
    """
    Customised FieldPanel to filter choices based on locale of page/model being created/edited
    Usage:
    widget_class - optional, override field widget type
                 - should be CheckboxSelectMultiple, RadioSelect, Select or SelectMultiple
    typed_choice_field - set to True with Select widget forces drop down list
    """

    def __init__(self, field_name, widget_class=None, typed_choice_field=False, *args, **kwargs):
        if not widget_class in [None, CheckboxSelectMultiple, RadioSelect, Select, SelectMultiple]:
            raise ImproperlyConfigured(_(
                "widget_class should be a Django form widget class of type "
                "CheckboxSelectMultiple, RadioSelect, Select or SelectMultiple"
            ))
        self.widget_class = widget_class
        self.typed_choice_field = typed_choice_field
        super().__init__(field_name, *args, **kwargs)

    def clone_kwargs(self):
        return {
            'heading': self.heading,
            'classname': self.classname,
            'help_text': self.help_text,
            'widget_class': self.widget_class,
            'typed_choice_field': self.typed_choice_field,
            'field_name': self.field_name,
        }
    class BoundPanel(FieldPanel.BoundPanel):
        def __init__(self, **kwargs):
            super().__init__(**kwargs)
            if not self.panel.widget_class:
                self.form.fields[self.field_name].widget.choices=self.choice_list
            else:
                self.form.fields[self.field_name].widget = self.panel.widget_class(choices=self.choice_list)
            if self.panel.typed_choice_field:
                self.form.fields[self.field_name].__class__.__name__ = 'typed_choice_field'
            pass
        # Filter line_id foreignkey field objects 
        @property
        def choice_list(self):
            #displayed_object = RegisterAPIChosen.objects.get(pk=self.instance.id)
            self.form.fields[self.field_name].queryset = self.form.fields[self.field_name].queryset.filter(register_api_foreign__pk=self.instance.register_api.pk)
            self.form.fields[self.field_name].queryset = self.form.fields[self.field_name].queryset.exclude(pk=self.instance.id)
            self.form.fields[self.field_name].queryset = self.form.fields[self.field_name].queryset.exclude(register_api__isnull=False)
            choices = ModelChoiceIterator(self.form.fields[self.field_name])
            return choices

class RegisterAPIChosenTemplate(SnippetViewSet):
    model = RegisterAPIChosen
    index_view_class = RegisterAPIChosenIndex

    panels = [
        FieldPanel("field_type"),
        FieldPanel('field_name'),
        NoSameField("line_id", widget_class=Select),
        FieldPanel('json_list'),
    ]


class TypedOnlyPanel(FieldPanel):
    """
    Customised FieldPanel to filter choices based on locale of page/model being created/edited
    Usage:
    widget_class - optional, override field widget type
                 - should be CheckboxSelectMultiple, RadioSelect, Select or SelectMultiple
    typed_choice_field - set to True with Select widget forces drop down list
    """

    def __init__(self, field_name, widget_class=None, typed_choice_field=False, *args, **kwargs):
        if not widget_class in [None, CheckboxSelectMultiple, RadioSelect, Select, SelectMultiple]:
            raise ImproperlyConfigured(_(
                "widget_class should be a Django form widget class of type "
                "CheckboxSelectMultiple, RadioSelect, Select or SelectMultiple"
            ))
        self.widget_class = widget_class
        self.typed_choice_field = typed_choice_field
        super().__init__(field_name, *args, **kwargs)

    def clone_kwargs(self):
        return {
            'heading': self.heading,
            'classname': self.classname,
            'help_text': self.help_text,
            'widget_class': self.widget_class,
            'typed_choice_field': self.typed_choice_field,
            'field_name': self.field_name,
        }
    class BoundPanel(FieldPanel.BoundPanel):
        def __init__(self, **kwargs):
            super().__init__(**kwargs)
            if not self.panel.widget_class:
                self.form.fields[self.field_name].widget.choices=self.choice_list
            else:
                self.form.fields[self.field_name].widget = self.panel.widget_class(choices=self.choice_list)
            if self.panel.typed_choice_field:
                self.form.fields[self.field_name].__class__.__name__ = 'typed_choice_field'
            pass

        @property
        def choice_list(self):
            register_api_chosen = self.form.fields[self.field_name].queryset
            register_api_chosen = list(register_api_chosen.filter(json_list=False, register_api__isnull=False).values_list('pk', flat=True))
            print(register_api_chosen)
            print(self.form.fields[self.field_name].queryset)
            self.form.fields[self.field_name].queryset = self.form.fields[self.field_name].queryset.filter(field_type__isnull=False, register_api_foreign__isnull=False, the_chosen__choosing__pk__in=register_api_chosen)
            choices = ModelChoiceIterator(self.form.fields[self.field_name])
            return choices


class OperatedTemplate(SnippetViewSet):
    model = OperatedField

    panels = [
        # MultipleChooserPanel("the_operated",
        #     chooser_field_name="chosen",
        #     label="API Key(s)", min_num=0),
        # InlinePanel("chosen_select"),
        # FieldPanel("register_api_chosen", widget=CustomCheckboxSelectMultiple),
        # FieldPanel("register_api_chosen", widget=CustomMultipleChoiceField),
        # FieldPanel("register_api_chosen", widget=OperatedChooserWidget),
        # FieldPanel("register_api_chosen", widget=forms.CheckboxSelectMultiple(choices=[RegisterAPIChosen.objects.filter(field_type__isnull=False)])),
        TypedOnlyPanel("register_api_chosen", widget_class=CheckboxSelectMultiple),
        FieldPanel('field_type'),
        FieldPanel('field_name'),
        FieldPanel('operation'),
    ]

class CollectAreaTemplate(SnippetViewSet):
    model = CollectArea

    panels = [
        FieldPanel('raw_data'),
        FieldPanel('quarter'),
        FieldPanel('polygon_field'),
    ]

class TrashTypeIndex(IndexView):
    def get_base_queryset(self):
        # Allow the queryset to be a callable that takes a request
        # so that it can be evaluated in the context of the request
        if callable(self.queryset):
            self.queryset = TrashType.objects.filter(area=True)
        return super().get_base_queryset()

class TypeLocaleTemplate(SnippetViewSet):
    model = TypeLocale
    panels = [
        FieldPanel('locale'),
        FieldPanel('language'),
        FieldPanel('the_type'),
    ]

class OSMType(FieldPanel):
    """
    Customised FieldPanel to filter choices based on locale of page/model being created/edited
    Usage:
    widget_class - optional, override field widget type
                 - should be CheckboxSelectMultiple, RadioSelect, Select or SelectMultiple
    typed_choice_field - set to True with Select widget forces drop down list
    """

    def __init__(self, field_name, widget_class=None, typed_choice_field=False, *args, **kwargs):
        if not widget_class in [None, CheckboxSelectMultiple, RadioSelect, Select, SelectMultiple]:
            raise ImproperlyConfigured(_(
                "widget_class should be a Django form widget class of type "
                "CheckboxSelectMultiple, RadioSelect, Select or SelectMultiple"
            ))
        self.widget_class = widget_class
        self.typed_choice_field = typed_choice_field
        super().__init__(field_name, *args, **kwargs)

    def clone_kwargs(self):
        return {
            'heading': self.heading,
            'classname': self.classname,
            'help_text': self.help_text,
            'widget_class': self.widget_class,
            'typed_choice_field': self.typed_choice_field,
            'field_name': self.field_name,
        }
    class BoundPanel(FieldPanel.BoundPanel):
        def __init__(self, **kwargs):
            super().__init__(**kwargs)
            if not self.panel.widget_class:
                self.form.fields[self.field_name].widget.choices=self.choice_list
            else:
                self.form.fields[self.field_name].widget = self.panel.widget_class(choices=self.choice_list)
            if self.panel.typed_choice_field:
                self.form.fields[self.field_name].__class__.__name__ = 'typed_choice_field'
            pass

        @property
        def choice_list(self):
            self.form.fields[self.field_name].queryset = self.form.fields[self.field_name].queryset.exclude(is_osm=False)
            choices = ModelChoiceIterator(self.form.fields[self.field_name])
            return choices

class TheTypeTemplate(SnippetViewSet):
    model = TheType
    panels = [
        FieldPanel('the_type'),
        #FieldPanel('osm_type', widget=CheckboxSelectMultiple),
        OSMType("osm_type", widget_class=CheckboxSelectMultiple),
        #MultipleChooserPanel(
        #    'related_osm', label="Related OSM types", chooser_field_name="OSM type(s)"
        #),
        FieldPanel('icon'),
        InlinePanel('related_the_type'),
    ]

class TrashTypeTemplate(SnippetViewSet):
    model = TrashType
    index_view_class = TrashTypeIndex
    panels = [
        FieldPanel('collect_area'),
        FieldPanel('the_type', widget=RadioSelect),
        FieldPanel('day', widget=CheckboxSelectMultiple),
        FieldPanel('hour'),
    ]

class PolygonfieldTemplate(SnippetViewSet):
    model = Polygonfield

    panels = [
        LeafletPanel("o_field"),
    ]

class PointfieldTemplate(SnippetViewSet):
    model = Pointfield

    panels = [
        LeafletPanel("o_field"),
    ]

register_snippet(RegisterAPITemplate)

register_snippet(RegisterAPIChosenTemplate)

register_snippet(OperatedTemplate)

register_snippet(CollectAreaTemplate)

register_snippet(TypeLocaleTemplate)

register_snippet(TheTypeTemplate)

register_snippet(TrashTypeTemplate)

register_snippet(PolygonfieldTemplate)

register_snippet(PointfieldTemplate)
