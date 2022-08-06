# Generated by Django 4.0.6 on 2022-08-04 19:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('notificaciones', '0010_alter_notificacionrespaldo_dia'),
    ]

    operations = [
        migrations.AlterField(
            model_name='notificacionrespaldo',
            name='dia',
            field=models.IntegerField(blank=True, choices=[(0, 'LUNES'), (1, 'MARTES'), (2, 'MIÉRCOLES'), (3, 'JUEVES'), (4, 'VIERNES'), (5, 'SÁBADO'), (6, 'DOMINGO')], default=3),
        ),
    ]
