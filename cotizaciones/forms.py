from django import forms
from .models import Quotation, IndirectCost, Material, Labor, Equipment, Customer

class QuotationForm(forms.ModelForm):
    class Meta:
        model = Quotation
        fields = [
            'customer', 'project_name', 'quotation_date', 'start_date',
            'end_date', 'project_cost', 'currency', 'exchange_rate',
            'payment_terms', 'validity_date'
        ]

class IndirectCostForm(forms.ModelForm):
    class Meta:
        model = IndirectCost
        fields = ['description', 'amount']

class MaterialForm(forms.ModelForm):
    class Meta:
        model = Material
        fields = ['material', 'spec', 'unit', 'qty', 'unit_cost', 'remarks']

class LaborForm(forms.ModelForm):
    class Meta:
        model = Labor
        fields = ['item', 'worker_qty', 'work_days', 'unit_price', 'remarks']

class EquipmentForm(forms.ModelForm):
    class Meta:
        model = Equipment
        fields = ['description', 'qty', 'days', 'unit_price', 'remarks']
