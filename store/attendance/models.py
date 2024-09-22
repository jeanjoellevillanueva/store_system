from django.contrib.auth.models import User
from django.db import models


class Attendance(models.Model):
    class Meta:
        db_table = 'ATTENDANCE'

    TASK_PICK = 'pick'
    TASK_PACK = 'pack'
    TASK_DELIVER = 'deliver'
    TASK_LIVE = 'live'
    TASK_BAZAAR = 'bazaar'
    TASK_DEVELOP = 'dev'
    TASK_ACCOUNTING = 'accounting'

    TASK_CHOICES = (
        (TASK_PICK, 'Pick'),
        (TASK_PACK, 'Pack'),
        (TASK_DELIVER, 'Deliver'),
        (TASK_BAZAAR, 'Bazaar'),
        (TASK_DEVELOP, 'Coding'),
        (TASK_ACCOUNTING, 'Accounting'),
    )

    employee = models.ForeignKey(User, on_delete=models.CASCADE)
    task = models.CharField(max_length=50, choices=TASK_CHOICES)
    time_in = models.DateTimeField(auto_now_add=True)
    time_out = models.DateTimeField(null=True, blank=True)
