from django.db import models
from django.utils import timezone

class PageStats(models.Model):
    """Single row to store global stats for the page"""
    page_name = models.CharField(max_length=100, default="trash_map")
    total_visitors = models.PositiveIntegerField(default=0)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Page Stats"
        verbose_name_plural = "Page Stats"

    def __str__(self):
        return f"{self.page_name}: {self.total_visitors}"

class VisitorSession(models.Model):
    """Tracks individual sessions to ensure uniqueness"""
    session_key = models.CharField(max_length=100, unique=True)
    created_at = models.DateTimeField(default=timezone.now)
    
    class Meta:
        verbose_name = "Visitor Session"
        verbose_name_plural = "Visitor Sessions"