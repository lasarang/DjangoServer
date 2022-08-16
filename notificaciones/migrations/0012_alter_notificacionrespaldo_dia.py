# Generated by Django 3.2.5 on 2022-08-15 00:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('notificaciones', '0011_alter_notificacionrespaldo_dia'),
    ]

    operations = [
        migrations.AlterField(
            model_name='notificacionrespaldo',
            name='dia',
            field=models.IntegerField(blank=True, choices=[(0, 'LUNES'), (1, 'MARTES'), (2, 'MIÉRCOLES'), (3, 'JUEVES'), (4, 'VIERNES'), (5, 'SÁBADO'), (6, 'DOMINGO')], default=0),
        ),
    ]