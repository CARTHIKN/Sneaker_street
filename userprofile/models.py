from typing import Self
from django.db import models
from userside.models import UserProfile
# Create your models here.
from django.db import models
from userside.models import UserProfile

class Userdetails(models.Model):

    userprofile =  models.OneToOneField(UserProfile, on_delete=models.CASCADE)
    fullname = models.CharField(max_length=25, blank=True,default="")
    date_of_birth = models.DateField(blank=True, null=True)
    profile_image = models.ImageField(upload_to="photos/profile", blank=True, null=True,)