from django.contrib import admin
from .models.data import (
    Client,
    Contact,
    Project,
    Drawing,
    Weather
)

from .models.dailyreport import (
    DailyReport,
    Manpower,
    Equipment,
    Activity,
    Photo,
)

# Inline registration for Contacts under Client
class ContactInline(admin.TabularInline):
    model = Contact
    extra = 1

@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ('legal_name', 'tax_id', 'email', 'phone')
    search_fields = ('legal_name', 'tax_id')
    inlines = [ContactInline]

@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    list_display = ('name', 'client', 'email', 'phone', 'role')
    list_filter = ('client',)
    search_fields = ('name', 'email', 'phone')

class DrawingInline(admin.TabularInline):
    model = Drawing
    extra = 1
    readonly_fields = ('uploaded_on',)
    fields = ('file', 'description', 'uploaded_on')


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = (
        'name', 'client', 'location_city',
        'start_date', 'contract_number'
    )
    list_filter = ('client', 'location_city')
    search_fields = ('name', 'client__legal_name')

    # ← add DrawingInline here
    inlines = [
        DrawingInline,
    ]

@admin.register(Weather)
class WeatherAdmin(admin.ModelAdmin):
    list_display = (
        'city', 'date', 'temp_c',
        'condition', 'wind_kmh', 'humidity_pct'
    )
    list_filter = ('city', 'date')
    search_fields = ('city',)

# Inline registrations for report details
class ManpowerInline(admin.TabularInline):
    model = Manpower
    extra = 1

class EquipmentInline(admin.TabularInline):
    model = Equipment
    extra = 1

class ActivityInline(admin.TabularInline):
    model = Activity
    extra = 1

class PhotoInline(admin.TabularInline):
    model = Photo
    extra = 1

@admin.register(DailyReport)
class DailyReportAdmin(admin.ModelAdmin):
    list_display = ('date', 'project')
    list_filter = ('project__client', 'project', 'date')
    date_hierarchy = 'date'
    inlines = [
        ManpowerInline,
        EquipmentInline,
        ActivityInline,
        PhotoInline,
    ]



