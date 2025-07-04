# Generated by Django 5.2.2 on 2025-06-12 08:03

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('manager', '0004_tenant_id_photo_alter_tenant_emergency_contact_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='tenant',
            name='phone_number',
            field=models.CharField(default=0, max_length=15, validators=[django.core.validators.RegexValidator(message='Enter a valid phone number.', regex='^\\+?[\\d\\s\\-]{7,15}$')]),
            preserve_default=False,
        ),
    ]
