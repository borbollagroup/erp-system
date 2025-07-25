# Generated by Django 5.0.7 on 2025-06-12 04:43

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Client',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('legal_name', models.CharField(max_length=200)),
                ('tax_id', models.CharField(max_length=50)),
                ('tax_system', models.CharField(max_length=10)),
                ('email', models.EmailField(max_length=254)),
                ('phone', models.CharField(max_length=20)),
                ('default_invoice_use', models.CharField(max_length=3)),
                ('street', models.CharField(max_length=200)),
                ('exterior', models.CharField(max_length=20)),
                ('interior', models.CharField(blank=True, max_length=20, null=True)),
                ('neighborhood', models.CharField(max_length=100)),
                ('city', models.CharField(max_length=100)),
                ('municipality', models.CharField(max_length=100)),
                ('zip_code', models.CharField(max_length=10)),
                ('state', models.CharField(max_length=100)),
                ('country', models.CharField(default='MEX', max_length=3)),
            ],
        ),
        migrations.CreateModel(
            name='DailyReport',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField()),
                ('temp_c', models.DecimalField(blank=True, decimal_places=1, max_digits=5, null=True)),
                ('condition', models.CharField(blank=True, max_length=100, null=True)),
                ('wind_kmh', models.DecimalField(blank=True, decimal_places=2, max_digits=6, null=True)),
                ('humidity_pct', models.PositiveSmallIntegerField(blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Contact',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200)),
                ('email', models.EmailField(blank=True, max_length=254, null=True)),
                ('phone', models.CharField(blank=True, max_length=20, null=True)),
                ('role', models.CharField(blank=True, max_length=100, null=True)),
                ('client', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='contacts', to='reportes.client')),
            ],
        ),
        migrations.CreateModel(
            name='ActivityEntry',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('activity', models.CharField(max_length=200)),
                ('quantity', models.DecimalField(decimal_places=2, max_digits=10)),
                ('unit', models.CharField(max_length=20)),
                ('description', models.TextField(blank=True)),
                ('report', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='activities', to='reportes.dailyreport')),
            ],
        ),
        migrations.CreateModel(
            name='EquipmentEntry',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('quantity', models.PositiveIntegerField()),
                ('hours', models.DecimalField(decimal_places=2, max_digits=5)),
                ('comments', models.TextField(blank=True)),
                ('report', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='equipment', to='reportes.dailyreport')),
            ],
        ),
        migrations.CreateModel(
            name='ManpowerEntry',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('role', models.CharField(max_length=100)),
                ('quantity', models.PositiveIntegerField()),
                ('hours', models.DecimalField(decimal_places=2, max_digits=5)),
                ('comments', models.TextField(blank=True)),
                ('report', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='manpower', to='reportes.dailyreport')),
            ],
        ),
        migrations.CreateModel(
            name='Photo',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image', models.ImageField(upload_to='report_photos/')),
                ('caption', models.CharField(blank=True, max_length=200)),
                ('report', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='photos', to='reportes.dailyreport')),
            ],
        ),
        migrations.CreateModel(
            name='Project',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200)),
                ('location_city', models.CharField(default='Saltillo', max_length=100)),
                ('start_date', models.DateField(blank=True, null=True)),
                ('contract_number', models.CharField(blank=True, max_length=100, null=True)),
                ('client', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='projects', to='reportes.client')),
            ],
        ),
        migrations.AddField(
            model_name='dailyreport',
            name='project',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='daily_reports', to='reportes.project'),
        ),
    ]
