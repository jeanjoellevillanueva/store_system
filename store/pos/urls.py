from django.urls import path

from .views import POSTemplateView


app_name = 'pos'


urlpatterns = [
    path(
        '',
        POSTemplateView.as_view(),
        name='home'
    ),
]
