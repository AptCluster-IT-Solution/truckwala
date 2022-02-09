# Generated by Django 3.2.12 on 2022-02-09 14:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('vehicles', '0002_vehiclecategory_image'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='vehicle',
            name='capacity',
        ),
        migrations.AddField(
            model_name='vehicle',
            name='area_of_loading_space',
            field=models.CharField(default='1x1x1', max_length=255),
            preserve_default=False,
        ),
    ]
