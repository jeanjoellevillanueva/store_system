from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import View
from django.views.generic import TemplateView

from .models import Product


class ProductDatatableTemplateView(LoginRequiredMixin, TemplateView):
    """
    View that will load the products in a datatable format.
    """

    template_name = 'expenses/datatables/table_expense.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        products = Product.objects.all()
        context['products'] = products
        return context
