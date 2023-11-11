from django.conf import settings


def project_info_context(request):
    context = {
        'DATATABLES_LENGTH': settings.DATATABLES_LENGTH,
        'FAVICON_LINK': settings.FAVICON_LINK,
        'LOGO_LINK': settings.LOGO_LINK,
        'LOGIN_IMAGE_LINK': settings.LOGIN_IMAGE_LINK,
        'PROJECT_NAME': settings.PROJECT_NAME,
    }
    return context
