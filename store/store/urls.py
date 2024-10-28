from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include
from django.urls import path


urlpatterns = [
    path('', include('pos.urls')),
    path('accounts/', include('accounts.urls')),
    path('attendance/', include('attendance.urls')),
    path('admin/', admin.site.urls),
    path('calendar/', include('calendars.urls')),
    path('dashboard/', include('dashboards.urls')),
    path('expenses/', include('expenses.urls')),
    path('inventory/', include('inventory.urls')),
    path('payslip/', include('payslips.urls')),
]

urlpatterns + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
