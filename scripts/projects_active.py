#!/usr/bin/env python3
import os
import sys
from datetime import date

# 1. Add your project root to the PYTHONPATH
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
#    └ adjust as needed if your script lives elsewhere

# 2. Tell Django which settings to use
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'borbolla_webpage.settings')

# 3. Bootstrap Django
import django
django.setup()

# 4. Import your model
from reportes.models import Project

def get_active_projects():
    today = date.today()
    qs = Project.objects.filter(
        # started on or before today
        start_date__lte=today
    ).order_by('-start_date')
    return qs

if __name__ == '__main__':
    print(f"Active projects as of {date.today()}:")
    for p in get_active_projects():
        print(f" • {p.pk}: {p.name} ({p.client}) — start {p.start_date}")
