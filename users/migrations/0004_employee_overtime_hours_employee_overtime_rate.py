# Generated by Django 5.0.7 on 2024-08-03 15:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0003_employee'),
    ]

    operations = [
        migrations.AddField(
            model_name='employee',
            name='overtime_hours',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=5),
        ),
        migrations.AddField(
            model_name='employee',
            name='overtime_rate',
            field=models.DecimalField(decimal_places=2, default=1.5, max_digits=10),
        ),
    ]
