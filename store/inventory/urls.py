from django.urls import path

from .views import DeliveryCustomCreateView
from .views import DeliveryListTemplateView
from .views import DeliveryReportTemplateView
from .views import ExportToShipView
from .views import InventoryTemplateView
from .views import OutOfStockPrintView
from .views import OutOfStockTemplateView
from .views import ProductCustomCreateView
from .views import ProductCustomUpdateView
from .views import ProductListDatatableTemplateView
from .views import ProductTemplateView
from .views import ToShipTemplateView
from .views import UploadToShipView
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
        'delivery/',
        DeliveryReportTemplateView.as_view(),
        name='delivery'
    ),
    path(
        'delivery/list/',
        DeliveryListTemplateView.as_view(),
        name='list_delivery'
    ),
    path(
        'delivery/<str:product_id>/',
        DeliveryCustomCreateView.as_view(),
        name='add_delivery'
    ),
    path(
        'out-of-stock/',
        OutOfStockTemplateView.as_view(),
        name='out_of_stock'
    ),
    path(
        'to-ship/',
        ToShipTemplateView.as_view(),
        name='to_ship'
    ),
    path(
        'upload/to-ship/',
        UploadToShipView.as_view(),
        name='to_ship_upload'
    ),
    path(
        'export/to-ship/',
        ExportToShipView.as_view(),
        name='to_ship_export'
    ),
    path(
        'export/out-of-stock/',
        OutOfStockPrintView.as_view(),
        name='out_of_stock_export'
    ),
]
