# Generated by Django 3.1.3 on 2021-07-07 20:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cultivo', '0002_auto_20210707_1952'),
    ]

    operations = [
        migrations.AddField(
            model_name='cultivo',
            name='maximo_precipitacion',
            field=models.FloatField(blank=True, default=0),
        ),
    ]
