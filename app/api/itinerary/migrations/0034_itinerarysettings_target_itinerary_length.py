# Generated by Django 2.2.10 on 2020-03-09 14:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('itinerary', '0033_auto_20200309_1242'),
    ]

    operations = [
        migrations.AddField(
            model_name='itinerarysettings',
            name='target_itinerary_length',
            field=models.IntegerField(default=6),
        ),
    ]
