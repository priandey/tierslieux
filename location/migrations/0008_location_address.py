# Generated by Django 2.2.7 on 2020-05-30 12:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('location', '0007_location_catchphrase'),
    ]

    operations = [
        migrations.AddField(
            model_name='location',
            name='address',
            field=models.CharField(max_length=255, null=True),
        ),
    ]
