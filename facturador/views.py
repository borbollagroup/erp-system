import requests
import json
from django.contrib.auth.decorators import user_passes_test
from .forms import OrganizationForm
from django.http import HttpResponse, Http404 , HttpResponseRedirect , JsonResponse
from django.conf import settings

from django.utils.timezone import make_aware
from django.shortcuts import render, redirect, get_object_or_404
from .models import Organization , Invoice
from django.urls import reverse
from decimal import Decimal, InvalidOperation
import calendar
import logging

from .management.commands.quotation_generator import *

from django.views.decorators.csrf import csrf_exempt
from django.utils.dateparse import parse_datetime

from django.utils.timezone import now
#from .utils import normalize_header, parse_date  # Assume these utility functions are already defined


FACTURAPI_ORGANIZATION_KEY = 'sk_user_mDR6VqA1GK2OW0k8o05qjlgK6yPbB4gMpeZlXaJ9nd'
FACTURAPI_KEY = 'sk_live_19Vbx6WJm5P4j8OEoEP1kAjn8KqeBARXQgY3ZlwLMy'

import openpyxl

from django.contrib import messages
from .models import Product, Tax, LocalTax


from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.utils import timezone
from datetime import datetime , timedelta



from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
import json
import os

from datetime import datetime

from datetime import datetime
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
import json

def parse_date(date_string):
    """Utility function to parse date strings to 'YYYY-MM-DD' format."""
    try:
        return datetime.strptime(date_string.split("T")[0], "%Y-%m-%d").strftime("%Y-%m-%d")
    except (ValueError, TypeError):
        return None

@csrf_exempt
@require_POST
def generate_quotation(request):
    # Check if the request method is POST
    if request.method == "POST":
        try:
            # Parse the JSON data from the request body
            data = json.loads(request.body)
            
            # Extract material data from the parsed JSON
            material_data = data.get("material", [])
            
            # Filter out any rows with "Especificación" or empty descriptions
            filtered_material_data = []
            for row in material_data:
                # If the 'specification' field contains "Especificación" or is empty, skip it
                if row.get("specification") == "Especificacion" or not row.get("specification"):
                    continue  # Skip this row
                # Append valid rows to the filtered list
                filtered_material_data.append(row)

            # Replace the original material data with the filtered version
            data["material"] = filtered_material_data

            # Specify the file path where the data will be saved
            file_path = "/home/borbolla/borbolla_webpage/quotation_records.json"
            
            # Save the filtered JSON data to a file
            print("DATA!",data)
            
            # Call the function to generate the PDF (assuming `main_q()` does this)
            main_q(data)
            
            # Return a success response
            return JsonResponse({"status": "success", "message": f"{data}"}, status=200)
        
        except json.JSONDecodeError:
            # Handle the case where JSON decoding fails
            return JsonResponse({"status": "error", "message": "Invalid JSON format."}, status=400)
        
        except Exception as e:
            # Handle any other exceptions
            return JsonResponse({"status": "error", "message": f"Error : {e} \n\nData : {data}"}, status=500)
    
    # Return a method-not-allowed response if not a POST request
    return JsonResponse({"status": "error", "message": "Only POST requests are allowed."}, status=405)


@require_http_methods(["POST"])
def get_invoices_current_month(request):
    try:
        body = json.loads(request.body)
        month = body.get('month')
        year = body.get('year')

        if not month or not year:
            return JsonResponse({"status": "error", "message": "Month and year must be provided."}, status=400)

        now = timezone.now()
        try:
            start_of_month = datetime(year, month, 1)
        except ValueError:
            return JsonResponse({"status": "error", "message": "Invalid month or year provided."}, status=400)

        end_of_month = (start_of_month + timedelta(days=calendar.monthrange(year, month)[1]))

        invoices = Invoice.objects.filter(fecha__gte=start_of_month, fecha__lt=end_of_month)

        invoice_data = [
            {
                "uuid": invoice.uuid,
                "fecha": invoice.fecha,
                "serie": invoice.serie,
                "folio": invoice.folio,
                "subtotal": invoice.subtotal,
                "subtotal_mxn": invoice.subtotal_mxn,
                "iva": invoice.iva,
                "iva_mxn": invoice.iva_mxn,
                "total": invoice.total,
                "total_mxn": invoice.total_mxn,
                "moneda": invoice.moneda,
                "metodo_pago": invoice.metodo_pago,
                "tipo_de_comprobante": invoice.tipo_de_comprobante,
                "tipo_cambio": invoice.tipo_cambio,
                "concepto_descripcion": invoice.concepto_descripcion,
                "receptor_nombre": invoice.receptor_nombre,
                "receptor_rfc": invoice.receptor_rfc,
                "traslado_importe": invoice.traslado_importe,
                "emisor_nombre": invoice.emisor_nombre,
                "emisor_rfc": invoice.emisor_rfc,
                "e_s": invoice.e_s,
                "status": invoice.status,
                "descuento": invoice.descuento,
                "cancelacion_fecha": invoice.cancelacion_fecha,
            }
            for invoice in invoices
        ]
        return JsonResponse({"status": "success", "invoices": invoice_data}, status=200)

    except Exception as e:
        # Log the error
        print(f"Error: {str(e)}")
        return JsonResponse({"status": "error", "message": "Internal server error"}, status=500)


# Function to handle the file upload and batch upsert
def upload_products(request):
    if request.method == 'POST' and request.FILES['file']:
        excel_file = request.FILES['file']

        # Load the workbook
        wb = openpyxl.load_workbook(excel_file)
        ws = wb.active

        # Prepare a list to track errors
        errors = []

        # Iterate over the rows in the worksheet, starting from the second row (1st row = headers)
        for index, row in enumerate(ws.iter_rows(min_row=2, values_only=True), start=2):
            try:
                # Unpack row data
                (product_id, description, product_key, price, tax_included, taxability, 
                unit_key, sku, tax_rate, tax_base, tax_type, tax_factor, tax_withholding, 
                local_tax_rate, local_tax_base, local_tax_type, local_tax_withholding) = row

                # Try to insert or update product
                product, created = Product.objects.update_or_create(
                    id=product_id,
                    defaults={
                        'description': description,
                        'product_key': product_key,
                        'price': price,
                        'tax_included': tax_included,
                        'taxability': taxability,
                        'unit_key': unit_key,
                        'sku': sku,
                    }
                )

                # Handle Tax data
                if tax_rate and tax_base and tax_type and tax_factor is not None:
                    Tax.objects.update_or_create(
                        product=product,
                        defaults={
                            'rate': tax_rate,
                            'base': tax_base,
                            'tax_type': tax_type,
                            'factor': tax_factor,
                            'withholding': tax_withholding,
                        }
                    )

                # Handle LocalTax data
                if local_tax_rate and local_tax_base and local_tax_type is not None:
                    LocalTax.objects.update_or_create(
                        product=product,
                        defaults={
                            'rate': local_tax_rate,
                            'base': local_tax_base,
                            'tax_type': local_tax_type,
                            'withholding': local_tax_withholding,
                        }
                    )

            except Exception as e:
                # Record errors for the current row
                errors.append(f"Row {index}: {str(e)}")

        # If there are errors, notify the user
        if errors:
            messages.error(request, f"Errors occurred during upload: {', '.join(errors)}")
        else:
            messages.success(request, "All products have been successfully uploaded.")

        return redirect('upload_products')

    return render(request, 'upload.html')


# Decorator to restrict views to superusers only
superuser_required = user_passes_test(lambda u: u.is_superuser)

# Configuración del logger
logger = logging.getLogger(__name__)






from django.utils.dateparse import parse_datetime

logger = logging.getLogger(__name__)

@csrf_exempt
def receive_invoices(request):
    if request.method == 'POST':
        try:
            # Load the JSON data
            data = json.loads(request.body)
            total_invoices = len(data)
            processed_invoices = 0
            failed_invoices = []

            # Process each invoice
            for invoice_data in data:
                uuid = invoice_data.get("UUID")
                try:
                    # Convert Fecha to a datetime object
                    fecha = parse_datetime(invoice_data.get('Fecha'))

                    # Prepare values for upsert
                    invoice_values = {
                        'fecha': fecha,
                        'serie': invoice_data.get('Serie', ''),
                        'folio': invoice_data.get('Folio', ''),
                        'subtotal': Decimal(invoice_data.get('SubTotal', '0')),
                        'subtotal_mxn': Decimal(invoice_data.get('SubTotal_MXN', '0')),
                        'iva': Decimal(invoice_data.get('IVA', '0')),
                        'iva_mxn': Decimal(invoice_data.get('IVA_MXN', '0')),
                        'total': Decimal(invoice_data.get('Total', '0')),
                        'total_mxn': Decimal(invoice_data.get('Total_MXN', '0')),
                        'moneda': invoice_data.get('Moneda', 'MXN'),
                        'metodo_pago': invoice_data.get('MetodoPago', ''),
                        'tipo_de_comprobante': invoice_data.get('TipoDeComprobante', ''),
                        'tipo_cambio': Decimal(invoice_data.get('TipoCambio', '1.0')),
                        'concepto_descripcion': invoice_data.get('Concepto_Descripcion', ''),
                        'receptor_nombre': invoice_data.get('Receptor_Nombre', ''),
                        'receptor_rfc': invoice_data.get('Receptor_Rfc', ''),
                        'traslado_importe': Decimal(invoice_data.get('Traslado_Importe', '0')),
                        'emisor_nombre': invoice_data.get('Emisor_Nombre', ''),
                        'emisor_rfc': invoice_data.get('Emisor_Rfc', ''),
                        'e_s': invoice_data.get('E/S', ''),
                        'status': invoice_data.get('Status', '') == 'Vigente',
                        'descuento': Decimal(invoice_data.get('Descuento', '0')),
                        'cancelacion_fecha': invoice_data.get('Cancelacion_Fecha', '')
                    }

                    # Perform the upsert operation (update or create)
                    Invoice.objects.update_or_create(uuid=uuid, defaults=invoice_values)
                    processed_invoices += 1

                except Exception as e:
                    logger.error(f"Error processing invoice UUID: {uuid}. Error: {str(e)}")
                    failed_invoices.append(uuid)

            # Log the result
            logger.info(f"Processed {processed_invoices} out of {total_invoices} invoices successfully.")
            if failed_invoices:
                logger.warning(f"Failed invoices: {failed_invoices}")

            # Return response
            return JsonResponse({"status": "success", "processed_invoices": processed_invoices, "failed_invoices": failed_invoices}, status=201)

        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON received: {str(e)}")
            return JsonResponse({"status": "error", "message": "Invalid JSON"}, status=400)

        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}")
            return JsonResponse({"status": "error", "message": str(e)}, status=500)

    return JsonResponse({"status": "error", "message": "Invalid request method"}, status=405)

    
def clean_decimal(value, field_name):
    """Utility function to clean and convert a value to Decimal."""
    from decimal import Decimal, InvalidOperation
    try:
        if isinstance(value, str):
            # Replace curly quotes with straight quotes, remove commas and strip whitespace
            value = value.replace('“', '').replace('”', '').strip().replace(',', '')

            # Handle common invalid values
            if value.lower() in ['nan', 'null', '', 'none']:
                logger.warning(f"Field {field_name} contains 'NaN' or invalid value. Replacing with 0.0.")
                return Decimal('0.0')

        # Handle None and NaN specifically
        if value in [None, '', 'NaN', 'null', float('nan'), 'NaN']:
            logger.warning(f"Field {field_name} contains invalid value: {value}. Replacing with 0.0.")
            return Decimal('0.0')

        decimal_value = Decimal(value)
        return decimal_value

    except (ValueError, InvalidOperation) as e:
        # Fallback handling for any conversion issues
        logger.error(f"Error converting field {field_name} value '{value}' to Decimal: {e}. Replacing with 0.0.")
        return Decimal('0.0')  # As a last resort, replace with 0.0




def api_keys(request, organization_id):
    # Fetch the organization using the organization_id instead of id
    organizacion = get_object_or_404(Organization, organization_id=organization_id)
    
    # Context for the template
    context = {
        'organizacion': organizacion,
        # Add any other necessary context
    }
    
    return render(request, 'facturador/organizaciones/api_keys.html', context)

@superuser_required
def get_new_api_key(request, organization):
    # Use the organization_id from the passed Organization instance
    organization_id = organization.organization_id

    # Define the correct API endpoint for getting a new API key
    mode = 'test' if request.GET.get('is_test') == 'true' else 'live'
    api_url = f'https://www.facturapi.io/v2/organizations/{organization_id}/apikeys/{mode}'

    headers = {
        'Authorization': f'Bearer {FACTURAPI_ORGANIZATION_KEY}',  # API key used for authentication
        'Content-Type': 'application/json',
    }
    print('\n\n\nHEADERS\n\n\n', headers)

    response = requests.put(api_url, headers=headers)
    print(response.json())
    
    if response.status_code == 200:
        return response.json()
    else:
        print('Error:', response.json())  # Log the full error message
        return None


@superuser_required
def listar_organizaciones(request):
    organizaciones = Organization.objects.all()

    for organizacion in organizaciones:
        print(organizacion)
        print('is_test \n>>', request.GET.get('is_test'))
        if request.GET.get('is_test') == 'true':
            if not organizacion.test_api_key:
                new_test_key = get_new_api_key(request, organizacion)
                print("new_test_key\n>>", new_test_key)
                if new_test_key:
                    organizacion.test_api_key = new_test_key
                    organizacion.save()
        else:
            if not organizacion.api_key:
                new_live_key = get_new_api_key(request, organizacion)
                if new_live_key:
                    organizacion.api_key = new_live_key
                    organizacion.save()

    return render(request, 'facturador/organizaciones/listar_organizaciones.html', {'organizaciones': organizaciones})


@superuser_required
def crear_organizacion(request):
    if request.method == 'POST':
        form = OrganizationForm(request.POST, request.FILES)
        if form.is_valid():
            data = form.cleaned_data
            payload = {
                "legal": {
                    "name": data['nombre'],
                    "legal_name": data['nombre'],
                    "tax_system": data['nombre'],
                    "website": data['sitio_web'],
                    "phone": data['telefono'],
                    "address": {
                        "street": data['direccion'],
                        "exterior": data['direccion'],
                        "interior": data['direccion'],
                        "neighborhood": data['direccion'],
                        "city": data['ciudad'],
                        "municipality": data['ciudad'],
                        "zip": data['codigo_postal'],
                        "state": data['estado'],
                    }
                },
                "customization": {
                    "has_logo": data['logo'],
                    "color": data['color'],
                    "next_folio_number": data['next_folio_number'],
                    "next_folio_number_test": data['next_folio_number_test'],
                }
            }
            headers = {
                'Authorization': f'Bearer {FACTURAPI_ORGANIZATION_KEY}',
            }
            response = requests.post('https://www.facturapi.io/v2/organizations', headers=headers, json=payload)
            org_id = response.json()['id']

            if data['cer_file'] and data['key_file'] and data['csd_password']:
                files = {
                    'cer': data['cer_file'],
                    'key': data['key_file'],
                    'password': (None, data['csd_password']),
                }
                requests.put(f'https://www.facturapi.io/v2/organizations/{org_id}/certificate', headers=headers, files=files)

            if data['logo_file']:
                logo_files = {
                    'file': data['logo_file'],
                }
                requests.put(f'https://www.facturapi.io/v2/organizations/{org_id}/logo', headers=headers, files=logo_files)

            return redirect('listar_organizaciones')
    else:
        form = OrganizationForm()

    return render(request, 'facturador/organizaciones/crear_organizacion.html', {'form': form})

@superuser_required
def editar_organizacion(request, organizacion_id):
    headers = {
        'Authorization': f'Bearer {FACTURAPI_ORGANIZATION_KEY}',
    }
    response = requests.get(f'https://www.facturapi.io/v2/organizations/{organizacion_id}', headers=headers)
    organizacion = response.json()

    if request.method == 'POST':
        form = OrganizationForm(request.POST, request.FILES)
        if form.is_valid():
            data = form.cleaned_data
            payload = {
                "legal": {
                    "name": data['nombre'],
                    "legal_name": data['nombre'],
                    "tax_system": data['nombre'],
                    "website": data['sitio_web'],
                    "phone": data['telefono'],
                    "address": {
                        "street": data['direccion'],
                        "exterior": data['direccion'],
                        "interior": data['direccion'],
                        "neighborhood": data['direccion'],
                        "city": data['ciudad'],
                        "municipality": data['ciudad'],
                        "zip": data['codigo_postal'],
                        "state": data['estado'],
                    }
                },
                "customization": {
                    "has_logo": data['logo'],
                    "color": data['color'],
                    "next_folio_number": data['next_folio_number'],
                    "next_folio_number_test": data['next_folio_number_test'],
                }
            }
            requests.put(f'https://www.facturapi.io/v2/organizations/{organizacion_id}', headers=headers, json=payload)

            if data['cer_file'] and data['key_file'] and data['csd_password']:
                files = {
                    'cer': data['cer_file'],
                    'key': data['key_file'],
                    'password': (None, data['csd_password']),
                }
                requests.put(f'https://www.facturapi.io/v2/organizations/{organizacion_id}/certificate', headers=headers, files=files)

            if data['logo_file']:
                logo_files = {
                    'file': data['logo_file'],
                }
                requests.put(f'https://www.facturapi.io/v2/organizations/{organizacion_id}/logo', headers=headers, files=logo_files)

            return redirect('listar_organizaciones')
    else:
        form = OrganizationForm(initial={
            'nombre': organizacion['legal']['name'],
            'direccion': organizacion['legal']['address']['street'],
            'codigo_postal': organizacion['legal']['address']['zip'],
            'ciudad': organizacion['legal']['address']['city'],
            'estado': organizacion['legal']['address']['state'],
            'pais': organizacion['legal']['address']['country'],
            'telefono': organizacion['legal']['phone'],
            'email': organizacion['legal'].get('email', ''),
            'sitio_web': organizacion['legal'].get('website', ''),
            'color': organizacion['customization']['color'],
            'logo': organizacion['customization']['has_logo'],
            'next_folio_number': organizacion['customization']['next_folio_number'],
            'next_folio_number_test': organizacion['customization']['next_folio_number_test'],
        })

    return render(request, 'facturador/organizaciones/editar_organizacion.html', {
        'form': form,
        'organizacion': organizacion,
    })

@superuser_required
def eliminar_organizacion(request, organizacion_id):
    headers = {
        'Authorization': f'Bearer {FACTURAPI_KEY}',
    }
    requests.delete(f'https://www.facturapi.io/v2/organizations/{organizacion_id}', headers=headers)
    return redirect('listar_organizaciones')

@superuser_required
def listar_clientes(request, api_key):
    # Fetch the organization
    organization = get_object_or_404(Organization, test_api_key=api_key)

    # Get is_test parameter from GET request (default to False if not provided)
    is_test = request.GET.get('is_test', 'false').lower() == 'true'
    
    # Get the correct API key based on the is_test value
    if is_test:
        api_key = organization.test_api_key
    else:
        api_key = organization.api_key
    # Set up the API request parameters
    params = {
        'page': request.GET.get('page', 1),
        'limit': request.GET.get('limit', 50),
    }

    # Optional search query
    search_query = request.GET.get('q', None)
    if search_query:
        params['q'] = search_query

    # Make the API request
    url = "https://www.facturapi.io/v2/customers"
    headers = {
        'Authorization': f'Bearer '+api_key
    }
    print(headers,params,'jijijiji')
    response = requests.get(url, headers=headers, params=params)
    print('response_clients_' , response.json())
    # Handle response
    if response.status_code == 200:
        data = response.json()
        clientes = data.get('data', [])
        total_pages = data.get('total_pages', 1)
        current_page = data.get('page', 1)
    else:
        # Handle the case where the API request fails
        clientes = []
        total_pages = 1
        current_page = 1

    page_range = range(1, total_pages + 1)

    context = {
        'organization': organization,
        'clientes': clientes,
        'total_pages': total_pages,
        'current_page': current_page,
        'is_test': is_test,
        'page_range': page_range,  # Add this to the context
    }
    print(context)
    return render(request, 'facturador/clientes/listar_clientes.html', context)

@superuser_required
def eliminar_cliente(request, api_key, cliente_id):
    # Determine if it's a test or live environment
    is_test = request.GET.get('is_test', 'false').lower() == 'true'
    api_url = f"https://www.facturapi.io/v2/customers/{cliente_id}"
    headers = {
        'Authorization': f'Bearer {api_key}',
    }

    response = requests.delete(api_url, headers=headers)
    
    if response.status_code == 200:
        return redirect('listar_clientes', api_key=api_key)
    else:
        return redirect('listar_clientes', api_key=api_key)



@superuser_required
def listar_facturas(request, organization_id):
    # Fetch the organization using the organization_id
    organization = get_object_or_404(Organization, organization_id=organization_id)
    
    # Determine if the request is for test or live data
    is_test = request.GET.get('is_test', 'false').lower() == 'true'
    
    # Get the appropriate API key based on the environment
    api_key = organization.get_api_key(is_test=is_test)
    
    # Set up the API request parameters
    params = {
        'page': request.GET.get('page', 1),
        'limit': request.GET.get('limit', 50),
        'q': request.GET.get('q', ''),
        'customer': request.GET.get('customer', ''),
        'type': request.GET.get('type', ''),
        'payment_method': request.GET.get('payment_method', ''),
    }
    
    # Make the API request to get invoices
    url = "https://www.facturapi.io/v2/invoices"
    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json',
    }
    
    response = requests.get(url, headers=headers, params=params)
    
    # Handle the API response
    if response.status_code == 200:
        data = response.json()
        invoices = data.get('data', [])
        total_pages = data.get('total_pages', 1)
        current_page = data.get('page', 1)
    else:
        invoices = []
        total_pages = 1
        current_page = 1
        # Log the error message or handle it as required
        print(f"Error fetching invoices: {response.status_code} - {response.text}")
    
    # Prepare the context for the template
    context = {
        'organization': organization,
        'invoices': invoices,
        'total_pages': total_pages,
        'current_page': current_page,
        'is_test': is_test,
    }
    
    # Render the template
    return render(request, 'facturador/facturas/listar_facturas.html', context)


@superuser_required
def descargar_factura(request, invoice_id):
    api_key = settings.FACTURAPI_KEY
    headers = {
        "Authorization": f"Bearer {api_key}"
    }

    url = f"https://www.facturapi.io/v2/invoices/{invoice_id}/pdf"

    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        pdf_response = HttpResponse(response.content, content_type='application/pdf')
        pdf_response['Content-Disposition'] = f'attachment; filename="invoice_{invoice_id}.pdf"'
        return pdf_response
    else:
        raise Http404("Invoice not found or couldn't be downloaded")

@superuser_required
def cancelar_factura(request, invoice_id):
    api_key = settings.FACTURAPI_KEY
    headers = {
        "Authorization": f"Bearer {api_key}"
    }

    url = f"https://www.facturapi.io/v2/invoices/{invoice_id}"

    response = requests.delete(url, headers=headers)

    if response.status_code == 200:
        return HttpResponse("Invoice canceled successfully")
    else:
        raise Http404("Invoice not found or couldn't be canceled")


@superuser_required
def crear_factura(request, organization_id):
    # Obtener la organización según el ID
    organization = get_object_or_404(Organization, id=organization_id)

    # Verificar si la solicitud es para un ambiente de prueba
    is_test = request.GET.get('is_test', 'false').lower() == 'true'
    api_key = organization.get_api_key(is_test=is_test)  # Obtener la clave API adecuada

    if request.method == 'POST':
        form = OrganizationForm(request.POST)
        if form.is_valid():
            datos_factura = form.cleaned_data
            headers = {
                'Authorization': f'Bearer {api_key}',
                'Content-Type': 'application/json'
            }
            # Reemplazar con el endpoint correcto de FacturAPI y el payload de la factura
            respuesta = requests.post('https://www.facturapi.io/v2/invoices', headers=headers, json=datos_factura)

            if respuesta.status_code == 201:
                return redirect('url_exito')  # Redirigir a una página de éxito
            else:
                # Manejar errores
                return render(request, 'error_template.html', {'error': respuesta.json()})
    
    else:
        form = OrganizationForm()

    return render(request, 'crear_factura_template.html', {'form': form, 'organization': organization, 'is_test': is_test})





def obtener_test_api_key(request, organization_id):
    organization = get_object_or_404(Organization, id=organization_id)
    url = f"https://www.facturapi.io/v2/organizations/{organization_id}/apikeys/test"
    headers = {
        "Authorization": f"Bearer {FACTURAPI_ORGANIZATION_KEY}"
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        test_api_key = response.json()
        organization.test_api_key = test_api_key
        organization.save()  # Update the model instance
        return JsonResponse({'test_api_key': test_api_key})
    else:
        return JsonResponse({'error': response.text}, status=response.status_code)



def renovar_test_api_key(request, organization_id):
    organization = get_object_or_404(Organization, organization_id=organization_id)
    url = f"https://www.facturapi.io/v2/organizations/{organization_id}/apikeys/test"
    headers = {
        "Authorization": f"Bearer {FACTURAPI_ORGANIZATION_KEY}"
    }
    response = requests.put(url, headers=headers)
    if response.status_code == 200:
        new_test_api_key = response.json()
        organization.test_api_key = new_test_api_key
        organization.save()  # Update the model instance
        return JsonResponse({'new_test_api_key': new_test_api_key})
    else:
        return JsonResponse({'error': response.text}, status=response.status_code)

def renovar_live_api_key(request, organization_id):
    organization = get_object_or_404(Organization, organization_id=organization_id)
    url = f"https://www.facturapi.io/v2/organizations/{organization_id}/apikeys/live"
    headers = {
        "Authorization": f"Bearer {FACTURAPI_ORGANIZATION_KEY}"
    }
    response = requests.put(url, headers=headers)
    if response.status_code == 200:
        new_live_api_key = response.json()
        organization.api_key = new_live_api_key
        organization.save()  # Update the model instance
        return JsonResponse({'new_live_api_key': new_live_api_key})
    else:
        return JsonResponse({'error': response.text}, status=response.status_code)
