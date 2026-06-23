import logging

from django.conf import settings
from django.contrib import messages
from django.core.mail import EmailMessage
from django.db import IntegrityError
from django.shortcuts import redirect, render
from django.views.decorators.csrf import requires_csrf_token
from django_ratelimit.decorators import ratelimit

from .forms import ContactForm, MentorshipApplicationForm, SponsorshipInquiryForm, VolunteerApplicationForm
from .utils import verify_recaptcha
from .models import FAQ, AboutPage, Event, SiteSettings, SponsorshipTier, Testimonial, TeamMember
from blog.models import Post

logger = logging.getLogger(__name__)


def index(request, slug=None):
    team_members = TeamMember.objects.filter(is_active=True).order_by('created_at')[:4]
    testimonials = Testimonial.objects.filter(is_active=True).only(
        'name', 'role', 'image', 'rating', 'review_text', 'media_type', 'chat_screenshot', 'video_file'
    ).order_by('-created_at')[:4]
    latest_posts = Post.objects.filter(status="PUBLISHED").only(
        'title', 'slug', 'image', 'thumbnail', 'body', 'date_created'
    ).order_by('-date_created')[:4]
    
    context = {
        'team_members': team_members,
        'testimonials': testimonials,
        'latest_posts': latest_posts,
    }
    return render(request, 'pages/index.html', context)


def team(request, slug=None):
    team_members = TeamMember.objects.filter(is_active=True).order_by('created_at')

    context = {
        'team_members': team_members,
      
    }
    return render(request, 'pages/team.html', context)



def about_us(request):
    about = AboutPage.load()
    testimonials_qs = (
        Testimonial.objects
        .filter(is_active=True)
        .only('name', 'role', 'image', 'rating', 'review_text',
              'media_type', 'chat_screenshot', 'video_file')
        .order_by('-created_at')[:6]
    )
    team_members = TeamMember.objects.filter(is_active=True).order_by('created_at')
    return render(request, 'pages/about.html', {
        'about': about,
        'testimonials': testimonials_qs,
        'team_members': team_members,
    })


def events(request):
    events_qs = (
        Event.objects
        .filter(is_active=True)
        .exclude(status=Event.STATUS_CANCELLED)
        .only('title', 'image', 'venue', 'start_datetime',
              'end_datetime', 'description', 'is_free', 'entry_fee', 'status')
        .order_by('start_datetime')
    )
    return render(request, 'pages/events.html', {'events': events_qs})


def testimonials(request):
    testimonials_qs = (
        Testimonial.objects
        .filter(is_active=True)
        .only('name', 'role', 'image', 'rating', 'review_text',
              'media_type', 'chat_screenshot', 'video_file')
        .order_by('-created_at')
    )
    return render(request, 'pages/testimonials.html', {'testimonials': testimonials_qs})


def faqs(request):
    faqs_qs = (
        FAQ.objects
        .filter(is_active=True)
        .only('question', 'answer')
        .order_by('created_at')
    )
    return render(request, 'pages/faq.html', {'faqs': faqs_qs})


@ratelimit(key='ip', rate='5/m', method='POST', block=True)
def contact_us(request):
    if request.method == "POST":
        contact_form = ContactForm(request.POST)
        is_valid = contact_form.is_valid()

        ip = request.META.get('REMOTE_ADDR', '') or ''
        recaptcha_token = request.POST.get('g-recaptcha-response', '')
        if not settings.DEBUG and not verify_recaptcha(recaptcha_token, ip):
            contact_form.add_error(None, 'reCAPTCHA verification failed. Please try again.')
            is_valid = False

        if is_valid:
            cd = contact_form.cleaned_data

            site_obj = SiteSettings.objects.first()
            recipient_email = (
                site_obj.support_email
                if site_obj and site_obj.support_email
                else getattr(settings, 'DEFAULT_FROM_EMAIL', None)
            )

            email_sent = True
            if recipient_email:
                try:
                    msg = EmailMessage(
                        subject=cd['subject'],
                        body=cd['message'],
                        from_email=getattr(settings, 'DEFAULT_FROM_EMAIL', None),
                        to=[recipient_email],
                        reply_to=[cd['email']],
                    )
                    msg.send(fail_silently=False)
                except Exception:
                    logger.exception("Failed to send contact email to %s", recipient_email)
                    email_sent = False

            contact_form.save()
            if email_sent:
                messages.success(request, 'Message sent successfully!')
            else:
                messages.warning(request, 'Your message has been saved, but we experienced an issue sending the email notification. We will follow up with you.')
            return redirect('core:contact')
        else:
            messages.error(request, 'Please fix the errors below.')
    else:
        contact_form = ContactForm()

    return render(request, 'pages/contact.html', {'contact_form': contact_form})


def terms(request):
    return render(request, 'pages/terms-conditions.html')


def privacy_policy(request):
    return render(request, 'pages/privacy-policy.html')


@ratelimit(key='ip', rate='5/m', method='POST', block=True)
def application_form(request):
    if request.method == "POST":
        form = MentorshipApplicationForm(request.POST)
        is_valid = form.is_valid()

        ip = request.META.get('REMOTE_ADDR', '') or ''
        recaptcha_token = request.POST.get('g-recaptcha-response', '')
        if not settings.DEBUG and not verify_recaptcha(recaptcha_token, ip):
            form.add_error(None, 'reCAPTCHA verification failed. Please try again.')
            is_valid = False

        if is_valid:
            try:
                form.save()
            except IntegrityError:
                form.add_error('email', 'An application with this email address has already been submitted.')
                return render(request, 'application_form/index.html', {'form': form})
                
            request.session['application_submitted'] = True
            messages.success(request, 'Your application has been submitted successfully!')
            return redirect('core:application_thank_you')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = MentorshipApplicationForm()
        
    return render(request, 'application_form/index.html', {'form': form})


def application_thank_you(request):
    if not request.session.pop('application_submitted', False):
        return redirect('core:application_form')
        
    share_url = request.build_absolute_uri('/apply/')
    return render(request, 'application_form/thankyou.html', {'share_url': share_url})


# ── Error handlers ─────────────────────────────────────────────────────────────

def error_400(request, exception):
    return render(request, 'errors/400.html', {'status_code': 400}, status=400)


def error_403(request, exception):
    return render(request, 'errors/403.html', {'status_code': 403}, status=403)


def error_404(request, exception):
    return render(request, 'errors/404.html', {'status_code': 404}, status=404)


def error_500(request):
    return render(request, 'errors/500.html', {'status_code': 500}, status=500)


@requires_csrf_token
def csrf_failure(request, reason=""):
    is_login_failure = request.path.startswith(
        getattr(settings, 'LOGIN_URL', '/authentication/login/')
    )
    return render(request, 'errors/csrf_failure.html', {
        'reason': reason,
        'is_login_failure': is_login_failure,
    }, status=403)



def sponsorship_landing(request):
    tiers = SponsorshipTier.objects.all()
    return render(request, 'core/sponsorship_landing.html', {'tiers': tiers})


@ratelimit(key='ip', rate='5/m', method='POST', block=True)
def sponsorship_apply(request):
    initial_data = {}
    plan = request.GET.get('plan')
    if plan:
        initial_data['tier'] = plan

    if request.method == 'POST':
        form = SponsorshipInquiryForm(request.POST)
        is_valid = form.is_valid()

        ip = request.META.get('REMOTE_ADDR', '') or ''
        recaptcha_token = request.POST.get('g-recaptcha-response', '')
        if not settings.DEBUG and not verify_recaptcha(recaptcha_token, ip):
            form.add_error(None, 'reCAPTCHA verification failed. Please try again.')
            is_valid = False

        if is_valid:
            form.save()
            messages.success(request, "Sponsorship inquiry received. We will contact you shortly.")
            return redirect('core:sponsorship')
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = SponsorshipInquiryForm(initial=initial_data)
    
    return render(request, 'core/sponsorship.html', {'form': form})


@ratelimit(key='ip', rate='5/m', method='POST', block=True)
def volunteer_application_form(request):
    if request.method == "POST":
        form = VolunteerApplicationForm(request.POST, request.FILES)
        is_valid = form.is_valid()

        ip = request.META.get('REMOTE_ADDR', '') or ''
        recaptcha_token = request.POST.get('g-recaptcha-response', '')
        if not settings.DEBUG and not verify_recaptcha(recaptcha_token, ip):
            form.add_error(None, 'reCAPTCHA verification failed. Please try again.')
            is_valid = False

        if is_valid:
            try:
                form.save()
            except IntegrityError:
                form.add_error('email', 'An application with this email address has already been submitted.')
                return render(request, 'application_form/volunteer.html', {'form': form})
                
            request.session['volunteer_application_submitted'] = True
            messages.success(request, 'Your volunteer application has been submitted successfully!')
            return redirect('core:volunteer_application_thank_you')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = VolunteerApplicationForm()
        
    return render(request, 'application_form/volunteer.html', {'form': form})


def volunteer_application_thank_you(request):
    if not request.session.pop('volunteer_application_submitted', False):
        return redirect('core:volunteer_application_form')
        
    share_url = request.build_absolute_uri('/volunteer/apply/')
    return render(request, 'application_form/volunteer_thankyou.html', {'share_url': share_url})