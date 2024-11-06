from django.urls import path

from .views import ExpenseCustomCreateView
from .views import ExpenseCustomDeleteView
from .views import ExpenseCustomUpdateView
from .views import ExpenseListDatatableTemplateView
from .views import ExpenseListDownloadView
from .views import ExpenseTemplateView


app_name = 'expenses'


urlpatterns = [
    path(
        '',
        ExpenseTemplateView.as_view(),
        name='home'
    ),
    path(
        'list/',
        ExpenseListDatatableTemplateView.as_view(),
        name='list_expense'
    ),
    path(
        'create/',
        ExpenseCustomCreateView.as_view(),
        name='create_expense'
    ),
    path(
        'update/<int:id>',
        ExpenseCustomUpdateView.as_view(),
        name='update_expense'
    ),
    path(
        'delete/<int:id>',
        ExpenseCustomDeleteView.as_view(),
        name='delete_expense'
    ),
    path(
        'download/',
        ExpenseListDownloadView.as_view(),
        name='download_expense'
    ),
]
