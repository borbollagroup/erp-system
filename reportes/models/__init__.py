# reportes/models/__init__.py

from .data import Client, Contact, Project, Weather
from .dailyreport import DailyReport, Manpower, Equipment, Activity, Photo

__all__ = [
    "Client", "Contact", "Project", "Weather",
    "DailyReport", "Manpower", "Equipment", "Activity", "Photo",
]
