# Generated by Django 3.2.12 on 2022-03-30 08:26

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('bookings', '0023_alter_transaction_options'),
    ]

    operations = [
        migrations.AlterField(
            model_name='transaction',
            name='booking',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='transactions', to='bookings.booking'),
        ),
    ]
