from django.apps import AppConfig


class BillingConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = "billing"      # must match your app folder
    label = "billing"     # must be unique across all your apps
