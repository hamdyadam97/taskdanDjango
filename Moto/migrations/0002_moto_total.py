# Generated by Django 5.0.6 on 2024-06-14 13:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Moto', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='moto',
            name='total',
            field=models.PositiveIntegerField(default=1),
        ),
    ]
