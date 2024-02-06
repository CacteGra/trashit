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

from .models import TrashSpecificities

from .views import issue_chooser_viewset

from .widgets import IssueChooserWidget

@hooks.register("register_admin_viewset")
def register_viewsets():
    return [issue_chooser_viewset]

class IssueTemplate(SnippetViewSet):
    model = TrashSpecificities
    index_view_class = TrashSpecificitiesIndex

    panels = [
        FieldPanel("point_field"),
    ]

register_snippet(IssueTemplate)
