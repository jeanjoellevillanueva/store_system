from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include
from django.urls import path


urlpatterns = [
    path('', include('dashboards.urls')),
    path('accounts/', include('accounts.urls')),
    path('admin/', admin.site.urls),
    path('inventory/', include('inventory.urls')),
]

urlpatterns + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
