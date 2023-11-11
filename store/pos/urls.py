from django.urls import path

from .views import POSCheckOutTemplateView
from .views import POSProductListTemplateView
from .views import POSTemplateView
from .views import SaleVoidJSONView
from .views import ProductSoldListTemplateView
from .views import ProductSoldTemplateView
from .views import RecentlySoldTemplateView
from .views import SaleCustomCreateView
from .views import SaleReportTemplateView


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
    path(
        'sales/',
        SaleReportTemplateView.as_view(),
        name='sale'
    ),
    path(
        'sales/<str:receipt_number>/',
        ProductSoldTemplateView.as_view(),
        name='sold'
    ),
    path(
        'sales/<str:receipt_number>/products/',
        ProductSoldListTemplateView.as_view(),
        name='list_sold'
    ),
    path(
        'sales/void/<str:id>/',
        SaleVoidJSONView.as_view(),
        name='void'
    ),
    path(
        'sales/recent',
        RecentlySoldTemplateView.as_view(),
        name='recent'
    ),
]
