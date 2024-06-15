# Generated by Django 5.0.6 on 2024-06-14 11:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('User', '0005_user_phone_code'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='email',
            field=models.EmailField(default=1, max_length=254, verbose_name='email address'),
            preserve_default=False,
        ),
    ]
