# Generated by Django 3.1.3 on 2021-07-15 15:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0002_usuario_cultivos'),
    ]

    operations = [
        migrations.AlterField(
            model_name='usuario',
            name='bucket_name',
            field=models.CharField(max_length=200, unique=True),
        ),
    ]
