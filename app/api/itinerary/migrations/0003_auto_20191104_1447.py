# Generated by Django 2.1.9 on 2019-11-04 14:47

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('itinerary', '0002_auto_20191104_1421'),
    ]

    operations = [
        migrations.AlterField(
            model_name='itineraryitem',
            name='itinerary',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='items', to='itinerary.Itinerary'),
        ),
    ]
