import json
import logging
from datetime import date, datetime
from decimal import Decimal
import requests
from django.shortcuts import render
from django.http import HttpResponseServerError
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Q
from .models import DailyReport, Manpower, Equipment, Activity, Photo, Project

logger = logging.getLogger(__name__)

# Weather API settings
GS_URL = 'https://script.google.com/macros/s/.../exec'
OWM_API_KEY = '6cddd2923580c11024597c9bb7bf5b55'

@csrf_exempt
def daily_report(request):
    if request.method == 'POST':
        try:
            # 1) parse incoming JSON payload
            payload = request.POST.get('payload')
            if not payload:
                raise ValueError("Missing payload JSON data")
            data = json.loads(payload)

            # 2) determine report date (fallback to today)
            raw_date = data.get('date')
            try:
                report_date = datetime.fromisoformat(raw_date).date() if raw_date else date.today()
            except Exception:
                logger.warning("Invalid date '%s', defaulting to today", raw_date)
                report_date = date.today()

            # 3) look up project & its city
            project = Project.objects.get(pk=int(data['project']))
            city = project.location_city

            # 4) fetch the right weather record
            today_str = date.today().isoformat()
            d_str     = report_date.isoformat()
            weather   = {}
            if d_str < today_str:
                # historical via Google Script
                resp    = requests.get(GS_URL, params={'city': city, 'date': d_str}, timeout=10)
                results = resp.json().get('results', [])
                if results:
                    rec = results[0]
                    weather = {
                        'temp':      rec.get('temp', 0),
                        'condition': rec.get('condition', ''),
                        'wind':      rec.get('wind', 0),
                        'humidity':  rec.get('humidity', 0),
                    }
            elif d_str == today_str:
                # current from OWM
                resp = requests.get(
                    'https://api.openweathermap.org/data/2.5/weather',
                    params={'q': city, 'appid': OWM_API_KEY, 'units': 'metric'},
                    timeout=10
                )
                j = resp.json()
                weather = {
                    'temp':      j['main']['temp'],
                    'condition': j['weather'][0]['description'],
                    'wind':      j['wind']['speed'],
                    'humidity':  j['main']['humidity'],
                }
            else:
                # forecast from OWM
                resp = requests.get(
                    'https://api.openweathermap.org/data/2.5/forecast',
                    params={'q': city, 'appid': OWM_API_KEY, 'units': 'metric'},
                    timeout=10
                )
                j     = resp.json()
                slot  = next((i for i in j['list'] if i['dt_txt'].startswith(d_str + ' 12:00:00')), None) or j['list'][0]
                weather = {
                    'temp':      slot['main']['temp'],
                    'condition': slot['weather'][0]['description'],
                    'wind':      slot['wind']['speed'],
                    'humidity':  slot['main']['humidity'],
                }

            # 5) helper to parse & quantize decimals
            def parse_decimal(val, field_name):
                try:
                    d  = Decimal(str(val))
                    dp = DailyReport._meta.get_field(field_name).decimal_places
                    return d.quantize(Decimal(f'1e-{dp}'))
                except Exception:
                    return Decimal('0')

            # 6) create main DailyReport
            report = DailyReport.objects.create(
                project=project,
                date=report_date,
                temp_c=     parse_decimal(weather.get('temp', 0),      'temp_c'),
                condition=  weather.get('condition', ''),
                wind_kmh=   parse_decimal(weather.get('wind', 0),      'wind_kmh'),
                humidity_pct=parse_decimal(weather.get('humidity', 0), 'humidity_pct'),
            )

            # 7) helper to parse ints
            def parse_int(v):
                try: return int(v)
                except: return 0

            # 8) create formset rows
            for role, qty, hrs, com in data.get('manpower', []):
                Manpower.objects.create(
                    daily_report=report,
                    role=role,
                    quantity=parse_int(qty),
                    hours=parse_int(hrs),
                    comments=com,
                )
            for eq, qty, hrs, com in data.get('equipment', []):
                Equipment.objects.create(
                    daily_report=report,
                    equipment=eq,
                    quantity=parse_int(qty),
                    hours_used=parse_int(hrs),
                    comments=com,
                )
            for act, qty, unit, desc in data.get('activities', []):
                Activity.objects.create(
                    daily_report=report,
                    activity=act,
                    quantity=parse_int(qty),
                    unit=unit,
                    description=desc,
                )
            for f in request.FILES.getlist('photos'):
                Photo.objects.create(daily_report=report, photo=f)

            # 9) render success page
            return render(request, 'reportes/success.html')

        except Exception as e:
            logger.exception("Error processing daily report: %s", e)
            return HttpResponseServerError(str(e))

    # GET → render the form
    try:
        today    = date.today()
        projects = Project.objects.filter(
            Q(start_date__lte=today),
            Q(end_date__gte=today) | Q(end_date__isnull=True)
        ).order_by('-start_date')

        return render(request, 'reportes/dailyreport_form.html', {
            'projects':    projects,
            'default_date': today.isoformat(),
        })

    except Exception as e:
        logger.exception("Error rendering daily report form: %s", e)
        return HttpResponseServerError(str(e))
