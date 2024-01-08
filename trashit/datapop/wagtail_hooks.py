from wagtail.snippets.models import register_snippet
from wagtail import hooks
from wagtail import blocks
from wagtail.snippets.views.snippets import SnippetViewSet, IndexView
from django.core.exceptions import ImproperlyConfigured
from django.forms.models import ModelChoiceIterator
from django.forms.widgets import (CheckboxSelectMultiple, RadioSelect, Select,
                                  SelectMultiple)
from django.utils.translation import gettext_lazy as _
from wagtail.admin.panels import FieldPanel, MultipleChooserPanel, InlinePanel
from wagtail.admin.filters import WagtailFilterSet
from django.utils.module_loading import import_string
from django import forms

from .all_functions import unique_get_data, one_list_item

from .models import RegisterAPI, RegisterAPIChosen, OperatedField

from .views import chosen_chooser_viewset, operated_chooser_viewset

from .widgets import OperatedChooserWidget

@hooks.register("register_admin_viewset")
def register_viewsets():
    return [chosen_chooser_viewset, operated_chooser_viewset]

@hooks.register('after_create_snippet')
def first_connection(request, register_api):
    r = RegisterAPI.objects.get(pk=register_api.pk)
    l = unique_get_data.main(r.api_endpoint)
    one_list_item.main(l, r.pk)
    return True

# @hooks.register('before_create_snippet')
# def first_connection(request, register_api):
#     r = RegisterAPI.objects.get(pk=register_api.pk)
#     l = unique_get_data.main(r.api_endpoint)
#     one_list_item.main(l, r.pk)
#     return True)

@hooks.register('after_edit_snippet')
def first_connection(request, connection_object):
    # try:
    #     r = RegisterAPI.objects.get(pk=connection_object.pk)
    #     all_chosen = RegisterAPIChosen.objects.filter(register_api=r, register_api_chosen_foreign__isnull=True)
        # for chosen in all_chosen:
        #     for f in SelectField._meta.get_fields()[3:]:
        #         field = f.name
        #         if field in ['register_api_chosen_foreign', 'field']:
        #             pass
        #         else:
        #             print(field)
        #             field_title = Field.objects.create(text_field=field)
        #             s = SelectField.objects.create(field=field_title)
        #             s.register_api_chosen_foreign = chosen
        #             s.save()
    #     return True
    # except RegisterAPI.DoesNotExist:
    #     print(False)
    # try:
    #     r = RegisterAPIChosen.objects.get(pk=connection_object.pk)
    #     select_field = r.selected_register_api_chosen
    #     text = select_field.field.text_field
    #     field_name = text[0].upper() + text[1:]
    #     m = import_string('datapop.models.{}'.format(field_name))
    #     the_field = m.objects.create(is_up=True,selectfield=select_field)
    #     g = setattr(select_field, text, the_field)
    #     g.save()
    #     return True
    # except RegisterAPIChosen.DoesNotExist:
    #     print(False)
    return True

class RegisterAPITemplate(SnippetViewSet):
    model = RegisterAPI

    panels = [
        FieldPanel('api_title'),
        FieldPanel('api_endpoint'),
        FieldPanel('city'),
        FieldPanel('is_dumb'),
        FieldPanel('pagination'),
        FieldPanel('once_every'),
        FieldPanel('sleep'),
        MultipleChooserPanel("the_api",
            chooser_field_name="chosen",
            label="API Key(s)", min_num=0)
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
                    cluster_id_list.append(o.chosen_id)
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

        @property
        def choice_list(self):
            self.form.fields[self.field_name].queryset = self.form.fields[self.field_name].queryset.exclude(pk=self.instance.id)
            choices = ModelChoiceIterator(self.form.fields[self.field_name])
            return choices

class RegisterAPIChosenTemplate(SnippetViewSet):
    model = RegisterAPIChosen
    index_view_class = RegisterAPIChosenIndex

    panels = [
        FieldPanel("field_type"),
        NoSameField("line_id", widget_class=Select),
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
            self.form.fields[self.field_name].queryset = self.form.fields[self.field_name].queryset.filter(field_type__isnull=False)
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
        FieldPanel('operation'),
    ]

register_snippet(RegisterAPITemplate)

register_snippet(RegisterAPIChosenTemplate)

register_snippet(OperatedTemplate)
