# Generated by Django 3.2.5 on 2022-08-03 00:29

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('notificaciones', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='notificacionrespaldo',
            name='fecha',
            field=models.DateField(blank=True, default=datetime.datetime.now),
        ),
    ]
