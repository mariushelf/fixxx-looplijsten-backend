# Generated by Django 3.1 on 2020-10-06 07:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cases', '0015_auto_20200916_1543'),
    ]

    operations = [
        migrations.AlterField(
            model_name='project',
            name='name',
            field=models.CharField(max_length=255, unique=True),
        ),
        migrations.AlterField(
            model_name='stadium',
            name='name',
            field=models.CharField(max_length=255, unique=True),
        ),
    ]
