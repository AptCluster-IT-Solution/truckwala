# Generated by Django 3.2.11 on 2022-02-03 06:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0005_auto_20210923_1100'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='address',
            field=models.CharField(default='kathmandu', max_length=255),
        ),
    ]