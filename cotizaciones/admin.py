from django.contrib import admin
from .models import Customer, Contact2, Quotation, Material, Labor, Equipment, IndirectCost

class CustomerAdmin(admin.ModelAdmin):
    list_display = ('name', 'manager', 'address', 'contact_email', 'created_at', 'updated_at')
    search_fields = ('name', 'manager', 'address', 'contact_email')

class ContactAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'phone_number', 'position', 'customer', 'created_at', 'updated_at')
    search_fields = ('name', 'email', 'phone_number', 'position', 'customer__name')

class QuotationAdmin(admin.ModelAdmin):
    list_display = ('project_name', 'customer', 'quotation_date', 'start_date', 'end_date', 'project_cost', 'currency', 'exchange_rate', 'payment_terms', 'validity_date', 'created_at', 'updated_at')
    search_fields = ('project_name', 'customer__name', 'quotation_date', 'start_date', 'end_date', 'currency', 'payment_terms', 'validity_date')

class MaterialAdmin(admin.ModelAdmin):
    list_display = ('material', 'spec', 'unit', 'qty', 'unit_cost', 'remarks', 'quotation', 'created_at', 'updated_at')
    search_fields = ('material', 'spec', 'unit', 'quotation__project_name')

class LaborAdmin(admin.ModelAdmin):
    list_display = ('item', 'worker_qty', 'work_days', 'unit_price', 'remarks', 'quotation', 'created_at', 'updated_at')
    search_fields = ('item', 'quotation__project_name')

class EquipmentAdmin(admin.ModelAdmin):
    list_display = ('description', 'qty', 'days', 'unit_price', 'remarks', 'quotation', 'created_at', 'updated_at')
    search_fields = ('description', 'quotation__project_name')

class IndirectCostAdmin(admin.ModelAdmin):
    list_display = ('description', 'amount', 'quotation', 'created_at', 'updated_at')
    search_fields = ('description', 'quotation__project_name')

admin.site.register(Customer, CustomerAdmin)
admin.site.register(Contact2, ContactAdmin)
admin.site.register(Quotation, QuotationAdmin)
admin.site.register(Material, MaterialAdmin)
admin.site.register(Labor, LaborAdmin)
admin.site.register(Equipment, EquipmentAdmin)
admin.site.register(IndirectCost, IndirectCostAdmin)
