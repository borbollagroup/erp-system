from django.db import models
from django.utils.timezone import now
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist




class Customer(models.Model):
    name = models.CharField(max_length=200, verbose_name="Customer Name / Nombre del Cliente", default="Default Customer")    
    manager = models.CharField(max_length=100, verbose_name="Manager Name / Nombre del Gerente", default="Default Manager")
    address = models.CharField(max_length=255, verbose_name="Address / Dirección", default="Default Address")
    contact_email = models.EmailField(max_length=100, verbose_name="Contact Email / Correo Electrónico de Contacto", default="default@example.com")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Created At / Creado En")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Updated At / Actualizado En")

    def __str__(self):
        return self.name

class Contact2(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name="contacts", verbose_name="Customer / Cliente")
    
    name = models.CharField(max_length=50, verbose_name="Nombre / Name", default="Generico")
    email = models.EmailField(max_length=50, verbose_name="Correo Electrónico / Email", default="default@example.com")
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="contact_profile", verbose_name="System User / Usuario del Sistema", null=True, blank=True)
    phone_number = models.CharField(max_length=20, verbose_name="Phone Number / Número de Teléfono")
    position = models.CharField(max_length=100, verbose_name="Position / Posición")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Created At / Creado En", blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Updated At / Actualizado En", blank=True, null=True)

    def save(self, *args, **kwargs):
        if not self.user_id:
            try:
                user = User.objects.create_user(
                    username=self.email,
                    email=self.email,
                    password=User.objects.make_random_password()
                )
                name_parts = self.name.split(maxsplit=1)
                user.first_name = name_parts[0]
                user.last_name = name_parts[1] if len(name_parts) > 1 else ""
                user.save()
                self.user = user
            except Exception as e:
                raise ValueError(f"Failed to create User: {e}")
        super(Contact2, self).save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} ({self.customer.name})"

class Quotation(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name="quotations", verbose_name="Customer / Cliente")
    #contact = models.ForeignKey(Contact2, on_delete=models.CASCADE, related_name='quotations', null=True, blank=True)
    project_name = models.CharField(max_length=200, verbose_name="Project Name / Nombre del Proyecto", default="Default Project")
    quotation_date = models.DateField(verbose_name="Quotation Date / Fecha de Cotización", default=now)
    start_date = models.DateField(verbose_name="Start Date / Fecha de Inicio", null=True, blank=True)
    end_date = models.DateField(verbose_name="End Date / Fecha de Finalización", null=True, blank=True)
    project_cost = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="Project Cost / Costo del Proyecto", default=0.00)
    currency = models.CharField(max_length=10, verbose_name="Currency / Moneda", default="MXN")
    exchange_rate = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Exchange Rate / Tipo de Cambio", default=0.00)
    payment_terms = models.CharField(max_length=100, verbose_name="Payment Terms / Términos de Pago", default="30%")
    validity_date = models.DateField(verbose_name="Validity Date / Fecha de Validez", null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Created At / Creado En")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Updated At / Actualizado En")


    def __str__(self):
        return self.project_name

    @property
    def folio(self):
        starting_number = 10945  # Define the starting number for folio
        return f"QT-{starting_number + self.id - 1:05}"  # Adjust the format

def get_default_quotation():
    try:
        # Fetch the first existing quotation as default
        return Quotation.objects.first().id 
    except (Quotation.DoesNotExist, AttributeError):
        # If no quotation exists, raise an error
        raise ObjectDoesNotExist("No default Quotation exists. Please create one first.")



class IndirectCost(models.Model):
    quotation = models.ForeignKey(Quotation, on_delete=models.CASCADE, related_name='indirect_costs', verbose_name="Quotation / Cotización", null=True, blank=True)
    description = models.CharField(max_length=200, verbose_name="Cost Description / Descripción del Costo", default="Default Indirect Cost")
    amount = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="Amount / Monto", default=0.00)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Created At / Creado En", blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Updated At / Actualizado En", blank=True, null=True)

    def __str__(self):
        return self.description

class Material(models.Model):
    quotation = models.ForeignKey(Quotation, on_delete=models.CASCADE, related_name="materials", verbose_name="Quotation / Cotización")
    material = models.CharField(max_length=100, verbose_name="Material Name / Nombre del Material", default="Default Material")
    spec = models.CharField(max_length=200, verbose_name="Specification / Especificación", blank=True, null=True)
    unit = models.CharField(max_length=50, verbose_name="Unit / Unidad", default="pcs")
    qty = models.PositiveIntegerField(verbose_name='Quantity / Cantidad', default=1)
    unit_cost = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="Unit Cost / Costo Unitario", default=0.00)
    remarks = models.TextField(verbose_name="Remarks / Observaciones", blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Created At / Creado En", blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Updated At / Actualizado En", blank=True, null=True)

    def __str__(self):
        return self.material

class Labor(models.Model):
    quotation = models.ForeignKey(Quotation, on_delete=models.CASCADE, related_name="labors", verbose_name="Quotation / Cotización")
    item = models.CharField(max_length=200, verbose_name="Labor Item / Tarea Laboral", default="Default Labor")
    worker_qty = models.PositiveIntegerField(verbose_name="Worker Quantity / Cantidad de Trabajadores", default=1)
    work_days = models.PositiveIntegerField(verbose_name="Work Days / Días de Trabajo", default=1)
    unit_price = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="Unit Price / Precio Unitario", default=0.00)
    remarks = models.TextField(verbose_name="Remarks / Observaciones", blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Created At / Creado En", blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Updated At / Actualizado En", blank=True, null=True)

    def __str__(self):
        return self.item

class Equipment(models.Model):
    quotation = models.ForeignKey(Quotation, on_delete=models.CASCADE, related_name='equipments', verbose_name='Quotation / Cotización')
    description = models.CharField(max_length=200, verbose_name='Equipment Description / Descripción del Equipo', default="Default Equipment")
    qty = models.PositiveIntegerField(verbose_name='Quantity / Cantidad', default=1)
    days = models.PositiveIntegerField(verbose_name='Days / Días', default=1)
    unit_price = models.DecimalField(max_digits=12, decimal_places=2, verbose_name='Unit Price / Precio Unitario', default=0.00)
    remarks = models.TextField(verbose_name='Remarks / Observaciones', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Created At / Creado En", blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Updated At / Actualizado En", blank=True, null=True)

    def __str__(self):
        return self.description
