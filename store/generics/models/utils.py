from django.core.exceptions import ObjectDoesNotExist


def get_or_none(model, **kwargs):
    """
    Fetch an object from the database, returning `None` if no matching record is found.
    """
    try:
        return model.objects.get(**kwargs)
    except ObjectDoesNotExist:
        return None
