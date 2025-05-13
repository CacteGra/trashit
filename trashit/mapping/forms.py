from captcha.fields import CaptchaField
    
import re
from django.contrib.gis import forms
from django.contrib.gis.geos import Point
from django.core.exceptions import ValidationError
from django.utils.encoding import force_str
from django.utils.translation import gettext_lazy as _


class SimplePointField(forms.Field):
    default_error_messages = {
        'invalid': _('Enter latitude,longitude'),
    }
    re_point = re.compile(r'^\s*(-?\d+(?:\.\d+)?),\s*(-?\d+(?:\.\d+)?)\s*$')

    def prepare_value(self, value):
        if isinstance(value, Point):
            return "{},{}".format(*value.coords)
        return value

    def to_python(self, value):
        """
        Validates input. Returns a Point instance or None for empty values.
        """
        value = super(SimplePointField, self).to_python(value)
        if value in self.empty_values:
            return None
        try:
            m = self.re_point.match(force_str(value))
            if not m:
                raise ValueError()
            value = Point(float(m.group(1)), float(m.group(2)))
        except (ValueError, TypeError):
            raise ValidationError(self.error_messages['invalid'],
                                  code='invalid')

        return value

class RequestLocalForm(forms.Form):
    coordinates = forms.PointField()  # this one is required
    captcha = CaptchaField()
