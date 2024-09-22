from django.contrib.auth.models import User
from django.db import models


class Attendance(models.Model):
    """
    Stores the attendance of employees.
    """
    class Meta:
        db_table = 'ATTENDANCE'

    TASK_PICK = 'pick'
    TASK_PACK = 'pack'
    TASK_DELIVER = 'deliver'
    TASK_LIVE = 'live'
    TASK_BAZAAR = 'bazaar'
    TASK_DEVELOP = 'dev'
    TASK_ACCOUNTING = 'accounting'
    TASK_ENCODER = 'encoding'
    TASK_CSR = 'csr'
    TASK_SORTING = 'sorting'

    TASK_CHOICES = (
        (TASK_PICK, 'Pick'),
        (TASK_PACK, 'Pack'),
        (TASK_DELIVER, 'Deliver'),
        (TASK_LIVE, 'Live Selling'),
        (TASK_BAZAAR, 'Bazaar'),
        (TASK_DEVELOP, 'Developer'),
        (TASK_ACCOUNTING, 'Accounting'),
        (TASK_ENCODER, 'Encoding'),
        (TASK_CSR, 'Customer Service'),
        (TASK_SORTING, 'Sorting'),
    )

    employee = models.ForeignKey(User, on_delete=models.CASCADE)
    task = models.TextField(max_length=500)
    time_in = models.DateTimeField(auto_now_add=True)
    time_out = models.DateTimeField(null=True, blank=True)

    @classmethod
    def get_task_display(cls, task_string):
        task_list = task_string.split(',')
        task_display = [dict(cls.TASK_CHOICES).get(task, task) for task in task_list]
        return '/'.join(task_display)
