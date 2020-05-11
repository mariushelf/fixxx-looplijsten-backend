# Generated by Django 2.2.10 on 2020-03-09 10:30

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('cases', '0006_auto_20191122_1952'),
    ]

    operations = [
        migrations.CreateModel(
            name='Project',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('project', models.CharField(choices=[('Bed en breakfast 2019', 'Bed en breakfast 2019'),
                                                      ('Burgwallenproject Oudezijde', 'Burgwallenproject Oudezijde'),
                                                      ('Corpo-rico', 'Corpo-rico'),
                                                      ('Digital toezicht Safari', 'Digital toezicht Safari'),
                                                      ('Digital toezicht Zebra', 'Digital toezicht Zebra'),
                                                      ('Haarlemmerbuurt', 'Haarlemmerbuurt'), ('Hotline', 'Hotline'),
                                                      ('Mystery Guest', 'Mystery Guest'),
                                                      ('Project Andes', 'Project Andes'),
                                                      ('Project Jordaan', 'Project Jordaan'),
                                                      ('Project Lobith', 'Project Lobith'),
                                                      ('Project Sahara', 'Project Sahara'), ('Safari', 'Safari'),
                                                      ('Safari 2015', 'Safari 2015'),
                                                      ('Sahara Adams Suites', 'Sahara Adams Suites'),
                                                      ('Sahara hele woning', 'Sahara hele woning'),
                                                      ('Sahara meer dan 4', 'Sahara meer dan 4'),
                                                      ('Sahara Recensies', 'Sahara Recensies'),
                                                      ('Sahara veel adv', 'Sahara veel adv'),
                                                      ('Social Media 2019', 'Social Media 2019'),
                                                      ('Woonschip (woonboot)', 'Woonschip (woonboot)'),
                                                      ('Zebra', 'Zebra')], max_length=255, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='State',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('state', models.CharField(
                    choices=[('2de Controle', '2de Controle'), ('2de hercontrole', '2de hercontrole'),
                             ('3de Controle', '3de Controle'), ('3de hercontrole', '3de hercontrole'),
                             ('Avondronde', 'Avondronde'), ('Hercontrole', 'Hercontrole'),
                             ('Onderzoek advertentie', 'Onderzoek advertentie'),
                             ('Onderzoek buitendienst', 'Onderzoek buitendienst'),
                             ('Weekend buitendienstonderzoek', 'Weekend buitendienstonderzoek')], max_length=255,
                    unique=True)),
            ],
        ),
    ]
