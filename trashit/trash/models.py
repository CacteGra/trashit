from django.db import models
from datapop.models import Pointfield

# Create your models here.


class TrashSpecificities(models.Model):
    id = models.AutoField(primary_key=True, editable=False)
    point_field = models.OneToOneField(Pointfield, on_delete=models.CASCADE)
    trash_type = models.CharField(max_length=250, null=True, blank=True)
    reported = models.BooleanField(default=False)
