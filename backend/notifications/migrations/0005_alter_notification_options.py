# Generated by Django 3.2.12 on 2022-02-09 14:03

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('notifications', '0004_alter_notification_notification_type'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='notification',
            options={'ordering': ['-created']},
        ),
    ]
