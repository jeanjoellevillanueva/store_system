from django.contrib.auth.models import User
from django.db import models


class Attendance(models.Model):
    class Meta:
        db_table = 'ATTENDANCE'
    
    TASK_PICK = 'pick'
    TASK_PACK = 'pack'
    TASK_DELIVER = 'deliver'
    
    TASK_CHOICES = (
        (TASK_PICK, 'Pick'),
        (TASK_PACK, 'Pack'),
        (TASK_DELIVER, 'Deliver'),
    )

    employee = models.ForeignKey(User, on_delete=models.CASCADE)
    task = models.CharField(max_length=255, default='', choices=TASK_CHOICES)
    time_in = models.DateTimeField(auto_now_add=True)
    time_out = models.DateTimeField(null=True, blank=True)




