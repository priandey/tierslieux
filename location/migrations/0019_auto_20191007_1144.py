# Generated by Django 2.2.5 on 2019-10-07 09:44

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('location', '0018_volunteeringrequest_validated'),
    ]

    operations = [
        migrations.AlterField(
            model_name='location',
            name='moderator',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='location', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='location',
            name='volunteers',
            field=models.ManyToManyField(related_name='volunteers', through='location.VolunteerBase', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='status',
            name='volunteer',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='opened', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='volunteerbase',
            name='volunteer',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
    ]