import json
from typing import Any

from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView


class CalendarTemplateView(LoginRequiredMixin, TemplateView):
    """
    Renders the home page for calendar.
    """
    template_name = 'calendars/home.html'


class CalendarComponentTemplateView(LoginRequiredMixin, TemplateView):
    """
    Loads the calendar component.
    """
    template_name = 'calendars/component/calendar.html'

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        calendar_data = [
            {'title': 'Event 1', 'start': '2024-09-21'},
            {'title': 'Event 1', 'start': '2024-09-21'},
            {'title': 'Event 1', 'start': '2024-09-21'},
            {'title': 'Event 1', 'start': '2024-09-21'},
            {'title': 'Event 1', 'start': '2024-09-21'},
            {'title': 'Event 1', 'start': '2024-09-21'},
            {'title': 'Event 3', 'start': '2024-09-21'},
            {'title': 'Event 1', 'start': '2024-09-21'},
            {'title': 'Event 2', 'start': '2024-09-22'},
        ]
        context['calendar_data'] = json.dumps(calendar_data)
        return context
