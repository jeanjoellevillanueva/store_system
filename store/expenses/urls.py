from django.urls import path

from .views import ExpenseTemplateView


app_name = 'expenses'


urlpatterns = [
    path(
        '',
        ExpenseTemplateView.as_view(),
        name='home'
    ),
]
