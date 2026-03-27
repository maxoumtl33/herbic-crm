from django import template
from decimal import Decimal

register = template.Library()


@register.filter
def prix(value):
    """Formate un prix: enlève les décimales si .00, sinon affiche 2 décimales."""
    if value is None:
        return '-'
    try:
        val = Decimal(str(value)).quantize(Decimal('0.01'))
        if val == val.to_integral_value():
            return f'${int(val)}'
        return f'${val}'
    except Exception:
        return f'${value}'


@register.filter
def prix_nu(value):
    """Même chose mais sans le $."""
    if value is None:
        return '-'
    try:
        val = Decimal(str(value)).quantize(Decimal('0.01'))
        if val == val.to_integral_value():
            return f'{int(val)}'
        return f'{val}'
    except Exception:
        return f'{value}'
