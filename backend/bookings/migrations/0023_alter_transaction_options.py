# Generated by Django 3.2.12 on 2022-02-09 14:03

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('bookings', '0022_alter_transaction_driver'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='transaction',
            options={'ordering': ['-date']},
        ),
    ]