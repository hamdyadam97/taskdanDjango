# Generated by Django 5.0.6 on 2024-06-14 12:27

import User.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('User', '0006_alter_user_email'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='agreement',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='user',
            name='file',
            field=models.FileField(blank=True, null=True, upload_to=User.models.upload_to_profile_pic),
        ),
        migrations.AddField(
            model_name='user',
            name='rules_agreed',
            field=models.BooleanField(default=False),
        ),
    ]
