from django.urls import path

from .views import POSCheckOutTemplateView
from .views import POSProductListTemplateView
from .views import POSTemplateView
from .views import SaleCustomCreateView


app_name = 'pos'


urlpatterns = [
    path(
        '',
        POSTemplateView.as_view(),
        name='home'
    ),
    path(
        'products/',
        POSProductListTemplateView.as_view(),
        name='list_product'
    ),
    path(
        'checkout/',
        POSCheckOutTemplateView.as_view(),
        name='checkout'
    ),
    path(
        'sales/create/',
        SaleCustomCreateView.as_view(),
        name='create_sale'
    ),
]
