from django.contrib.auth.models import AbstractUser
from django.db import models


# Create your models here.

class Officer(AbstractUser):
    office_latitude = models.FloatField(blank=True, null=True)
    office_longitude = models.FloatField(blank=True, null=True)
    office_time_entry = models.TimeField(auto_now=False, auto_now_add=False, blank=True, null=True)
    total_attendance = models.PositiveIntegerField(default=0)
    phone = models.CharField(max_length=10, null=True)


class Absence(models.Model):
    absence_date = models.DateField(blank=True)
    officer = models.ForeignKey(Officer,related_name='absent', on_delete=models.CASCADE)
