# Generated by Django 2.2.7 on 2020-01-23 07:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('location', '0003_auto_20200123_0822'),
    ]

    operations = [
        migrations.AlterField(
            model_name='location',
            name='localities',
            field=models.ManyToManyField(related_name='locations', to='location.Locality'),
        ),
    ]
