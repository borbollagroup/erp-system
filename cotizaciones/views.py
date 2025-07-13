from django.shortcuts import render, get_object_or_404
#from cotizaciones.models import Quotation, IndirectCost, Material, Labor, Equipment, Contact
from decimal import Decimal
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.db import transaction
#from decimal import Decimal
from django.utils.dateparse import parse_date
from .models import Quotation, IndirectCost, Material, Labor, Equipment, Customer
from .forms import QuotationForm , LaborForm , MaterialForm , IndirectCostForm , EquipmentForm
import json

from django.shortcuts import render, redirect
from django.forms import modelformset_factory
from django.db import transaction
from django.contrib.auth.decorators import login_required

def create_quotation_form(request):
    # Assuming you are fetching customers for dropdown selection
    customers = Customer.objects.all()

    # Define the sections dynamically in the view
    sections = ["materials", "labors", "equipments", "indirect_costs"]

    return render(
        request,
        "cotizaciones/create_quotation_form.html",
        {
            "customers": customers,
            "sections": sections,  # Pass the list to the template
        },
    )



@csrf_exempt
@transaction.atomic
def create_quotation(request):
    if request.method == "GET":
        try:
            # Quotation Data
            customer_id = request.GET.get('customer_id')
            project_name = request.GET.get('project_name', 'Default Project')
            quotation_date = parse_date(request.GET.get('quotation_date', ''))
            start_date = parse_date(request.GET.get('start_date', ''))
            end_date = parse_date(request.GET.get('end_date', ''))
            project_cost = Decimal(request.GET.get('project_cost', '0.00'))
            currency = request.GET.get('currency', 'MXN')
            exchange_rate = Decimal(request.GET.get('exchange_rate', '0.00'))
            payment_terms = request.GET.get('payment_terms', '30%')
            validity_date = parse_date(request.GET.get('validity_date', ''))

            # Related Data (parse JSON strings into lists)
            indirect_costs = json.loads(request.GET.get('indirect_costs', '[]'))
            materials = json.loads(request.GET.get('materials', '[]'))
            labors = json.loads(request.GET.get('labors', '[]'))
            equipments = json.loads(request.GET.get('equipments', '[]'))

            # Validate Customer
            customer = Customer.objects.get(id=customer_id)

            # Create Quotation
            quotation = Quotation.objects.create(
                customer=customer,
                project_name=project_name,
                quotation_date=quotation_date,
                start_date=start_date,
                end_date=end_date,
                project_cost=project_cost,
                currency=currency,
                exchange_rate=exchange_rate,
                payment_terms=payment_terms,
                validity_date=validity_date,
            )

            # Create Indirect Costs
            for cost in indirect_costs:
                IndirectCost.objects.create(
                    quotation=quotation,
                    description=cost['description'],
                    amount=Decimal(cost['amount']),
                )

            # Create Materials
            for material in materials:
                Material.objects.create(
                    quotation=quotation,
                    material=material['material'],
                    spec=material.get('spec', ''),
                    unit=material.get('unit', 'pcs'),
                    qty=int(material['qty']),
                    unit_cost=Decimal(material['unit_cost']),
                    remarks=material.get('remarks', ''),
                )

            # Create Labors
            for labor in labors:
                Labor.objects.create(
                    quotation=quotation,
                    item=labor['item'],
                    worker_qty=int(labor['worker_qty']),
                    work_days=int(labor['work_days']),
                    unit_price=Decimal(labor['unit_price']),
                    remarks=labor.get('remarks', ''),
                )

            # Create Equipments
            for equipment in equipments:
                Equipment.objects.create(
                    quotation=quotation,
                    description=equipment['description'],
                    qty=int(equipment['qty']),
                    days=int(equipment['days']),
                    unit_price=Decimal(equipment['unit_price']),
                    remarks=equipment.get('remarks', ''),
                )

            # Return Success Response with the consultation URL
            return JsonResponse({
                "success": True,
                "quotation_id": quotation.id,
                "folio": quotation.folio,
                "consultation_url": f"https://www.borbollagroup.com/cotizaciones/{quotation.folio}"
            }, status=201)

        except Exception as e:
            # Handle Errors
            return JsonResponse({"success": False, "error": str(e)}, status=400)

    else:
        return JsonResponse({"success": False, "error": "Invalid request method."}, status=405)

@login_required
def quotation_view(request, folio):
    # Query the database for the quotation with the given ID
    
    quotation = get_object_or_404(Quotation, id=folio)

    # Calculate the total quantities for materials, labor, and equipment
    material_sum = sum(material.qty * material.unit_cost for material in quotation.materials.all())
    labor_sum = sum(labor.worker_qty * labor.work_days * labor.unit_price for labor in quotation.labors.all())
    equipment_sum = sum(equipment.qty * (equipment.days + equipment.qty ) * equipment.unit_price for equipment in quotation.equipments.all())
    project_sum = material_sum + labor_sum + equipment_sum
    management_expense = project_sum * Decimal('0.06')
    safety_expense = project_sum * Decimal('0.03')
    profit = project_sum * Decimal('0.08')


    # Calculate the indirect sum
    indirect_sum = management_expense + safety_expense + profit + sum(indirect.amount for indirect in quotation.indirect_costs.all())

    # Format numbers with no decimal places and comma separators
    def format_number(value):
        return "{:,.0f}".format(value)

    # Create the dictionary to be passed to the template
    quotation_data = {
        "folio": quotation.folio,
        "customer_information": {
            "name": quotation.customer.name,
            "address": quotation.customer.address,
            "manager": quotation.customer.manager,
            "contact": quotation.customer.contact_email
        },
        "quotation_details": {
            "quotation_date": quotation.quotation_date,
            "project_name": quotation.project_name,
            "start_date": quotation.start_date,
            "end_date": quotation.end_date
        },
        "financial_information": {
            "currency": quotation.currency,
            "exchange_rate": format_number(quotation.exchange_rate),
            "payment_terms": quotation.payment_terms,
            "validity_date": quotation.validity_date
        },
        "summary": [
            {
                "description": quotation.project_name,
                "unit": "LOT",
                "materials": format_number(material_sum),
                "labor": format_number(labor_sum),
                "equipment": format_number(equipment_sum),
                "extras": format_number(indirect_sum),
                "total": format_number(material_sum + labor_sum + equipment_sum + indirect_sum)
            }
        ],
        "labor": [
            {"item": labor.item, "worker_qty": labor.worker_qty, "work_days": labor.work_days, "unit_price": format_number(labor.unit_price), "total_price": format_number(labor.worker_qty * labor.work_days * labor.unit_price), "remarks": labor.remarks}
            for labor in quotation.labors.all()
        ],
        "materials": [
            {"material": material.material, "spec": material.spec, "unit": material.unit, "qty": material.qty, "unit_cost": format_number(material.unit_cost), "total": format_number(material.qty * material.unit_cost), "remarks": material.remarks}
            for material in quotation.materials.all()
        ],
        "equipment": [
            {"description": equipment.description, "qty": equipment.qty, "days": equipment.days + equipment.qty, "unit_price": format_number(equipment.unit_price), "total_price": format_number(( equipment.days + equipment.qty ) *  equipment.qty * equipment.unit_price), "remarks": f"{equipment.qty} * {equipment.description} * {equipment.days} days + {equipment.qty} days freight"}
            for equipment in quotation.equipments.all()
        ],
        "indirect_costs": [
            {"description": "Management Expense / Gastos Administrativos", "amount": format_number(management_expense)},
            {"description": "Safety Expense / Gastos Seguridad", "amount": format_number(safety_expense)},
            {"description": "Extras / Adicionales", "amount": format_number(profit)},
            *[
                {"description": cost.description, "amount": format_number(cost.amount)}
                for cost in quotation.indirect_costs.all()
            ]
        ],
        "project_cost": format_number(material_sum + labor_sum + equipment_sum + indirect_sum),
        "labor_sum": format_number(labor_sum),
        "material_sum": format_number(material_sum),
        "equipment_sum": format_number(equipment_sum),
        "indirect_sum": format_number(indirect_sum)
    }

    return render(request, 'cotizaciones/quotation.html', quotation_data)
