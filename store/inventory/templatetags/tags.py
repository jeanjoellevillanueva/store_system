from django import template

from ..models import Delivery


register = template.Library()


@register.filter(name='reason_display')
def reason_display(reason):
    """
    Returns the proper display of delivery reason.
    """
    deliver_dict = {}
    choices = Delivery.DELIVER_CHOICES
    for choice in choices:
        deliver_dict[choice[0]] = choice[1]
    return deliver_dict.get(reason)
