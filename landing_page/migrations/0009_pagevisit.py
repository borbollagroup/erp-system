# Generated by Django 5.0.7 on 2024-09-01 14:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('landing_page', '0008_alter_post_options'),
    ]

    operations = [
        migrations.CreateModel(
            name='PageVisit',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('home_visit_count', models.IntegerField(default=0)),
                ('portfolio_visit_count', models.IntegerField(default=0)),
                ('about_visit_count', models.IntegerField(default=0)),
            ],
        ),
    ]
