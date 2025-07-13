# facturador/forms.py

from django import forms

class InvoiceForm(forms.Form):
    customer_id = forms.CharField(label="Customer ID", max_length=100, required=True)
    items = forms.CharField(
        label="Items (JSON format)", 
        widget=forms.Textarea(attrs={'rows': 5}),
        required=True,
        help_text="Provide items as a JSON string"
    )
    payment_form = forms.CharField(label="Payment Form", max_length=2, required=True)
    use = forms.CharField(label="Use (CFDI)", max_length=3, required=True, initial="G01")
    payment_method = forms.ChoiceField(
        label="Payment Method",
        choices=[("PUE", "PUE"), ("PPD", "PPD")],
        initial="PUE"
    )
    currency = forms.CharField(label="Currency", max_length=3, required=False, initial="MXN")
    conditions = forms.CharField(label="Conditions", max_length=1000, required=False)
    async_invoice = forms.BooleanField(label="Async", required=False, initial=False)
    folio_number = forms.IntegerField(label="Folio Number", required=False)
    series = forms.CharField(label="Series", max_length=25, required=False)
    pdf_custom_section = forms.CharField(
        label="PDF Custom Section (HTML)", 
        widget=forms.Textarea(attrs={'rows': 5}),
        required=False
    )
    external_id = forms.CharField(label="External ID", max_length=100, required=False)


class OrganizationForm(forms.Form):
    nombre = forms.CharField(label='Nombre de la Organización', max_length=255, widget=forms.TextInput(attrs={'class': 'form-control'}))
    direccion = forms.CharField(label='Dirección', max_length=255, widget=forms.TextInput(attrs={'class': 'form-control'}))
    codigo_postal = forms.CharField(label='Código Postal', max_length=10, widget=forms.TextInput(attrs={'class': 'form-control'}))
    ciudad = forms.CharField(label='Ciudad', max_length=255, widget=forms.TextInput(attrs={'class': 'form-control'}))
    estado = forms.CharField(label='Estado', max_length=255, widget=forms.TextInput(attrs={'class': 'form-control'}))
    pais = forms.CharField(label='País', max_length=255, widget=forms.TextInput(attrs={'class': 'form-control'}))
    telefono = forms.CharField(label='Teléfono', max_length=20, widget=forms.TextInput(attrs={'class': 'form-control'}))
    email = forms.EmailField(label='Correo Electrónico', widget=forms.EmailInput(attrs={'class': 'form-control'}))
    sitio_web = forms.URLField(label='Sitio Web', required=False, widget=forms.URLInput(attrs={'class': 'form-control'}))
    color = forms.CharField(label='Color del Tema', max_length=7, required=False, widget=forms.TextInput(attrs={'type': 'color', 'class': 'form-control'}))
    logo = forms.BooleanField(label='Tiene Logo', required=False, widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}))
    next_folio_number = forms.IntegerField(label='Número de Folio Siguiente', widget=forms.NumberInput(attrs={'class': 'form-control'}))
    next_folio_number_test = forms.IntegerField(label='Número de Folio Siguiente en Pruebas', widget=forms.NumberInput(attrs={'class': 'form-control'}))

    # Fields for CSD upload
    cer_file = forms.FileField(label='Archivo .cer del CSD', required=False, widget=forms.FileInput(attrs={'class': 'form-control'}))
    key_file = forms.FileField(label='Archivo .key del CSD', required=False, widget=forms.FileInput(attrs={'class': 'form-control'}))
    csd_password = forms.CharField(label='Contraseña del Certificado', required=False, widget=forms.PasswordInput(attrs={'class': 'form-control'}))

    # Field for Logo upload
    logo_file = forms.FileField(label='Archivo de Logotipo (JPG, PNG, SVG)', required=False, widget=forms.FileInput(attrs={'class': 'form-control'}))
