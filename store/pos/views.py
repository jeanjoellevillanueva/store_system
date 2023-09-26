from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView


class POSTemplateView(LoginRequiredMixin, TemplateView):
    """
    """
    template_name = 'pos/home.html'
