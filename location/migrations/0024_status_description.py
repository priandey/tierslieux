# Generated by Django 2.2.7 on 2019-11-11 11:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('location', '0023_auto_20191111_1220'),
    ]

    operations = [
        migrations.AddField(
            model_name='status',
            name='description',
            field=models.TextField(max_length=600, null=True),
        ),
    ]