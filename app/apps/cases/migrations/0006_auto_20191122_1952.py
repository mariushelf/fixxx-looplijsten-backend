# Generated by Django 2.1.11 on 2019-11-22 19:52

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("cases", "0005_auto_20191120_1039"),
    ]

    operations = [
        migrations.RemoveField(model_name="case", name="address",),
        migrations.RemoveField(model_name="case", name="postal_code",),
        migrations.RemoveField(model_name="case", name="stadium_code",),
        migrations.AddField(
            model_name="case",
            name="case_id",
            field=models.CharField(max_length=255, null=True),
        ),
    ]