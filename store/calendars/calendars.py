import pytz

from django.conf import settings

from attendance.models import Attendance
from attendance.models import Overtime


def get_calendar_data(filters):
    """
    Returns the data ready to use for a calendar.
    """
    attendances = (
        Attendance.objects
            .filter(**filters)
            .order_by('id')
            .values_list('employee__username', 'task', 'time_in', 'time_out')
    )
    overtimes = (
        Overtime.objects
            .filter(**filters)
            .order_by('id')
            .values_list('employee__username', 'task', 'date', 'hours')
    )
    manila_tz = pytz.timezone('Asia/Manila')
    attendance_data = [
        {
            'title': f'{employee}',
            'start': time_in.strftime('%Y-%m-%d') if time_in else 'N/A',
            'color': settings.SUCCESS_COLOR,
            'extendedProps': {
                'person': f'{employee}',
                'subtitle': 'Regular',
                'task': f'{Attendance.get_task_display(task)}',
                'time': f'{time_in.astimezone(manila_tz).strftime("%I:%M:%S %p") if time_in else "N/A"} - '
                    f'{time_out.astimezone(manila_tz).strftime("%I:%M:%S %p") if time_out else "N/A"}',
            }
        }
        for employee, task, time_in, time_out in attendances
    ]
    overtime_data = [
        {
            'title': f'{employee} - {hours} hr(s)',
            'start': date.astimezone(manila_tz).strftime('%Y-%m-%d'),
            'color': settings.INFO_COLOR,
            'extendedProps': {
                'person': f'{employee}',
                'subtitle': 'Overtime',
                'task': f'{Attendance.get_task_display(task)}',
                'time': f'{hours} hr(s)',
            }
        }
        for employee, task, date, hours in overtimes
    ]
    return attendance_data + overtime_data
