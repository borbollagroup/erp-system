from django.db import models
from django.core.exceptions import ValidationError
from django.utils import timezone
from decimal import Decimal

from django.urls import reverse

from reportes.models.data import Client, Project, Contact

import uuid

def generate_token():
    # return a 32-char hex string
    return uuid.uuid4().hex


class Supplier(models.Model):
    name          = models.CharField(max_length=200)
    tax_id        = models.CharField("Tax ID", max_length=50, blank=True)
    address       = models.TextField(blank=True)
    contact_email = models.EmailField(blank=True)
    phone         = models.CharField(max_length=20, blank=True)

    def __str__(self):
        return self.name


class SupplierContact(models.Model):
    supplier = models.ForeignKey(
        Supplier, on_delete=models.CASCADE, related_name="contacts"
    )
    name     = models.CharField(max_length=200)
    email    = models.EmailField(blank=True)
    phone    = models.CharField(max_length=20, blank=True)
    role     = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return f"{self.name} ({self.supplier.name})"


class Quotation(models.Model):
    QUOTE_TYPE = [
        ("out", "To Client"),
        ("in",  "From Supplier"),
    ]
    CURRENCY_CHOICES = [
        ('USD', 'USD'),
        ('MXN', 'MXN'),
    ]
    notify_contacts = models.ManyToManyField(
        Contact,
        blank=True,
        related_name='quotations'
    )    
    email_sent = models.BooleanField(default=False)
    coin         = models.CharField(max_length=3, choices=CURRENCY_CHOICES, default='MXN')
    quote_type   = models.CharField(max_length=3, choices=QUOTE_TYPE, default="out")
    client       = models.ForeignKey(
        Client, null=True, blank=True,
        on_delete=models.SET_NULL, related_name="sales_quotes"
    )
    supplier     = models.ForeignKey(
        Supplier, null=True, blank=True,
        on_delete=models.SET_NULL, related_name="purchase_quotes"
    )
    project      = models.ForeignKey(
        Project, on_delete=models.CASCADE, related_name="quotations"
    )
    number       = models.CharField(max_length=50)
    date_issued  = models.DateField()
    valid_until  = models.DateField(null=True, blank=True)
    total_amount = models.DecimalField(max_digits=12, decimal_places=2)
    access_token = models.CharField(max_length=32, unique=True, default=generate_token)

    def get_absolute_url(self):
        return reverse('billing:quotation_detail', args=[self.pk])

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        super().save(*args, **kwargs)

        if is_new:
            # YYMMDD
            today = timezone.now().strftime("%y%m%d")

            # Build client_code from the initials of each word
            name = self.client.legal_name or ""
            initials = [w[0].upper() for w in name.split() if w]
            client_code = "".join(initials)

            seq = 11348 + self.pk
            self.number = f"QT-{client_code}-{seq}-{today}"

            # Only update the number field
            super().save(update_fields=['number'])

    def clean(self):
        if self.quote_type == "out":
            if not self.client:
                raise ValidationError("Outgoing quotes must have a client.")
            if self.supplier:
                raise ValidationError("Outgoing quotes cannot have a supplier.")
        else:
            if not self.supplier:
                raise ValidationError("Incoming quotes must have a supplier.")
            if self.client:
                raise ValidationError("Incoming quotes cannot have a client.")

    @property
    def is_outgoing(self):
        return self.quote_type == "out"

    @property
    def is_incoming(self):
        return self.quote_type == "in"

    def __str__(self):
        arrow = "→" if self.is_outgoing else "←"
        party = self.client or self.supplier
        return f"{self.number} {arrow} {party}"
    
    def get_secure_url(self):
        return reverse('billing:quotation_public', args=[str(self.access_token)])

    class Meta:
        ordering = ['-date_issued']    # newest first


# billing/models.py

class QuotationItem(models.Model):
    CATEGORY = [
        ("labor",     "Labor"),
        ("material",  "Material"),
        ("equipment", "Equipment"),
        ("overhead",  "Overhead"),    # ← New!
    ]
    quotation   = models.ForeignKey(
        Quotation, on_delete=models.CASCADE, related_name="items"
    )
    category    = models.CharField(max_length=10, choices=CATEGORY)
    description = models.CharField(max_length=255)
    qty         = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    days        = models.DecimalField(max_digits=8, decimal_places=2, default=1)
    unit_price  = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    remarks     = models.CharField(max_length=255, blank=True)

    @property
    def total_price(self):
        return (self.qty * self.days * self.unit_price).quantize(Decimal("1.00"))

    def __str__(self):
        return f"{self.description} [{self.get_category_display()}]"



class PurchaseOrder(models.Model):
    quotation    = models.ForeignKey(
        Quotation,
        limit_choices_to={"quote_type": "in"},
        on_delete=models.CASCADE,
        related_name="purchase_orders"
    )
    po_number    = models.CharField("PO Number", max_length=50)
    date_issued  = models.DateField()
    total_amount = models.DecimalField(max_digits=12, decimal_places=2)

    def clean(self):
        if self.quotation.quote_type != "in":
            raise ValidationError("POs can only be created for supplier quotes.")

    def __str__(self):
        return f"PO {self.po_number} ← {self.quotation.supplier.name}"


class PurchaseOrderItem(models.Model):
    po          = models.ForeignKey(
        PurchaseOrder, on_delete=models.CASCADE, related_name="items"
    )
    description = models.CharField(max_length=255)
    qty         = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    days        = models.DecimalField(max_digits=8, decimal_places=2, default=1)
    unit_price  = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    remarks     = models.CharField(max_length=255, blank=True)

    @property
    def total_price(self):
        return (self.qty * self.days * self.unit_price).quantize(Decimal("1.00"))

    def __str__(self):
        return f"{self.description} (PO {self.po.po_number})"
