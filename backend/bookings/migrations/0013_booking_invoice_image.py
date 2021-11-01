# Generated by Django 3.2.7 on 2021-10-09 09:22

import bookings.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bookings', '0012_auto_20211006_0619'),
    ]

    operations = [
        migrations.AddField(
            model_name='booking',
            name='invoice_image',
            field=models.ImageField(blank=True, null=True, upload_to=bookings.models.get_invoice_image_path),
        ),
    ]