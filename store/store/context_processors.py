from django.conf import settings


def project_info_context(request):
    context = {
        'PROJECT_NAME': settings.PROJECT_NAME,
        'FAVICON_LINK': settings.FAVICON_LINK,
        'LOGO_LINK': settings.LOGO_LINK,
        'LOGIN_IMAGE_LINK': settings.LOGIN_IMAGE_LINK,
    }
    return context
