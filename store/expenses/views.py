from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import transaction
from django.http import Http404
from django.views import View
from django.views.generic import TemplateView


class ExpensesTemplateView(LoginRequiredMixin, TemplateView):
    """
    Dashboard for expenses.
    """
    template_name = 'expenses/home.html'

    def get_context_data(self, **kwargs) -> dict:
        context = super().get_context_data(**kwargs)
        return context
