from django.db import models
from django.utils import timezone
from wagtail.snippets.models import register_snippet

@register_snippet
class VisitorStats(models.Model):
    page_name = models.CharField(max_length=100, default="trash_map")
    total_visitors = models.PositiveIntegerField(default=0)
    session_key = models.CharField(max_length=100, unique=True, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.page_name}: {self.total_visitors}"

    class Meta:
        verbose_name = "Visitor Statistic"
        verbose_name_plural = "Visitor Statistics"

@register_snippet
class PageStats(models.Model):
    page_name = models.CharField(max_length=100, default="trash_map")
    total_visitors = models.PositiveIntegerField(default=0)
    total_seconds_spent = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def average_time_spent(self):
        if self.total_visitors > 0:
            return round(self.total_seconds_spent / self.total_visitors, 2)
        return 0

    def __str__(self):
        return f"{self.page_name} {self.total_visitors} (Avg: {self.average_time_spent}s)"