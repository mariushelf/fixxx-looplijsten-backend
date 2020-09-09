# Generated by Django 3.1 on 2020-09-08 09:44

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='TeamSettings',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('settings', models.JSONField(default={'days': {'friday': {'day': {'length_of_list': 6, 'primary_stadium': 'Onderzoek buitendienst', 'secondary_stadia': ['2de Controle', '3de Controle']}, 'evening': {'length_of_list': 6, 'primary_stadium': 'Avondronde', 'secondary_stadia': ['Hercontrole', '2de hercontrole', '3de hercontrole']}}, 'monday': {'day': {'length_of_list': 6, 'primary_stadium': 'Onderzoek buitendienst', 'secondary_stadia': ['2de Controle', '3de Controle']}, 'evening': {'length_of_list': 6, 'primary_stadium': 'Avondronde', 'secondary_stadia': ['Hercontrole', '2de hercontrole', '3de hercontrole']}}, 'saturday': {'day': {'length_of_list': 6, 'primary_stadium': 'Weekend buitendienstonderzoek', 'secondary_stadia': ['Hercontrole', '2de hercontrole', '3de hercontrole']}}, 'sunday': {'day': {'length_of_list': 6, 'primary_stadium': 'Weekend buitendienstonderzoek', 'secondary_stadia': ['Hercontrole', '2de hercontrole', '3de hercontrole']}}, 'thursday': {'day': {'length_of_list': 6, 'primary_stadium': 'Onderzoek buitendienst', 'secondary_stadia': ['2de Controle', '3de Controle']}, 'evening': {'length_of_list': 6, 'primary_stadium': 'Avondronde', 'secondary_stadia': ['Hercontrole', '2de hercontrole', '3de hercontrole']}}, 'tuesday': {'day': {}, 'evening': {'length_of_list': 6, 'primary_stadium': 'Avondronde', 'secondary_stadia': ['Hercontrole', '2de hercontrole', '3de hercontrole']}}, 'wednesday': {'day': {}, 'evening': {'length_of_list': 6, 'primary_stadium': 'Avondronde', 'secondary_stadia': ['Hercontrole', '2de hercontrole', '3de hercontrole']}}}, 'opening_date': '2019-01-01', 'postal_codes': [{'range_end': 1109, 'range_start': 1000}], 'projects': ['Bed en breakfast 2019', 'Burgwallenproject Oudezijde', 'Corpo-rico', 'Digital toezicht Safari', 'Digital toezicht Zebra', 'Haarlemmerbuurt', 'Hotline', 'Mystery Guest', 'Project Andes', 'Project Jordaan', 'Project Lobith', 'Safari', 'Safari 2015', 'Social Media 2019', 'Woonschip (woonboot)', 'Zebra']})),
            ],
        ),
    ]
