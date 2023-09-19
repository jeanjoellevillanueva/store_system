from django.contrib.auth.models import User
from django.db import models


class ModelMixin(models.Model):
    """
    A mixin class that adds `created_by` and `updated_by` fields to a model.
    """

    created_by = models.ForeignKey(
        User, on_delete=models.SET_NULL,
        related_name='%(class)s_created',
        null=True, blank=True
    )
    updated_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        related_name='%(class)s_updated',
        null=True,
        blank=True
    )
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True
