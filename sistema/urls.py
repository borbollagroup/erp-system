from django.urls import path
from .views import redirect_to_airtable_js

urlpatterns = [
    path('', redirect_to_airtable_js, name='redirect_to_airtable_js'),
]
