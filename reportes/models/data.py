from django.db import models
from datetime import date
from django.conf import settings
import os, unicodedata, re
from django.core.files.storage import FileSystemStorage

class AsciiFileSystemStorage(FileSystemStorage):
    def get_valid_name(self, name):
        # strip directory, work on basename
        basename, ext = os.path.splitext(name)
        # normalize unicode → NFKD, drop non-ascii
        slug = unicodedata.normalize('NFKD', basename) \
                          .encode('ascii', 'ignore') \
                          .decode('ascii')
        # collapse any non-word/space/-, replace spaces with -
        slug = re.sub(r'[^\w\s-]', '', slug).strip().replace(' ', '-')
        return f"{slug}{ext}"

# create an instance you’ll reuse
ascii_storage = AsciiFileSystemStorage()


class Client(models.Model):
    legal_name = models.CharField(max_length=200)
    tax_id = models.CharField(max_length=50)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=20, blank=True)

    def __str__(self):
        return self.legal_name

class Contact(models.Model):
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='contacts')
    name = models.CharField(max_length=200)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=20, blank=True)
    role = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return f"{self.name} ({self.client})"

class Project(models.Model):
    name = models.CharField(max_length=200)
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='projects')
    location_city = models.CharField(max_length=100)
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True, default=None)
    contract_number = models.CharField(max_length=100, blank=True)
    notify_contacts = models.ManyToManyField(
        'Contact',
        blank=True,
        related_name='notified_projects'
    )

    def __str__(self):
        return f"{self.name} ({self.client})"
    
class Drawing(models.Model):
    project     = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='drawings')
    description = models.CharField(max_length=255, blank=True)
    file        = models.FileField(
                     upload_to='project_drawings/',
                     storage=ascii_storage,        # ← use the ASCII storage
                 )
    uploaded_on = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.description or os.path.basename(self.file.name)


class Weather(models.Model):
    city = models.CharField(max_length=100)
    date = models.DateField()
    temp_c = models.DecimalField(max_digits=5, decimal_places=1)
    condition = models.CharField(max_length=100)
    wind_kmh = models.DecimalField(max_digits=6, decimal_places=2)
    humidity_pct = models.DecimalField(max_digits=5, decimal_places=2)

    class Meta:
        unique_together = (('city', 'date'),)

    def __str__(self):
        return f"{self.city} @ {self.date}"

