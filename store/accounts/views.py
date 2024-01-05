from django.conf import settings
from django.contrib.auth import login
from django.contrib.auth import logout
from django.contrib.auth.views import LoginView as AuthLoginView
from django.shortcuts import redirect
from django.urls import reverse_lazy

from .forms import LoginForm


class LoginView(AuthLoginView):
    """
    View used for logging in.
    """

    template_name = 'login.html'
    form_class = LoginForm
    success_url = reverse_lazy(settings.LOGIN_REDIRECT_URL)

    def form_valid(self, form):
        user = form.get_user()
        login(self.request, user)
        return super().form_valid(form)
    
    def get_success_url(self):
        """
        Return the URL to redirect to after processing a valid form.
        """
        if not (self.request.user.is_staff or self.request.user.is_superuser):
            self.success_url = reverse_lazy('pos:home')
        return str(self.success_url)


def logout_view(request):
    """
    View used for logging out the user.
    """
    logout(request)
    return redirect(reverse_lazy('accounts:login'))
