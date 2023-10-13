from django.urls import path

from .views import ExpensesTemplateView


app_name = 'expenses'


urlpatterns = [
    path(
        '',
        ExpensesTemplateView.as_view(),
        name='home'
    ),
]
