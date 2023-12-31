# Generated by Django 4.1.5 on 2023-04-13 20:55

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("getdata", "0002_delete_conflicts"),
    ]

    operations = [
        migrations.CreateModel(
            name="Conflict",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("start_date", models.DateField()),
                ("end_date", models.DateField(blank=True, null=True)),
                ("start_time", models.TimeField(blank=True, null=True)),
                ("end_time", models.TimeField(blank=True, null=True)),
                (
                    "company",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="getdata.company",
                    ),
                ),
                (
                    "performer_id",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="getdata.performers",
                    ),
                ),
            ],
        ),
    ]
