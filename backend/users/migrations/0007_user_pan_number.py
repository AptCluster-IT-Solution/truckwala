# Generated by Django 3.2.11 on 2022-02-03 06:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0006_user_address'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='pan_number',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]
