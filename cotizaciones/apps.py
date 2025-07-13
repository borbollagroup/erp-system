from django.apps import AppConfig


class CotizacionesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'cotizaciones'
    verbose_name = "Cotizaciones / Quotations"  # Optional: Make it more descriptive in admin


