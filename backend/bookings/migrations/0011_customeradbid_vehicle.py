# Generated by Django 3.2.7 on 2021-10-06 06:16

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('vehicles', '0001_initial'),
        ('bookings', '0010_driverad_vehicle'),
    ]

    operations = [
        migrations.AddField(
            model_name='customeradbid',
            name='vehicle',
            field=models.ForeignKey(blank=True, default=1, on_delete=django.db.models.deletion.CASCADE, related_name='bid_ads', to='vehicles.vehicle'),
            preserve_default=False,
        ),
    ]
