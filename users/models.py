from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

from PIL import Image

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    image = models.ImageField(default='default.jpg', upload_to='profile_pics')
    cellphone = models.CharField(max_length=15)
    visibility      = models.CharField(max_length=10 , default=1)

    def __str__(self):
        return f'{self.user.username} Profile'

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        img = Image.open(self.image.path)

        if img.height > 250 or img.width > 200:
            output_size = (250, 200)
            img.thumbnail(output_size)
            img.save(self.image.path)
    
class Employee(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    position = models.CharField(max_length=100)
    salary = models.DecimalField(max_digits=10, decimal_places=2)
    date_hired = models.DateField()
    attendance = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    department = models.CharField(max_length=100)
    sat_salary = models.DecimalField(max_digits=10,decimal_places=2)
    IMSS       = models.DecimalField(max_digits=10,decimal_places=2)
    INFONAVIT  = models.DecimalField(max_digits=10,decimal_places=2)
    bonus      = models.DecimalField(max_digits=10,decimal_places=2)
    overtime_hours = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    overtime_rate = models.DecimalField(max_digits=10, decimal_places=2, default=1.5)  # 1.5x regular rate
    #overtime_pay = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    date_posted = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f'{self.user.username} Employee'

    def increment_attendance(self):
        self.attendance += 1
        self.save()

    def deactivate_employee(self):
        self.is_active = False
        self.save()

    def activate_employee(self):
        self.is_active = True
        self.save()

    def calculate_overtime_pay(self):
        self.overtime_pay = self.overtime_hours * 100

    def add_overtime_hours(self, hours):
        self.overtime_hours += hours
        self.calculate_overtime_pay()
        self.save()