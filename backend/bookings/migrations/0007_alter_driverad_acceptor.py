# Generated by Django 3.2.7 on 2021-09-28 00:52

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0005_auto_20210923_1100'),
        ('bookings', '0006_auto_20210926_1006'),
    ]

    operations = [
        migrations.AlterField(
            model_name='driverad',
            name='acceptor',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='accepted_ads', to='users.customer'),
        ),
    ]
