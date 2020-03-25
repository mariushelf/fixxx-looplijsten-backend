# Generated by Django 2.2.10 on 2020-03-09 12:40

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('itinerary', '0031_itinerarysettings'),
    ]

    operations = [
        migrations.AlterField(
            model_name='itinerarysettings',
            name='itinerary',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='settings', to='itinerary.Itinerary', unique=True),
        ),
    ]