from django.urls import path

from .views import DeliveryCustomCreateView
from .views import InventoryTemplateView
from .views import ProductCustomCreateView
from .views import ProductCustomUpdateView
from .views import ProductListDatatableTemplateView
from .views import ProductTemplateView
from .views import VariationCustomCreateView
from .views import VariationCustomDeleteView
from .views import VariationCustomUpdateView
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
        'products/update/',
        ProductCustomUpdateView.as_view(),
        name='update_product'
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
    path(
        'products/<str:item_code>/variations/create/',
        VariationCustomCreateView.as_view(),
        name='create_variation'
    ),
    path(
        'products/<str:item_code>/variations/update/<str:id>/',
        VariationCustomUpdateView.as_view(),
        name='update_variation'
    ),
    path(
        'products/<str:item_code>/variations/delete/<str:id>/',
        VariationCustomDeleteView.as_view(),
        name='delete_variation'
    ),
    path(
        'delivery/<str:product_id>/',
        DeliveryCustomCreateView.as_view(),
        name='add_delivery'
    ),
]
