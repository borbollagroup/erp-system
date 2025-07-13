# billing/forms.py

from django import forms
from .models import Quotation
from reportes.models.data import Contact

class QuotationForm(forms.ModelForm):
    # manually add the 'number' field so it's on the form
    number = forms.CharField(required=False, widget=forms.HiddenInput())
    
    notify_contacts = forms.ModelMultipleChoiceField(
        queryset=Contact.objects.none(),
        required=False,
        widget=forms.SelectMultiple(attrs={
          'class': 'form-select',
          'size': 6,
        })
    )

    class Meta:
        model = Quotation
        fields = [
          'quote_type','coin','client','supplier','project',
          'date_issued','valid_until','notify_contacts',
          'number',    # ← make sure you add it here
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        client_id = (
            self.data.get('client')
            or getattr(self.instance.client, 'pk', None)
        )
        if client_id:
            self.fields['notify_contacts'].queryset = Contact.objects.filter(
                client_id=client_id
            )
        else:
            self.fields['notify_contacts'].queryset = Contact.objects.none()
