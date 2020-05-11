# Generated by Django 2.2.10 on 2020-03-09 15:25

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('cases', '0009_auto_20200309_1525'),
        ('itinerary', '0034_itinerarysettings_target_itinerary_length'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='itinerarysettings',
            name='exclude_states',
        ),
        migrations.RemoveField(
            model_name='itinerarysettings',
            name='primary_state',
        ),
        migrations.RemoveField(
            model_name='itinerarysettings',
            name='secondary_states',
        ),
        migrations.AddField(
            model_name='itinerarysettings',
            name='exclude_stadium',
            field=models.ManyToManyField(related_name='settings_as_exclude_stadium', to='cases.Stadium'),
        ),
        migrations.AddField(
            model_name='itinerarysettings',
            name='primary_stadium',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE,
                                    related_name='settings_as_primary_stadium', to='cases.Stadium'),
        ),
        migrations.AddField(
            model_name='itinerarysettings',
            name='secondary_stadia',
            field=models.ManyToManyField(related_name='settings_as_secondary_stadium', to='cases.Stadium'),
        ),
    ]
