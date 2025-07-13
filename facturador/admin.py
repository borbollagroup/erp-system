# facturador/admin.py

from django.contrib import admin
from .models import Product, Tax, LocalTax, Organization, Invoice, Unit, ExchangeRate, BankRate , APIKey



@admin.register(APIKey)
class APIKeyAdmin(admin.ModelAdmin):
    list_display = ['name', 'key', 'is_active', 'created_at']


@admin.register(ExchangeRate)
class ExchangeRateAdmin(admin.ModelAdmin):
    # Define which fields to display in the list view
    list_display = ('id', 'timestamp', 'date', 'usd_to_mxn_rate')

    # Enable search by the date or rate
    search_fields = ('date',)

    # Set fields to be read-only
    readonly_fields = ('timestamp', 'date', 'usd_to_mxn_rate')

    # Order records by timestamp in descending order
    ordering = ('-timestamp',)

    # Set the number of records to display per page
    list_per_page = 100

    # Enable an action to export selected entries as CSV
    actions = ['export_as_csv']

    # Export data as CSV
    def export_as_csv(self, request, queryset):
        import csv
        from django.http import HttpResponse
        from datetime import datetime

        opts = self.model._meta
        content_disposition = f'attachment; filename={opts.verbose_name_plural}-{datetime.now().strftime("%Y-%m-%d")}.csv'
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = content_disposition
        writer = csv.writer(response)

        # Include all fields in the CSV header
        field_names = [field.name for field in opts.fields]
        writer.writerow(field_names)

        # Write data rows
        for obj in queryset:
            writer.writerow([getattr(obj, field) for field in field_names])

        return response

    export_as_csv.short_description = "Export Selected Exchange Rates as CSV"


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('id', 'description', 'product_key', 'price', 'tax_included', 'taxability', 'unit', 'sku')
    search_fields = ('id', 'description', 'product_key', 'sku')
    list_filter = ('tax_included', 'taxability')
    readonly_fields = ('price', 'created_at')
    ordering = ('-created_at',)
    list_per_page = 100
    actions = ['export_as_csv']
    filter_horizontal = ('taxes', 'local_taxes')
    exclude = ('id',)



    def export_as_csv(self, request, queryset):
        import csv
        from django.http import HttpResponse
        from datetime import datetime

        opts = self.model._meta
        content_disposition = f'attachment; filename={opts.verbose_name_plural}-{datetime.now().strftime("%Y-%m-%d")}.csv'
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = content_disposition
        writer = csv.writer(response)

        field_names = [field.name for field in opts.fields]
        writer.writerow(field_names)

        for obj in queryset:
            writer.writerow([getattr(obj, field) for field in field_names])

        return response

    export_as_csv.short_description = "Export Selected Products as CSV"

# Register Unit model in the admin panel
@admin.register(Unit)
class UnitAdmin(admin.ModelAdmin):
    list_display = ('key', 'name', '_type')
    search_fields = ('key', 'name')
    list_filter = ('_type',)



# Register BankRate in the admin
@admin.register(BankRate)
class BankRateAdmin(admin.ModelAdmin):
    list_display = ('bank_name', 'buy_rate', 'sell_rate', 'exchange_rate')
    search_fields = ('bank_name', 'exchange_rate__date')
    list_filter = ('exchange_rate__date',)
    ordering = ('-exchange_rate__date',)

# Register Tax model in admin
@admin.register(Tax)
class TaxAdmin(admin.ModelAdmin):
    list_display = ('tax_type', 'rate', 'factor', 'withholding')
    search_fields = ('tax_type',)
    list_filter = ('tax_type', 'factor', 'withholding')

# Register LocalTax model in admin
@admin.register(LocalTax)
class LocalTaxAdmin(admin.ModelAdmin):
    list_display = ('tax_type', 'rate', 'withholding')
    search_fields = ('tax_type',)
    list_filter = ('tax_type', 'withholding')

# Register Organization model with extended options
@admin.register(Organization)
class OrganizationAdmin(admin.ModelAdmin):
    list_display = ('organization_id', 'name', 'legal_name', 'rfc', 'is_production_ready')
    search_fields = ('organization_id', 'name', 'legal_name', 'rfc')
    list_filter = ('is_production_ready', 'state')
    readonly_fields = ('organization_id', 'created_at', 'updated_at')

# Register Invoice model with extended options
@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    # Display all fields in the list view
    list_display = (
        'uuid', 'fecha', 'subtotal', 'iva', 'total', 'moneda', 'emisor_nombre','receptor_nombre', 'status', 'concepto_descripcion', 

    )

    # Add all searchable fields
    search_fields = (
        'uuid', 'receptor_nombre', 'receptor_rfc', 'emisor_nombre', 'emisor_rfc', 
        'concepto_descripcion', 'serie', 'folio'
    )

    # Add filter options
    list_filter = ('fecha', 'moneda', 'metodo_pago', 'tipo_de_comprobante', 'status')

    # Set default ordering
    ordering = ('-fecha',)

    # Limit the number of records displayed per page
    list_per_page = 200

    # Use date hierarchy
    date_hierarchy = 'fecha'

    # Make all fields readonly
    readonly_fields = (
        'uuid', 'fecha', 'serie', 'folio', 'subtotal', 'subtotal_mxn', 'iva', 'iva_mxn', 'total', 
        'total_mxn', 'descuento', 'moneda', 'metodo_pago', 'tipo_de_comprobante', 'tipo_cambio', 
        'concepto_descripcion', 'receptor_nombre', 'receptor_rfc', 'traslado_importe', 
        'emisor_nombre', 'emisor_rfc', 'e_s', 'status'
    )

    # Organize fields in fieldsets
    fieldsets = (
        (None, {
            'fields': ('uuid', 'fecha', 'serie', 'folio', 'receptor_nombre', 'receptor_rfc', 'emisor_nombre', 'emisor_rfc')
        }),
        ('Amounts', {
            'classes': ('collapse',),
            'fields': ('subtotal', 'subtotal_mxn', 'iva', 'iva_mxn', 'total', 'total_mxn', 'descuento')
        }),
        ('Transaction Details', {
            'classes': ('collapse',),
            'fields': ('moneda', 'metodo_pago', 'tipo_de_comprobante', 'tipo_cambio', 'traslado_importe', 'concepto_descripcion', 'e_s', 'status')
        }),
    )

    # Disable add and delete permissions
    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    # Add CSV export functionality
    actions = ['export_as_csv']

    def export_as_csv(self, request, queryset):
        import csv
        from django.http import HttpResponse
        from datetime import datetime

        opts = self.model._meta
        content_disposition = f'attachment; filename={opts.verbose_name_plural}-{datetime.now().strftime("%Y-%m-%d")}.csv'
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = content_disposition
        writer = csv.writer(response)

        # Include all fields for export
        field_names = [field.name for field in opts.fields]
        writer.writerow(field_names)

        for obj in queryset:
            writer.writerow([getattr(obj, field) for field in field_names])

        return response

    export_as_csv.short_description = "Export Selected Invoices as CSV"
