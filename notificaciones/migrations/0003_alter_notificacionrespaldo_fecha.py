# Generated by Django 3.2.5 on 2022-08-03 00:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('notificaciones', '0002_notificacionrespaldo_fecha'),
    ]

    operations = [
        migrations.AlterField(
            model_name='notificacionrespaldo',
            name='fecha',
            field=models.DateField(blank=True, default='19:32:48'),
        ),
    ]
