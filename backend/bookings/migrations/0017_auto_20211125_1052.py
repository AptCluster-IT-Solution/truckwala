# Generated by Django 3.2.9 on 2021-11-25 10:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bookings', '0016_transaction_created'),
    ]

    operations = [
        migrations.AddField(
            model_name='customerad',
            name='product_type',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='customerad',
            name='unit',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='driverad',
            name='product_type',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='driverad',
            name='unit',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]