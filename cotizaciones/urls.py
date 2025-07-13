from django.urls import path
from .views import quotation_view, create_quotation, create_quotation_form

urlpatterns = [
    path('<int:folio>/', quotation_view, name='quotation_view'),  # View to display quotation details
    path('create/', create_quotation, name='create_quotation'),  # Existing view to create quotation via API
    path('create/form/', create_quotation_form, name='create_quotation_form'),  # New form-based view
]
