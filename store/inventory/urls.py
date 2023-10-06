from django.urls import path

from .views import InventoryTemplateView
from .views import ProductCustomCreateView
from .views import ProductListDatatableTemplateView
from .views import ProductTemplateView
from .views import VariationListDatatableTemplateView

app_name = 'inventory'


urlpatterns = [
    path(
        '',
        InventoryTemplateView.as_view(),
        name='home'
    ),
    path(
        'products/list/',
        ProductListDatatableTemplateView.as_view(),
        name='list_product'
    ),
    path(
        'products/create/',
        ProductCustomCreateView.as_view(),
        name='create_product'
    ),
    path(
        'products/<str:item_code>/',
        ProductTemplateView.as_view(),
        name='product'
    ),
    path(
        'products/<str:item_code>/variations/',
        VariationListDatatableTemplateView.as_view(),
        name='list_variation'
    ),
]
