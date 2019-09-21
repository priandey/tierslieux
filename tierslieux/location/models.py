from django.db import models

from user.models import Volunteer, Moderator


class Location(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    volunteers = models.ForeignKey(Volunteer, related_name='location', on_delete=models.CASCADE, null=True)
    moderator = models.ForeignKey(Moderator, on_delete=models.CASCADE)

class Status(models.Model):
    activity = models.CharField(max_length=255, null=True)
    open_date = models.DateTimeField(auto_now_add=True)
    close_date = models.DateTimeField(null=True) #TODO : Add function to edit this field when closing location
    volunteer = models.ForeignKey(Volunteer, related_name='opened', on_delete=models.SET_NULL, null=True)
    location = models.ForeignKey(Location, related_name='status', on_delete=models.CASCADE)

    def __repr__(self):
        return f'{self.activity} at {self.open_date}'
