# Generated by Django 5.0.7 on 2025-06-25 17:03

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('billing', '0006_alter_quotation_options'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='quotation',
            options={'ordering': ['-date_issued']},
        ),
    ]
