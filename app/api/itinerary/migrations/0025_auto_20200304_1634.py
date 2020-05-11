# Generated by Django 2.2.10 on 2020-03-04 16:34

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('itinerary', '0024_auto_20200304_1619'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='itinerary',
            name='enforcers',
        ),
        migrations.RemoveField(
            model_name='itinerary',
            name='supervisors',
        ),
        migrations.AddField(
            model_name='itinerary',
            name='team',
            field=models.ManyToManyField(related_name='itineraries', to=settings.AUTH_USER_MODEL),
        ),
    ]
