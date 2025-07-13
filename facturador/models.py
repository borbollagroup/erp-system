from django.db import models
from django.utils import timezone
import datetime

import uuid


class APIKey(models.Model):
    key = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)  # UUID-based API key
    name = models.CharField(max_length=100)  # Name of the API key holder (optional)
    is_active = models.BooleanField(default=True)  # To enable/disable the key
    created_at = models.DateTimeField(auto_now_add=True)  # When the key was created

    def __str__(self):
        return f"{self.name} - {'Active' if self.is_active else 'Inactive'}"



def today():
    return timezone.now().date()
# Model for Unit with the provided options
class Unit(models.Model):
    _type = models.CharField(max_length=100)  # Describes the type of the unit (e.g., 'Múltiplos / Fracciones / Decimales')
    key = models.CharField(max_length=10, unique=True)  # The unique key for each unit (e.g., 'H87', 'EA')
    name = models.CharField(max_length=100)  # The full name of the unit (e.g., 'Pieza', 'Elemento')

    def __str__(self):
        return f"{self.key} - {self.name}"

# Model for organization details
class Organization(models.Model):
    organization_id = models.CharField(max_length=50, primary_key=True)  # Primary key for the Organization
    name = models.CharField(max_length=255)  # Name of the organization
    legal_name = models.CharField(max_length=255, null=True, blank=True)  # Legal name, can be null
    rfc = models.CharField(max_length=20, unique=True)  # Unique RFC field
    address = models.TextField(null=True, blank=True)  # Address field, can be null
    is_production_ready = models.BooleanField(default=False)  # Flag for production readiness
    state = models.CharField(max_length=100, null=True, blank=True)  # State field, can be null
    created_at = models.DateTimeField(auto_now_add=True)  # Auto-filled creation date
    updated_at = models.DateTimeField(auto_now=True)  # Auto-filled update date

    def __str__(self):
        return self.name


# Invoice model for storing invoice data
class Invoice(models.Model):
    uuid = models.CharField(max_length=255, unique=True)  # Unique identifier for the invoice
    fecha = models.DateTimeField()  # Date and time of the invoice
    serie = models.CharField(max_length=50, null=True, blank=True)  # Series code (optional)
    folio = models.CharField(max_length=50, null=True, blank=True)  # Folio number (optional)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)  # Subtotal amount
    subtotal_mxn = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)  # Subtotal in MXN currency
    iva = models.DecimalField(max_digits=10, decimal_places=2)  # VAT amount
    iva_mxn = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)  # VAT amount in MXN
    total = models.DecimalField(max_digits=10, decimal_places=2)  # Total amount
    total_mxn = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)  # Total amount in MXN
    moneda = models.CharField(max_length=10)  # Currency code
    metodo_pago = models.CharField(max_length=100)  # Payment method
    tipo_de_comprobante = models.CharField(max_length=50)  # Type of voucher
    tipo_cambio = models.DecimalField(max_digits=10, decimal_places=2, default=1.0)  # Exchange rate
    concepto_descripcion = models.TextField(null=True, blank=True)  # Concept description (optional)
    receptor_nombre = models.CharField(max_length=255, null=True, blank=True)  # Receiver's name (optional)
    receptor_rfc = models.CharField(max_length=255, null=True, blank=True)  # Receiver's tax code (optional)
    traslado_importe = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)  # Transferred tax amount (optional)
    emisor_nombre = models.CharField(max_length=255)  # Issuer's name
    emisor_rfc = models.CharField(max_length=255)  # Issuer's tax code
    e_s = models.CharField(max_length=50)  # Entry/Exit type
    status = models.BooleanField(default=True)  # Invoice status: active (True) or cancelled (False)
    descuento = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)  # Discount amount
    cancelacion_fecha = models.CharField(max_length=255 , null = True , default = '')  # Issuer's tax code

    def __str__(self):
        return f'{self.uuid} {self.status}'

# Product and other models remain the same as the previous code.




class Product(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    livemode = models.BooleanField(default=False)
    description = models.CharField(max_length=500)
    product_key = models.CharField(max_length=20)

    # Campos para el desglose de cotización
    material = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    labor = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    expenses = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    machinery = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    # El precio se calculará automáticamente
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, editable=False)

    tax_included = models.BooleanField(default=True, null=True)
    taxability = models.CharField(max_length=2, default="01", choices=[
        ('01', 'No objeto de impuesto'),
        ('02', 'Sí objeto de impuesto'),
        ('03', 'Sí objeto de impuesto, pero no obligado a desglose'),
        ('04', 'Sí objeto de impuesto, y no causa impuesto'),
        ('05', 'Sí objeto de impuesto, IVA crédito PODEBI'),
    ])

    taxes = models.ManyToManyField('Tax', blank=True, related_name='products')
    local_taxes = models.ManyToManyField('LocalTax', blank=True, related_name='products')

    unit = models.ForeignKey('Unit', on_delete=models.SET_NULL, null=True, blank=True, related_name='products')

    sku = models.CharField(max_length=100, null=True, blank=True)

    def save(self, *args, **kwargs):
        # Calcular el precio como la suma de material, mano de obra, gastos y maquinaria
        self.price = self.material + self.labor + self.expenses + self.machinery
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.description} ({self.sku})"


class Tax(models.Model):
    rate = models.DecimalField(max_digits=5, decimal_places=4)
    base = models.DecimalField(max_digits=10, decimal_places=2, default=100.00)
    tax_type = models.CharField(max_length=50, default="IVA")
    factor = models.CharField(max_length=10, choices=[
        ('Tasa', 'Tasa'),
        ('Cuota', 'Cuota'),
        ('Exento', 'Exento')
    ], default='Tasa')
    withholding = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.tax_type} - {self.rate * 100}%"
class LocalTax(models.Model):
    rate = models.DecimalField(max_digits=5, decimal_places=4)
    tax_type = models.CharField(max_length=100)
    base = models.DecimalField(max_digits=10, decimal_places=2, default=100.00)
    withholding = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.tax_type} - {self.rate * 100}%"




class ExchangeRate2(models.Model):
    date = models.DateField(default=today)
    average_rate = models.DecimalField(max_digits=10, decimal_places=4)
    buy_rate = models.DecimalField(max_digits=10, decimal_places=4)
    sell_rate = models.DecimalField(max_digits=10, decimal_places=4)

    def __str__(self):
        return f"Exchange rate on {self.date}"



class BankRate(models.Model):
    bank_name = models.CharField(max_length=255)
    buy_rate = models.DecimalField(max_digits=10, decimal_places=4)
    sell_rate = models.DecimalField(max_digits=10, decimal_places=4)
    exchange_rate = models.ForeignKey(ExchangeRate2, on_delete=models.CASCADE, related_name='bank_rates')

    def __str__(self):
        return f"Rates from {self.bank_name} on {self.exchange_rate.date}"


class ExchangeRate(models.Model):
    timestamp = models.DateTimeField(auto_now_add=True)  # Automatically set the field to now when the record is first created
    date = models.CharField(max_length=10)  # Date of the exchange rate from Banxico API
    usd_to_mxn_rate = models.DecimalField(max_digits=10, decimal_places=4)  # Exchange rate with up to 4 decimal places

    def __str__(self):
        return f"{self.date}: {self.usd_to_mxn_rate}"
