from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView


class InventoryTemplateView(LoginRequiredMixin, TemplateView):
    """
    """
    template_name = 'inventory/home.html'