# Generated by Django 2.1.11 on 2019-11-11 11:11

import django.contrib.auth.validators
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('users', '0004_auto_20191104_1046'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='username',
            field=models.CharField(default='fixxx',
                                   error_messages={'unique': 'A user with that username already exists.'},
                                   help_text='Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.',
                                   max_length=150, unique=True,
                                   validators=[django.contrib.auth.validators.UnicodeUsernameValidator()],
                                   verbose_name='username'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='user',
            name='email',
            field=models.EmailField(error_messages={'unique': 'A user with that email already exists.'}, max_length=254,
                                    unique=True),
        ),
    ]
