import json
from datetime import datetime
from typing import Any
from typing import Dict

from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView


class HomeTemplateView(LoginRequiredMixin, TemplateView):
    """
    View for loading `Home` page.
    """
    template_name = 'dashboards/home.html'
