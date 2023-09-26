from django.urls import path

from .views import InventoryTemplateView


app_name = 'inventory'


urlpatterns = [
     path(
        'products/',
        InventoryTemplateView.as_view(),
        name='products'
    ),
]
