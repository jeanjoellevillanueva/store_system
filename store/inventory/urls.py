from django.urls import path

from .views import ProductDatatableTemplateView


app_name = 'inventory'


urlpatterns = [
     path(
        'products/',
        ProductDatatableTemplateView.as_view(),
        name='list_products'
    ),
]
