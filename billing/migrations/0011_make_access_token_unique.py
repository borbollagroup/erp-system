# billing/migrations/0011_make_access_token_unique.py
import uuid
from django.db import migrations, models

def generate_token():
    return uuid.uuid4().hex

class Migration(migrations.Migration):

    dependencies = [
        ('billing', '0010_add_nullable_access_token'),
    ]

    operations = [
        # Now make it non-nullable and unique, with a callable default for new rows
        migrations.AlterField(
            model_name='quotation',
            name='access_token',
            field=models.CharField(
                max_length=32,
                unique=True,
                null=False,
                default=generate_token,
            ),
        ),
    ]
