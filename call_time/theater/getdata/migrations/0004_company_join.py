# Generated by Django 4.1.5 on 2023-04-23 21:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("getdata", "0003_conflict"),
    ]

    operations = [
        migrations.AddField(
            model_name="company",
            name="join",
            field=models.BooleanField(default=True),
        ),
    ]
