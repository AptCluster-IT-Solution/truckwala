# Generated by Django 3.2.7 on 2021-11-01 12:28

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('bookings', '0015_alter_transaction_booking'),
    ]

    operations = [
        migrations.AddField(
            model_name='transaction',
            name='created',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
    ]
