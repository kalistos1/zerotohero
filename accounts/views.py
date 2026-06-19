import logging
from datetime import timedelta

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import authenticate, get_user_model, logout
from django.contrib.auth import login as auth_login
from django.contrib.auth import views as auth_views
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone
from django.views.decorators.http import require_POST
from django_ratelimit.decorators import ratelimit

from core.utils import verify_recaptcha

from .forms import CompleteProfileForm, LoginForm, SignUpForm
from .models import Profile, TempUrl
from .utils import get_hash, send_email

logger = logging.getLogger(__name__)
User = get_user_model()


def mentee_signup(request):
    template = 'pages/signup.html'

    if request.method == 'POST':
        form = SignUpForm(request.POST)

        ip = request.META.get('REMOTE_ADDR', '') or ''
        recaptcha_token = request.POST.get('g-recaptcha-response', '')
        if not settings.DEBUG and not verify_recaptcha(recaptcha_token, ip):
            messages.error(request, 'reCAPTCHA verification failed. Please try again.')
            return render(request, template, {'form': form})

        if form.is_valid():
            cd = form.cleaned_data
            try:
                user = User.objects.create_user(
                    username=cd['username'],
                    email=cd['email'],
                    password=cd['password'],
                    first_name=cd['first_name'],
                    last_name=cd['last_name'],
                    accepted_terms=cd['accepted_terms'],
                )

                link_hash = get_hash()
                expiry_date = timezone.now() + timedelta(hours=24)
                TempUrl.objects.create(url_hash=link_hash, user=user, expires=expiry_date)

                context = {
                    'name': f"{cd['first_name']} {cd['last_name']}",
                    'username': user.username,
                    'email': user.email,
                    'hash': link_hash,
                }
                send_email(
                    [user.email],
                    'Verify your Zero to Hero account',
                    'emails/new_signup_email.html',
                    context,
                    'Zero to Hero <no-reply@zerotohero.com>',
                )
                return render(request, 'pages/registration-successful.html', context)

            except IntegrityError:
                # Race condition safety net — the form validators catch duplicates
                # but two concurrent requests can still slip through.
                messages.error(request, 'An account with that username or email already exists.')
                return render(request, template, {'form': form})
            except Exception as e:
                logger.exception('Error during signup', exc_info=e)
                messages.error(request, 'An unexpected error occurred. Please try again later.')
                return render(request, template, {'form': form})
    else:
        form = SignUpForm()

    return render(request, template, {'form': form})


@ratelimit(key='ip', rate='10/m', method='ALL', block=True)
def verify(request, hash):
    url = get_object_or_404(TempUrl, url_hash=hash, expires__gte=timezone.now())
    user = url.user

    if not user.is_active:
        messages.error(request, 'This account has been disabled.')
        return redirect('accounts:login')

    if request.method == 'POST':
        user.is_verified = True
        user.save()
        url.delete()
        messages.success(request, 'Your account has been verified. Please log in to continue.')
        return redirect('accounts:login')
    return render(request, 'pages/verify_confirm.html', {'hash': hash})


@login_required
def complete_profile(request):
    profile, _ = Profile.objects.get_or_create(user=request.user)
    if request.method == 'POST':
        form = CompleteProfileForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            request.user.profile_completed = True
            request.user.save()
            return redirect('dashboard:dash_index')
    else:
        form = CompleteProfileForm(instance=profile)

    return render(request, 'complete_profile.html', {'form': form})


@login_required
@require_POST
def signout(request):
    logout(request)
    return redirect('core:index')


def signin(request):
    if request.user.is_authenticated:
        return redirect(get_dashboard_url(request.user))

    if request.method == 'POST':
        form = LoginForm(request.POST)

        ip = request.META.get('REMOTE_ADDR', '') or ''
        recaptcha_token = request.POST.get('g-recaptcha-response', '')
        if not settings.DEBUG and not verify_recaptcha(recaptcha_token, ip):
            messages.error(request, 'reCAPTCHA verification failed. Please try again.')
            return render(request, 'pages/login.html', {'form': form}, status=400)

        if form.is_valid():
            cd = form.cleaned_data
            user = authenticate(request, username=cd['username'], password=cd['password'])

            if user is not None:
                if not getattr(user, 'is_verified', False):
                    messages.error(request, 'Your account has not been verified yet. Please check your email.')
                else:
                    auth_login(request, user)
                    return redirect(get_dashboard_url(request.user))
            else:
                messages.error(request, 'Invalid login details')
        else:
            messages.error(request, 'Invalid login details')
    else:
        form = LoginForm()

    return render(request, 'pages/login.html', {'form': form})


from django.utils.decorators import method_decorator
from django_ratelimit.decorators import ratelimit

@method_decorator(ratelimit(key='ip', rate='3/h', method='POST', block=True), name='dispatch')
class CaptchaPasswordResetView(auth_views.PasswordResetView):
    template_name = 'pages/forgot-password.html'

    def form_valid(self, form):
        request = self.request
        ip = request.META.get('REMOTE_ADDR', '') or ''
        recaptcha_token = request.POST.get('g-recaptcha-response', '')
        if not settings.DEBUG and not verify_recaptcha(recaptcha_token, ip):
            messages.error(request, 'reCAPTCHA verification failed. Please try again.')
            return self.form_invalid(form)
        return super().form_valid(form)


def get_dashboard_url(user):
    if getattr(user, 'is_admin', False):
        return reverse('dashboard:dash_index')
    return reverse('dashboard:profile')

