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
            .values_list('employee__username', 'task', 'time_in', 'time_out', 'id')
    )
    overtimes = (
        Overtime.objects
            .filter(**filters)
            .order_by('id')
            .values_list('employee__username', 'task', 'date', 'hours', 'id')
    )
    manila_tz = pytz.timezone('Asia/Manila')
    attendance_data = [
        {
            'title': f'{employee}',
            'start': time_in.strftime('%Y-%m-%d') if time_in else 'N/A',
            'color': settings.SUCCESS_COLOR,
            'extendedProps': {
                'id': primary_key,
                'person': f'{employee}',
                'subtitle': 'Regular',
                'task': f'{Attendance.get_task_display(task)}',
                'task_value': task,
                'time': f'{time_in.astimezone(manila_tz).strftime("%I:%M:%S %p") if time_in else "N/A"} - '
                    f'{time_out.astimezone(manila_tz).strftime("%I:%M:%S %p") if time_out else "N/A"}',
            }
        }
        for employee, task, time_in, time_out, primary_key in attendances
    ]
    overtime_data = [
        {
            'title': f'{employee} - {hours} hr(s)',
            'start': date.astimezone(manila_tz).strftime('%Y-%m-%d'),
            'color': settings.INFO_COLOR,
            'extendedProps': {
                'id': primary_key,
                'person': f'{employee}',
                'subtitle': 'Overtime',
                'task': f'{Attendance.get_task_display(task)}',
                'task_value': task,
                'time': f'{hours} hr(s)',
            }
        }
        for employee, task, date, hours, primary_key in overtimes
    ]
    return attendance_data + overtime_data
