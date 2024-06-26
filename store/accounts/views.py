from django.conf import settings
from django.contrib.auth import login
from django.contrib.auth import logout
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import FormView

from .forms import LoginForm


class LoginView(FormView):
    """
    View used for logging in.
    """

    template_name = 'login.html'
    form_class = LoginForm
    success_url = reverse_lazy(settings.LOGIN_REDIRECT_URL)

    def form_valid(self, form):
        user = form.get_user()
        login(self.request, user)
        if not self.request.user.is_staff:
            self.success_url = reverse_lazy('pos:home')
        return super().form_valid(form)


def logout_view(request):
    """
    View used for logging out the user.
    """
    logout(request)
    return redirect(reverse_lazy('accounts:login'))
