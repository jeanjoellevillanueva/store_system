from django.contrib.auth.models import User
from django.db import models


class Attendance(models.Model):
    class Meta:
        db_table = 'ATTENDANCE'
    employee = models.OneToOneField(User, on_delete=models.CASCADE)
    task = models.CharField(max_length=255)
    time_in = models.DateTimeField(auto_now_add=True)
    time_out = models.DateTimeField(null=True, blank=True)




