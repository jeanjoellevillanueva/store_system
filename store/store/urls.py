from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path, reverse
from django.shortcuts import redirect
from django.views import View

from urllib.parse import urlencode

class AdminLoginRedirectView(View):
    """Require staff to use the public OTP flow before opening Django admin."""

    def dispatch(self, request, *args, **kwargs):
        next_url = request.GET.get('next')

        if next_url:
            login_url = reverse('accounts:login')
            return redirect(f'{login_url}?{urlencode({"next": next_url})}')

        return redirect('accounts:login')


urlpatterns = [
    path('', include('pos.urls')),
    path('accounts/', include('accounts.urls')),
    path('attendance/', include('attendance.urls')),
    path('admin/login/', AdminLoginRedirectView.as_view()),
    path('admin/', admin.site.urls),
    path('calendar/', include('calendars.urls')),
    path('dashboard/', include('dashboards.urls')),
    path('expenses/', include('expenses.urls')),
    path('inventory/', include('inventory.urls')),
    path('payslip/', include('payslips.urls')),
]

urlpatterns + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
