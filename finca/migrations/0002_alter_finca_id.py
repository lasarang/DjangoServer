# Generated by Django 3.2.5 on 2021-08-10 15:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('finca', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='finca',
            name='id',
            field=models.BigAutoField(primary_key=True, serialize=False),
        ),
    ]
