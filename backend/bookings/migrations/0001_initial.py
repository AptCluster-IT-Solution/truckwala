# Generated by Django 3.2.6 on 2021-08-27 09:21

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Booking",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("start_time", models.DateTimeField(blank=True)),
                ("end_time", models.DateTimeField(blank=True)),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("P", "Pending"),
                            ("A", "Accepted"),
                            ("D", "Dispatched"),
                            ("F", "Fulfilled"),
                        ],
                        max_length=1,
                    ),
                ),
                ("created", models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name="CustomerAd",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("description", models.CharField(max_length=255)),
                ("start_place", models.CharField(max_length=255)),
                ("end_place", models.CharField(max_length=255)),
                ("cost", models.PositiveIntegerField(default=0)),
                ("quantity", models.PositiveIntegerField(default=0)),
                ("created", models.DateTimeField(auto_now_add=True)),
                ("start_time", models.DateTimeField(blank=True, null=True)),
                ("end_time", models.DateTimeField(blank=True, null=True)),
            ],
            options={"abstract": False},
        ),
        migrations.CreateModel(
            name="DriverAd",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("description", models.CharField(max_length=255)),
                ("start_place", models.CharField(max_length=255)),
                ("end_place", models.CharField(max_length=255)),
                ("cost", models.PositiveIntegerField(default=0)),
                ("quantity", models.PositiveIntegerField(default=0)),
                ("created", models.DateTimeField(auto_now_add=True)),
            ],
            options={"abstract": False},
        ),
    ]
