# Generated by Django 2.2.10 on 2020-04-07 11:41

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cases', '0012_auto_20200407_1141'),
        ('itinerary', '0037_auto_20200313_1250'),
    ]

    operations = [
        migrations.AddField(
            model_name='itinerarysettings',
            name='start_case',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='cases.Case'),
        ),
    ]
