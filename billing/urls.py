from django.urls import path
from .views import (
    QuotationListView, QuotationDetailView,
    QuotationCreateView, QuotationUpdateView, QuotationDeleteView, project_list_json,client_contacts_json,
    quotation_send,quotation_public
)



app_name = 'billing'

urlpatterns = [
    path('api/projects/', project_list_json, name='project_list_json'),
    path('api/contacts/', client_contacts_json, name='client_contacts_json'),
    path('quotations/',           QuotationListView.as_view(),   name='quotation_list'),
    path('quotations/add/',       QuotationCreateView.as_view(), name='quotation_add'),
    path('quotations/<int:pk>/',  QuotationDetailView.as_view(), name='quotation_detail'),
    path('quotations/<int:pk>/edit/',   QuotationUpdateView.as_view(), name='quotation_edit'),
    path('quotations/<int:pk>/delete/', QuotationDeleteView.as_view(), name='quotation_delete'),
    path('quotations/<int:pk>/send/', quotation_send, name='quotation_send'),
    path('quotations/public/<str:token>/',  quotation_public, name='quotation_public'),
]
