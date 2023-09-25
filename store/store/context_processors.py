from django.conf import settings


def project_info_context(request):
    context = {
        'PROJECT_NAME': settings.PROJECT_NAME,
    }
    return context
