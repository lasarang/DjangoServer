# Generated by Django 3.2.5 on 2022-08-03 00:11

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='NotificacionRespaldo',
            fields=[
                ('id', models.BigAutoField(primary_key=True, serialize=False)),
                ('user_tag', models.CharField(max_length=200)),
                ('titulo', models.CharField(max_length=2000)),
                ('cuerpo', models.CharField(max_length=2000)),
                ('fue_revisada', models.CharField(max_length=1)),
            ],
        ),
    ]
