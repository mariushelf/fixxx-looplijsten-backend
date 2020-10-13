# Generated by Django 3.0.7 on 2020-07-06 12:12

import django.core.validators
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("itinerary", "0047_auto_20200706_1145"),
    ]

    operations = [
        migrations.CreateModel(
            name="PostalCodeSettings",
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
                (
                    "postal_code_range_start",
                    models.IntegerField(
                        blank=True,
                        null=True,
                        validators=[
                            django.core.validators.MinValueValidator(1000),
                            django.core.validators.MaxValueValidator(1109),
                        ],
                    ),
                ),
                (
                    "postal_code_range_end",
                    models.IntegerField(
                        blank=True,
                        null=True,
                        validators=[
                            django.core.validators.MinValueValidator(1000),
                            django.core.validators.MaxValueValidator(1109),
                        ],
                    ),
                ),
                (
                    "itinerary",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="postal_code_settings",
                        to="itinerary.Itinerary",
                    ),
                ),
                (
                    "itinerary_settings",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="postal_code_ranges",
                        to="itinerary.ItinerarySettings",
                    ),
                ),
            ],
        ),
        migrations.DeleteModel(
            name="PostalCodeRange",
        ),
    ]
