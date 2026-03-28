from django import template
from django.conf import settings
from decimal import Decimal, ROUND_HALF_UP

register = template.Library()

TAUX_TAXES = Decimal(str(getattr(settings, 'TAUX_TAXES_TOTAL', 14.975)))
TAUX_TPS = Decimal(str(getattr(settings, 'TAUX_TPS', 5.0)))
TAUX_TVQ = Decimal(str(getattr(settings, 'TAUX_TVQ', 9.975)))


def _format(val):
    """Formate: entier si .00, sinon 2 décimales."""
    val = val.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
    if val == val.to_integral_value():
        return f'{int(val)}'
    return f'{val}'


@register.filter
def prix(value):
    """Formate un prix HT avec $."""
    if value is None:
        return '-'
    try:
        return f'${_format(Decimal(str(value)))}'
    except Exception:
        return f'${value}'


@register.filter
def prix_ttc(value):
    """Prix TTC (HT + TPS + TVQ)."""
    if value is None:
        return '-'
    try:
        ht = Decimal(str(value))
        ttc = ht * (1 + TAUX_TAXES / 100)
        return f'${_format(ttc)}'
    except Exception:
        return f'${value}'


@register.filter
def montant_tps(value):
    """Montant TPS."""
    if value is None:
        return '-'
    try:
        return f'${_format(Decimal(str(value)) * TAUX_TPS / 100)}'
    except Exception:
        return '-'


@register.filter
def montant_tvq(value):
    """Montant TVQ."""
    if value is None:
        return '-'
    try:
        return f'${_format(Decimal(str(value)) * TAUX_TVQ / 100)}'
    except Exception:
        return '-'


@register.filter
def nombre(value):
    """Formate un nombre: enlève .00, garde les décimales si utiles."""
    if value is None:
        return '-'
    try:
        val = Decimal(str(value)).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        if val == val.to_integral_value():
            return f'{int(val)}'
        # Enlever le trailing zero: 1.50 -> 1.5
        return f'{val.normalize()}'
    except Exception:
        return f'{value}'


@register.filter
def prix_nu(value):
    """Prix sans $."""
    if value is None:
        return '-'
    try:
        return _format(Decimal(str(value)))
    except Exception:
        return f'{value}'
