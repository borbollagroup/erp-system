from datetime import date, timedelta
from django import forms
from django.db.models import Q
from django.forms import inlineformset_factory
from .models.dailyreport import DailyReport, Manpower, Equipment, Activity, Photo
from .models.data import Project , Client, Contact, Drawing

class DailyReportForm(forms.ModelForm):
    project = forms.ModelChoiceField(
        queryset=Project.objects.none(),
        widget=forms.Select(attrs={'class': 'form-select'}),
        label='Project'
    )
    date = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        initial=date.today,
        label='Report Date'
    )

    class Meta:
        model = DailyReport
        fields = ['project', 'date', 'temp_c', 'condition', 'wind_kmh', 'humidity_pct']
        widgets = {
            'temp_c': forms.HiddenInput(),
            'condition': forms.HiddenInput(),
            'wind_kmh': forms.HiddenInput(),
            'humidity_pct': forms.HiddenInput(),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        cutoff = date.today() - timedelta(days=90)
        # Include projects with start_date in last 90 days or no start_date
        self.fields['project'].queryset = Project.objects.filter(
            Q(start_date__gte=cutoff) | Q(start_date__isnull=True)
        ).order_by('-start_date')

# Inline formsets
ManpowerFormSet = inlineformset_factory(
    DailyReport, Manpower,
    fields=('role', 'quantity', 'hours', 'comments'),
    extra=1, can_delete=True,
    widgets={
        'role': forms.TextInput(attrs={'class':'form-control'}),
        'quantity': forms.NumberInput(attrs={'class':'form-control'}),
        'hours': forms.NumberInput(attrs={'class':'form-control'}),
        'comments': forms.TextInput(attrs={'class':'form-control'}),
    }
)

EquipmentFormSet = inlineformset_factory(
    DailyReport, Equipment,
    fields=('equipment', 'quantity', 'hours_used', 'comments'),
    extra=1, can_delete=True,
    widgets={
        'equipment': forms.TextInput(attrs={'class':'form-control'}),
        'quantity': forms.NumberInput(attrs={'class':'form-control'}),
        'hours_used': forms.NumberInput(attrs={'class':'form-control'}),
        'comments': forms.TextInput(attrs={'class':'form-control'}),
    }
)

ActivityFormSet = inlineformset_factory(
    DailyReport, Activity,
    fields=('activity', 'quantity', 'unit', 'description'),
    extra=1, can_delete=True,
    widgets={
        'activity': forms.TextInput(attrs={'class':'form-control'}),
        'quantity': forms.NumberInput(attrs={'class':'form-control'}),
        'unit': forms.TextInput(attrs={'class':'form-control'}),
        'description': forms.TextInput(attrs={'class':'form-control'}),
    }
)

PhotoFormSet = inlineformset_factory(
    DailyReport, Photo,
    fields=('photo',),
    extra=1, can_delete=True,
    widgets={
        'photo': forms.ClearableFileInput(attrs={'class':'form-control'}),
    }
)

# For views: collect formsets in a dict for template rendering
FORMSET_CLASSES = {
    'Manpower': ManpowerFormSet,
    'Equipment': EquipmentFormSet,
    'Activities': ActivityFormSet,
    'Photos': PhotoFormSet,
}



class ClientForm(forms.ModelForm):
    class Meta:
        model = Client
        fields = ['legal_name','tax_id','email','phone']
        widgets = {
            'legal_name': forms.TextInput(attrs={'class':'form-control', 'placeholder':'Legal Name'}),
            'tax_id':     forms.TextInput(attrs={'class':'form-control', 'placeholder':'Tax ID'}),
            'email':      forms.EmailInput(attrs={'class':'form-control', 'placeholder':'Email'}),
            'phone':      forms.TextInput(attrs={'class':'form-control', 'placeholder':'Phone'}),
        }

class ContactForm(forms.ModelForm):
    class Meta:
        model = Contact
        fields = ['name','email','phone','role']
        widgets = {
            'name':  forms.TextInput(attrs={'class':'form-control', 'placeholder':'Name'}),
            'email': forms.EmailInput(attrs={'class':'form-control', 'placeholder':'Email'}),
            'phone': forms.TextInput(attrs={'class':'form-control', 'placeholder':'Phone'}),
            'role':  forms.TextInput(attrs={'class':'form-control', 'placeholder':'Role'}),
        }

ContactFormSet = inlineformset_factory(
    Client, Contact,
    form=ContactForm,
    extra=1, can_delete=True
)



class ProjectForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.pk:
            qs = Contact.objects.filter(client=self.instance.client)
        else:
            qs = Contact.objects.none()
        self.fields['notify_contacts'].queryset = qs
        self.fields['notify_contacts'].widget.attrs.update({
            'class':'form-select','multiple':'multiple'
        })
    start_date = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'type': 'date',
            'class': 'form-control',
        }),
        label='Start Date'
    )
    end_date = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'type': 'date',
            'class': 'form-control',
        }),
        label='End Date'
    )

    class Meta:
        model = Project
        fields = ['name', 'client', 'location_city', 'start_date', 'end_date', 'contract_number', 'notify_contacts']
        widgets = {
            'name':          forms.TextInput(attrs={'class':'form-control', 'placeholder':'Project Name', 'required':True}),
            'client':        forms.Select(attrs={'class':'form-select', 'required':True}),
            'location_city': forms.TextInput(attrs={'class':'form-control', 'placeholder':'City'}),
            'contract_number': forms.TextInput(attrs={'class':'form-control', 'placeholder':'Contract #'}),
        }



class DrawingForm(forms.ModelForm):
    file = forms.FileField(
        required=False,
        widget=forms.ClearableFileInput(attrs={'class':'form-control'})
    )
    description = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'class':'form-control', 'placeholder':'Description'})
    )
    class Meta:
        model = Drawing
        fields = ['file','description']

DrawingFormSet = inlineformset_factory(
    Project, Drawing, form=DrawingForm,
    extra=1, can_delete=True
)
