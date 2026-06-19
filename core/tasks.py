import logging
from django.core.mail import EmailMultiAlternatives
from huey.contrib.djhuey import task
from django.template.loader import render_to_string
from django.conf import settings
from core.models import MentorshipApplication

logger = logging.getLogger(__name__)



@task()
def send_decision_email_task(application_id: int, decision: str) -> bool:
    """
    Sends a customized acceptance or rejection email to a mentorship applicant.
    
    """
    if decision not in ['accepted', 'rejected']:
        logger.error(f"Invalid decision type '{decision}' for application {application_id}.")
        return False

    try:
        app = MentorshipApplication.objects.get(id=application_id)
    except MentorshipApplication.DoesNotExist:
        logger.error(f"MentorshipApplication with id {application_id} not found.")
        return False

    subject = "Update on your Mentorship Application - Zero to Hero"
    if decision == "accepted":
        subject = "Congratulations! You've been accepted to the Zero to Hero Mentorship"

    from_email = settings.DEFAULT_FROM_EMAIL
    to_email = [app.email]
    context = {'full_name': app.full_name}

    try:
        text_content = render_to_string(f"emails/{decision}_email.txt", context)
        html_content = render_to_string(f"emails/{decision}_email.html", context)

        msg = EmailMultiAlternatives(subject, text_content, from_email, to_email)
        msg.attach_alternative(html_content, "text/html")

        # 2024 Spam Compliance: Native Unsubscribe Header
        msg.extra_headers['List-Unsubscribe'] = f"<mailto:{from_email}?subject=unsubscribe>"
        
        # Dispatch to background thread instead of a heavy worker queue
        msg.send()
        
        logger.info(f"{decision.capitalize()} email queued in local thread for {app.email}.")
        return True

    except Exception as e:
        logger.error(f"Failed to prepare {decision} email for {app.email}. Error: {str(e)}")
        return False
