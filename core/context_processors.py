from django.conf import settings
from django.core.cache import cache
from core.seo import _safe_base_url

from .models import SiteSettings

_SITE_SETTINGS_CACHE_KEY = 'site_settings'
_SITE_SETTINGS_CACHE_TTL = 3600  # 1 hour


def site_settings(request):
    obj = cache.get(_SITE_SETTINGS_CACHE_KEY)
    if obj is None:
        obj = SiteSettings.objects.first()
        obj_dict = {'site_name': obj.site_name} if obj else {}
        cache.set(_SITE_SETTINGS_CACHE_KEY, obj_dict, timeout=_SITE_SETTINGS_CACHE_TTL)
    return {'site_settings': obj if isinstance(obj, dict) else {'site_name': getattr(obj, 'site_name', '')}}


def recaptcha(request):
    site_key = getattr(settings, 'RECAPTCHA_SITE_KEY', '')
    return {
        'RECAPTCHA_SITE_KEY': site_key,
        'RECAPTCHA_ENABLED': bool(site_key and getattr(settings, 'RECAPTCHA_SECRET_KEY', '')),
        # Injected so {% if not debug %} in templates works correctly.
        # Without this, 'debug' is undefined in templates (renders as ''),
        # causing the reCAPTCHA widget to always render, even in DEBUG mode.
        'debug': settings.DEBUG,
    }


def safe_base_url(request):
    """Provides a safe base URL for templates to prevent Host header injection."""
    return {
        'safe_base_url': _safe_base_url(request)
    }
