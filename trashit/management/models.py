from django.db import models
from django.utils import timezone

class VisitorStats(models.Model):
    page_name = models.CharField(max_length=100, default="trash_map")
    total_visitors = models.PositiveIntegerField(default=0)
    # We use a unique key to ensure we don't double count the same session
    session_key = models.CharField(max_length=100, unique=True, blank=True, null=True) 
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.page_name}: {self.total_visitors}"