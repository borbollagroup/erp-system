from django.db import models
from datetime import date
from django.conf import settings
from .data import Project


class DailyReport(models.Model):
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="daily_reports",
        null=True,
        blank=True,
    )

    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    date = models.DateField()
    temp_c = models.DecimalField(max_digits=5, decimal_places=1, null=True, blank=True)
    condition = models.CharField(max_length=100, null=True, blank=True)
    wind_kmh = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    humidity_pct = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)

    def __str__(self):
        return f"Report: {self.project.name} @ {self.date}"

class Manpower(models.Model):
    daily_report = models.ForeignKey(DailyReport, related_name='manpower', on_delete=models.CASCADE)
    role = models.CharField(max_length=100)
    quantity = models.IntegerField()
    hours = models.DecimalField(max_digits=5, decimal_places=2)
    comments = models.CharField(max_length=200, blank=True)

    def __str__(self):
        return f"{self.role} x{self.quantity}"

class Equipment(models.Model):
    daily_report = models.ForeignKey(DailyReport, related_name='equipment', on_delete=models.CASCADE)
    equipment = models.CharField(max_length=100)
    quantity = models.IntegerField()
    hours_used = models.DecimalField(max_digits=5, decimal_places=2)
    comments = models.CharField(max_length=200, blank=True)

    def __str__(self):
        return f"{self.equipment} x{self.quantity}"

class Activity(models.Model):
    daily_report = models.ForeignKey(DailyReport, related_name='activities', on_delete=models.CASCADE)
    activity = models.CharField(max_length=100)
    quantity = models.DecimalField(max_digits=10, decimal_places=2)
    unit = models.CharField(max_length=50)
    description = models.CharField(max_length=200, blank=True)

    def __str__(self):
        return self.activity

class Photo(models.Model):
    daily_report = models.ForeignKey(DailyReport, related_name='photos', on_delete=models.CASCADE)
    photo = models.ImageField(upload_to='daily_photos/')

    def __str__(self):
        return f"Photo for {self.daily_report}"
