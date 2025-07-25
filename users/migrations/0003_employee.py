# Generated by Django 5.0.7 on 2024-08-03 13:47

import django.db.models.deletion
import django.utils.timezone
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0002_rename_image_profile_image'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Employee',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('position', models.CharField(max_length=100)),
                ('salary', models.DecimalField(decimal_places=2, max_digits=10)),
                ('date_hired', models.DateField()),
                ('attendance', models.PositiveIntegerField(default=0)),
                ('is_active', models.BooleanField(default=True)),
                ('department', models.CharField(max_length=100)),
                ('sat_salary', models.DecimalField(decimal_places=2, max_digits=10)),
                ('IMSS', models.DecimalField(decimal_places=2, max_digits=10)),
                ('INFONAVIT', models.DecimalField(decimal_places=2, max_digits=10)),
                ('bonus', models.DecimalField(decimal_places=2, max_digits=10)),
                ('date_posted', models.DateTimeField(default=django.utils.timezone.now)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
