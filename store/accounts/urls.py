from django.urls import path

from .views import LoginView
from .views import logout_view

from .views import AccountComponentTemplateView
from .views import AccountCustomCreateView
from .views import AccountCustomDeleteView
from .views import AccountCustomUpdateView
from .views import AccountListDatatableTemplateView

app_name = 'accounts'

urlpatterns = [
    path(
        'login/',
        LoginView.as_view(),
        name='login'
    ),
    path(
        'logout/',
        logout_view,
        name='logout'
    ),
    path(
        '',
        AccountComponentTemplateView.as_view(),
        name='home'
    ),
    path(
        'accounts/list/',
        AccountListDatatableTemplateView.as_view(),
        name='list_account'
    ),
    path(
        'create/',
        AccountCustomCreateView.as_view(),
        name='create_account'
    ),
    path(
        'delete/<int:id>',
        AccountCustomDeleteView.as_view(),
        name='delete_account'
    ),
    path(
        'update/<int:id>',
        AccountCustomUpdateView.as_view(),
        name='update_account'
    ),
]
