import requests

from django.db import models
from django.db.utils import IntegrityError
from django.utils import timezone
from django.utils.crypto import get_random_string
from django.utils.text import slugify
from django.contrib.auth.models import User

from .utils import address_to_coordinate, coordinate_to_address


class LocationManager(models.Manager):
    def create(self, *args, **kwargs):
        """
        Lookup upon an adress and parse result into localities and coordinates
        """
        slug = slugify(kwargs['name'])

        try:
            location = super(LocationManager, self).create(slug=slug, *args, **kwargs)
        except IntegrityError:
            slug = slugify(slug + '-' + get_random_string(length=6))
            location = super(LocationManager, self).create(slug=slug, *args, **kwargs)

        if 'address' in kwargs and not 'latitude' in kwargs and not 'longitude' in kwargs:
            coords = address_to_coordinate(kwargs['address'])
            location.latitude = coords[0]
            location.longitude = coords[1]
        elif 'latitude' in kwargs and 'longitude' in kwargs and not 'address' in kwargs:
            location.address = coordinate_to_address(kwargs['latitude'], kwargs['longitude'])
        else:
            pass
        location.save()
        return location


class Location(models.Model):
    """
    A location
    """
    objects = LocationManager()

    name = models.CharField(max_length=255)
    catchphrase = models.CharField(max_length=100)
    description = models.TextField()
    address = models.CharField(max_length=255, null=True)
    volunteers = models.ManyToManyField(User, through='VolunteerBase', related_name="volunteers")
    moderator = models.ForeignKey(User, on_delete=models.CASCADE, related_name="location_moderator")
    slug = models.SlugField(unique=True, blank=True)
    latitude = models.DecimalField(max_digits=18, decimal_places=15, null=True)
    longitude = models.DecimalField(max_digits=18, decimal_places=15, null=True)
    public = models.BooleanField(default=True)

    def __repr__(self):
        return self.name


class Status(models.Model):
    """
    Status represent an activity running in a location
    """
    activity = models.CharField(max_length=255)
    description = models.TextField(null=True)
    open_date = models.DateTimeField(auto_now_add=True)
    close_date = models.DateTimeField(null=True)
    volunteer = models.ForeignKey(User, related_name='opened', on_delete=models.SET_NULL, null=True)
    location = models.ForeignKey(Location, related_name='statuses', on_delete=models.CASCADE)

    def __repr__(self):
        return f'{self.activity} at {self.open_date}'

    def close(self):
        self.close_date = timezone.now()
        self.save()

    @property
    def is_opened(self):
        """
        :return: True if status is currently running, False otherwise
        """
        if not self.close_date:
            return True
        else:
            return False

    @property
    def open_time(self):
        """
        :return: Return a dict of data about time the status cover. If status
        is still running, return open time from open date until now.
        """
        if self.close_date:
            opened_time = self.close_date - self.open_date
        else:
            opened_time = timezone.now() - self.open_date

        opened_time_seconds = opened_time.total_seconds()
        ot_hours = int(opened_time_seconds // 3600)
        ot_rest = opened_time_seconds % 3600
        ot_minutes = int(ot_rest // 60)
        response = {
            'total_seconds': opened_time_seconds,
            'pretty'       : '{} hours, {} minutes'.format(ot_hours, ot_minutes)
        }
        return response



class VolunteeringRequest(models.Model):
    """
    VolunteeringRequest object represent a request of volunteership from one user to another

    - validated = If the two users (sender/receiver) agree on the volunteership,
    the request is considered validated.
    """
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name="request_sent")
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name="request_received")
    comment = models.CharField(max_length=255, null=True, default="Je souhaiterais être bénévole pour votre association")
    validated = models.BooleanField(null=True)
    date = models.DateTimeField(auto_now_add=True)

    @property
    def sender_is_mod(self):
        """
        :return: Return wheter sender user is moderator of the location or not
        """
        if self.volunteer_base.get().location.moderator == self.sender:
            return True
        else:
            return False

    def validate(self):
        self.validated = True
        self.save()
        activity = self.volunteer_base.get().is_active
        activity = True
        activity.save()


class VolunteerBase(models.Model):
    """
    VolunteerBase object represents a relation of volunteership between an user and a location.

    - is_active : The volunteership can be active or not (eg: user has not been validated yet,
    volunteership relation has ended, etc.)

    - volunteering_request : Every volunteership relation begin with a request from one user to another.
    """
    volunteer = models.ForeignKey(User, on_delete=models.CASCADE)
    location = models.ForeignKey(Location, on_delete=models.CASCADE)
    is_active = models.BooleanField(default=False)
    volunteering_request = models.ForeignKey(VolunteeringRequest, on_delete=models.CASCADE, related_name="volunteer_base")

    class Meta:
        unique_together = (("volunteer", "location"),)
