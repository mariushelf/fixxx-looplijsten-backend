# Generated by Django 3.1 on 2020-09-16 13:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("cases", "0013_auto_20200915_0735"),
    ]

    operations = [
        migrations.AlterField(
            model_name="stadium",
            name="name",
            field=models.CharField(
                choices=[
                    ("Onderzoek buitendienst", "Onderzoek buitendienst"),
                    ("2de Controle", "2de Controle"),
                    ("3de Controle", "3de Controle"),
                    ("Hercontrole", "Hercontrole"),
                    ("2de hercontrole", "2de hercontrole"),
                    ("3de hercontrole", "3de hercontrole"),
                    ("Avondronde", "Avondronde"),
                    ("Onderzoek advertentie", "Onderzoek advertentie"),
                    ("Weekend buitendienstonderzoek", "Weekend buitendienstonderzoek"),
                    ("Issuemelding", "Issuemelding"),
                    ("ZL Corporatie", "ZL Corporatie"),
                    ("Crimineel gebruik woning", "Crimineel gebruik woning"),
                ],
                max_length=255,
                unique=True,
            ),
        ),
    ]