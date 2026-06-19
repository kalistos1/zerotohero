import logging
import secrets

from django.core.mail import EmailMessage
from django.template.loader import render_to_string

logger = logging.getLogger(__name__)


def send_email(receiver, subject, template_name, context, sender):
    msg_html = render_to_string(template_name, context)
    msg = EmailMessage(subject=subject, body=msg_html, from_email=sender, to=receiver)
    msg.content_subtype = "html"
    return msg.send()


def get_hash():
    # token_urlsafe(32) produces 43 URL-safe characters from os.urandom — 256 bits of entropy.
    return secrets.token_urlsafe(32)
