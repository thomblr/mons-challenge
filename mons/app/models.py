from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class UserSettings(models.Model):
    user = models.OneToOneField(User, primary_key=True, on_delete=models.CASCADE)
    home = models.CharField(max_length=255)
    category = models.CharField(max_length=255)
    langue = models.CharField(max_length=255)


class SaveTripPoints(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    trajet = models.CharField(max_length=100)
    date = models.DateTimeField(auto_now_add=True)
    pts = models.IntegerField()