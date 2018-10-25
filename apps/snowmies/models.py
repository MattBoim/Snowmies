from django.db import models

# Create your models here.
class User(models.Model):
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    email = models.CharField(max_length=255)
    password = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class Ride(models.Model):
    resort = models.CharField(max_length=255)
    time = models.DateTimeField()
    location = models.CharField(max_length=255)
    ride_with = models.CharField(max_length=255)
    experience_lvl = models.IntegerField()
    min_age = models.IntegerField()
    max_age = models.IntegerField()
    ride_type = models.CharField(max_length=255)
    more = models.TextField()
    user = models.ForeignKey(User, related_name="rides")