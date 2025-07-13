from django.contrib import admin
from .models import (
    Supplier, SupplierContact,
    Quotation, QuotationItem,
    PurchaseOrder, PurchaseOrderItem,
)

class SupplierContactInline(admin.TabularInline):
    model = SupplierContact
    extra = 1

@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):
    list_display = ('name','tax_id','contact_email','phone')
    inlines = [SupplierContactInline]


class QuotationItemInline(admin.TabularInline):
    model = QuotationItem
    extra = 1
    fields = ('category','description','qty','days','unit_price','remarks','total_price')
    readonly_fields = ('total_price',)

class PurchaseOrderInline(admin.TabularInline):
    model = PurchaseOrder
    extra = 0
    fields = ('po_number','date_issued','total_amount')
    show_change_link = True

@admin.register(Quotation)
class QuotationAdmin(admin.ModelAdmin):
    list_display = ('number','quote_type','project','__str__','date_issued','total_amount')
    list_filter  = ('quote_type','project')
    inlines = [QuotationItemInline, PurchaseOrderInline]


class PurchaseOrderItemInline(admin.TabularInline):
    model = PurchaseOrderItem
    extra = 1
    fields = ('description','qty','days','unit_price','remarks','total_price')
    readonly_fields = ('total_price',)

@admin.register(PurchaseOrder)
class PurchaseOrderAdmin(admin.ModelAdmin):
    list_display = ('po_number','quotation','date_issued','total_amount')
    inlines = [PurchaseOrderItemInline]
