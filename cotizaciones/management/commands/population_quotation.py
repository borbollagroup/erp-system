from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from cotizaciones.models import Customer, Contact, Quotation, Material, Labor, Equipment, IndirectCost
from django.utils.timezone import now
import random
from decimal import Decimal


class Command(BaseCommand):
    help = "Populates the database with sample data for testing."

    def handle(self, *args, **kwargs):
        # Populate Customers
        customers = []
        for i in range(1, 4):
            customer, created = Customer.objects.update_or_create(
                name=f"Customer {i}",
                defaults={
                    "manager": f"Manager {i}",
                }
            )
            customers.append(customer)

        # Populate Contacts for each Customer
        for customer in customers:
            for j in range(1, 4):  # Add 3 contacts per customer
                user, created = User.objects.update_or_create(
                    username=f"contact_{customer.id}_{j}",
                    defaults={
                        "email": f"contact_{customer.id}_{j}@example.com",
                        "first_name": f"Contact {j}",
                        "last_name": f"Customer {customer.id}",
                    }
                )
                Contact.objects.update_or_create(
                    customer=customer,
                    name=f"Contact {j} for {customer.name}",
                    defaults={
                        "email": user.email,
                        "user": user,
                        "phone_number": f"+123456789{j}",
                        "position": f"Position {j}",
                    }
                )

        # Populate Quotations
        for customer in customers:
            for k in range(1, 4):  # Add 3 quotations per customer
                quotation, created = Quotation.objects.update_or_create(
                    customer=customer,
                    project_name=f"Project {k} for {customer.name}",
                    defaults={
                        "quotation_date": now().date(),
                        "start_date": now().date(),
                        "end_date": now().date(),
                        "project_cost": Decimal("0.00"),  # Will calculate later
                    }
                )

                # Populate Materials
                for m in range(1, 4):  # Add 3 materials per quotation
                    unit_cost = Decimal(f"{random.randint(100, 500)}.00")
                    total_cost = unit_cost * Decimal("10")
                    Material.objects.update_or_create(
                        quotation=quotation,
                        material=f"Material {m} for {quotation.project_name}",
                        defaults={
                            "spec": f"Specification {m}",
                            "unit": "KG",
                            "unit_cost": unit_cost,
                            "total": total_cost,
                            "remarks": f"Remarks for Material {m}",
                        }
                    )

                # Populate Labor
                for l in range(1, 4):  # Add 3 labor items per quotation
                    unit_price = Decimal(f"{random.randint(100, 500)}.00")
                    total_price = unit_price * Decimal("8")
                    Labor.objects.update_or_create(
                        quotation=quotation,
                        item=f"Labor {l} for {quotation.project_name}",
                        defaults={
                            "worker_qty": random.randint(1, 5),
                            "work_days": random.randint(1, 10),
                            "unit_price": unit_price,
                            "total_price": total_price,
                            "remarks": f"Remarks for Labor {l}",
                        }
                    )

                # Populate Equipment
                for e in range(1, 4):  # Add 3 equipment items per quotation
                    unit_price = Decimal(f"{random.randint(500, 1000)}.00")
                    total_price = unit_price * Decimal("5")
                    Equipment.objects.update_or_create(
                        quotation=quotation,
                        description=f"Equipment {e} for {quotation.project_name}",
                        defaults={
                            "qty": random.randint(1, 3),
                            "days": random.randint(1, 7),
                            "unit_price": unit_price,
                            "total_price": total_price,
                            "remarks": f"Remarks for Equipment {e}",
                        }
                    )

                # Update project cost (sum of all items)
                materials_total = sum(m.total for m in quotation.materials.all())
                labors_total = sum(l.total_price for l in quotation.labors.all())
                equipments_total = sum(e.total_price for e in quotation.equipments.all())
                quotation.project_cost = materials_total + labors_total + equipments_total
                quotation.save()

        self.stdout.write(self.style.SUCCESS("Database populated successfully!"))
