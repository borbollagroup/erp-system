# billing/migrations/0010_add_nullable_access_token.py
import uuid
from django.db import migrations, models

def backfill_tokens(apps, schema_editor):
    Quotation = apps.get_model('billing', 'Quotation')
    for q in Quotation.objects.all():
        q.access_token = uuid.uuid4().hex
        q.save(update_fields=['access_token'])

class Migration(migrations.Migration):

    dependencies = [
        ('billing', '0009_quotation_email_sent'),
    ]

    operations = [
        # 1) Add the field, allow NULL for now
        migrations.AddField(
            model_name='quotation',
            name='access_token',
            field=models.CharField(max_length=32, null=True),
        ),
        # 2) Back‐fill it on every existing row
        migrations.RunPython(backfill_tokens, reverse_code=migrations.RunPython.noop),
    ]
