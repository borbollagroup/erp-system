from django.urls import path
from .views import (
    listar_organizaciones, 
    editar_organizacion, 
    eliminar_organizacion, 
    crear_organizacion, 
    listar_facturas,
    descargar_factura,
    cancelar_factura,
    listar_clientes,
    eliminar_cliente,  # <-- Ensure this is imported
    crear_factura, 
    obtener_test_api_key,
    renovar_live_api_key,
    renovar_test_api_key,
    api_keys,
    get_invoices_current_month,
    generate_quotation,
    receive_invoices
)

urlpatterns = [


    path('api/receive_invoices/', receive_invoices, name='receive_invoices'),
    path('api/invoices/current_month/', get_invoices_current_month, name='invoices-current-month'),
    path('api/quotation/create/', generate_quotation, name='generate_quotation'),

    # API Key management
    path('organizations/<str:organization_id>/api_keys/', api_keys, name='api_keys'),
    path('organizations/<str:organization_id>/obtener_test_api_key/', obtener_test_api_key, name='obtener_test_api_key'),
    path('organizations/<str:organization_id>/renovar_test_api_key/', renovar_test_api_key, name='renovar_test_api_key'),
    path('organizations/<str:organization_id>/renovar_live_api_key/', renovar_live_api_key, name='renovar_live_api_key'),

    # Organization management
    path('organizaciones/', listar_organizaciones, name='listar_organizaciones'),
    path('organizaciones/crear/', crear_organizacion, name='crear_organizacion'),
    path('organizaciones/editar/<str:organizacion_id>/', editar_organizacion, name='editar_organizacion'),
    path('organizaciones/eliminar/<str:organizacion_id>/', eliminar_organizacion, name='eliminar_organizacion'),

    # Client management
    path('clientes/<str:api_key>/', listar_clientes, name='listar_clientes'),
    path('clientes/<str:api_key>/eliminar/<str:cliente_id>/', eliminar_cliente, name='eliminar_cliente'),  # <-- Add this line

    # Invoice management
    path('facturas/<str:organization_id>/', listar_facturas, name='listar_facturas'),
    path('facturador/<int:organization_id>/crear_factura/', crear_factura, name='crear_factura'),
    path('factura/<str:invoice_id>/descargar/', descargar_factura, name='descargar_factura'),
    path('factura/<str:invoice_id>/cancelar/', cancelar_factura, name='cancelar_factura'),


]
