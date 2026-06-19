import logging

import requests
from django.conf import settings

logger = logging.getLogger(__name__)


def verify_recaptcha(token, remote_ip=None):
    """Verify a Google reCAPTCHA v2 ("I am not a robot") token.

     """
    secret_key = getattr(settings, 'RECAPTCHA_SECRET_KEY', '')
    if not secret_key:
        logger.warning(
            'reCAPTCHA check called but RECAPTCHA_SECRET_KEY is not configured. '
        )
        return False

    if not token:
        logger.warning('reCAPTCHA: empty token received — user did not complete the challenge.')
        return False

    data = {'secret': secret_key, 'response': token}
    if remote_ip:
        data['remoteip'] = remote_ip

    try:
        response = requests.post(
            'https://www.google.com/recaptcha/api/siteverify',
            data=data,
            timeout=5,
        )
        response.raise_for_status()
    except requests.HTTPError as e:
        logger.error('reCAPTCHA: HTTP error %s — %s', e.response.status_code, e)
        return False
    except requests.RequestException as e:
        logger.error('reCAPTCHA: request failed — %s', e)
        return False

    try:
        result = response.json()
    except ValueError as e:
        # Google returned 200 OK but with non-JSON body (e.g. maintenance page).
        logger.error('reCAPTCHA: could not parse JSON response — %s', e)
        return False

    logger.debug('reCAPTCHA siteverify response: %s', result)

    if result.get('success', False):
        return True

    error_codes = result.get('error-codes', [])
    logger.error('reCAPTCHA failed — error codes: %s', error_codes)
    return False
