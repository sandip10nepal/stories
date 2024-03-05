# Generated by Django 5.0.1 on 2024-02-22 00:59

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("home", "0002_rename_category_category_name"),
    ]

    operations = [
        migrations.CreateModel(
            name="mywords",
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
                ("word", models.CharField(max_length=100, unique=True)),
                ("meaning", models.TextField()),
            ],
        ),
    ]