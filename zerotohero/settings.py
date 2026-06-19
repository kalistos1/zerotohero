import os
from pathlib import Path
from django.contrib import messages
from django.core.exceptions import ImproperlyConfigured
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent


# ── Required secrets — fail loudly at startup if missing ─────────────────────

def _require_env(name):
    value = os.environ.get(name)
    if not value:
        raise ImproperlyConfigured(
            f"Required environment variable '{name}' is not set. "
            f"Copy .env.example to .env and fill in the values."
        )
    return value


SECRET_KEY = _require_env('DJANGO_SECRET_KEY')

DEBUG = os.getenv('DJANGO_DEBUG', 'False') == 'True'

_raw_hosts = os.getenv('DJANGO_ALLOWED_HOSTS', '')
ALLOWED_HOSTS = [h.strip() for h in _raw_hosts.split(',') if h.strip()]
if not DEBUG and not ALLOWED_HOSTS:
    raise ImproperlyConfigured(
        "DJANGO_ALLOWED_HOSTS must be set in production (DEBUG=False)."
    )


# ── Application definition ────────────────────────────────────────────────────

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',

    'django_htmx',
    'taggit',
    'django_prose_editor',
    'django_countries',
    'compressor',
    'axes',
    
    'csp',

    'accounts',
    'core',
    'blog',
    'dashboard',
    'mentee',
    'mentor',
    'notification',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    # Brute-force protection — must come after SessionMiddleware
    'axes.middleware.AxesMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django_htmx.middleware.HtmxMiddleware',
    'csp.middleware.CSPMiddleware',
    'core.middleware.SecurityHeadersMiddleware',
]

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.db.DatabaseCache',
        'LOCATION': 'notification_cache',
    }
}

ROOT_URLCONF = 'zerotohero.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'core.context_processors.site_settings',
                'core.context_processors.recaptcha',
                'core.context_processors.safe_base_url',
            ],
        },
    },
]

WSGI_APPLICATION = 'zerotohero.wsgi.application'

AUTHENTICATION_BACKENDS = [
    'axes.backends.AxesStandaloneBackend',   # Must be first — gates all authenticate() calls
    'accounts.backend.EmailBackend',          # Handles both username and email login
]

AUTH_USER_MODEL = 'accounts.User'

MESSAGE_TAGS = {
    messages.ERROR: 'danger',
}

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Africa/Lagos'
USE_I18N = True
USE_L10N = True
USE_TZ = True

STATIC_ROOT = os.path.join(BASE_DIR, 'staticroot')
STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']

STATICFILES_FINDERS = [
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    'compressor.finders.CompressorFinder',
]

COMPRESS_ENABLED = not DEBUG
COMPRESS_OFFLINE = True
COMPRESS_CSS_FILTERS = [
    'compressor.filters.css_default.CssAbsoluteFilter',
    'compressor.filters.cssmin.rCSSMinFilter',
]
COMPRESS_JS_FILTERS = ['compressor.filters.jsmin.JSMinFilter']

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# ── Session security ──────────────────────────────────────────────────────────

SESSION_COOKIE_AGE = 86400          # 24 hours (was 7 days — reduce stolen-cookie window)
SESSION_COOKIE_SECURE = not DEBUG
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = 'Lax'
SESSION_SAVE_EVERY_REQUEST = True
SESSION_EXPIRE_AT_BROWSER_CLOSE = True
SESSION_ENGINE = 'django.contrib.sessions.backends.db'

# ── Security headers ──────────────────────────────────────────────────────────

SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'
SECURE_REFERRER_POLICY = 'same-origin'
SECURE_CROSS_ORIGIN_OPENER_POLICY = 'same-origin'
CSRF_FAILURE_VIEW = 'core.views.csrf_failure'

# ── Email ─────────────────────────────────────────────────────────────────────

DEFAULT_FROM_EMAIL = 'no-reply@zerotohero.com'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER', '')
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD', '')
EMAIL_USE_TLS = True
EMAIL_USE_SSL = False
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
NOTIFICATION_EMAIL = os.getenv('NOTIFICATION_EMAIL', '')

LOGIN_REDIRECT_URL = '/'
LOGIN_URL = '/accounts/login/'
LOGOUT_URL = '/'

GOOGLE_MAPS_API_KEY = os.getenv('GOOGLE_MAPS_API_KEY', '')
RECAPTCHA_SITE_KEY = os.getenv('RECAPTCHA_SITE_KEY', '')
RECAPTCHA_SECRET_KEY = os.getenv('RECAPTCHA_SECRET_KEY', '')

# ── Production-only hardening ─────────────────────────────────────────────────

if not DEBUG:
    SECURE_SSL_REDIRECT = True
    CSRF_COOKIE_SECURE = True
    # Do NOT set CSRF_COOKIE_HTTPONLY=True — HTMX reads the token via JS.
    # Server-side {{ csrf_token }} injection in the base template keeps it safe.
    CSRF_COOKIE_SAMESITE = 'Strict'
    SECURE_HSTS_SECONDS = 31536000
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
    CSRF_TRUSTED_ORIGINS = ["https://zerotohero.com"]
    _raw_origins = os.getenv('DJANGO_CSRF_TRUSTED_ORIGINS', '')
    CSRF_TRUSTED_ORIGINS += [o.strip() for o in _raw_origins.split(',') if o.strip()]
    if not CSRF_TRUSTED_ORIGINS:
        raise ImproperlyConfigured(
            "DJANGO_CSRF_TRUSTED_ORIGINS must be set in production."
        )

# ── Rate limiting ─────────────────────────────────────────────────────────────

RATELIMIT_ENABLE = True
RATELIMIT_USE_CACHE = 'default'
RATELIMIT_IP_META_KEY = 'REMOTE_ADDR'

# ── CSP ───────────────────────────────────────────────────────────────────────
# Start in report-only mode, tighten after confirming no violations.

_CSP_DIRECTIVES = {
    'default-src': ("'self'",),
    'script-src': (
        "'self'",
        "'unsafe-inline'",                  # Required for inline scripts in templates
        "https://www.google.com",           # reCAPTCHA
        "https://www.gstatic.com",          # reCAPTCHA
        "https://maps.googleapis.com",      # Google Maps
        "https://unpkg.com",                # HTMX CDN (migrate to self-hosted)
    ),
    'style-src': ("'self'", "'unsafe-inline'", "https://fonts.googleapis.com"),
    'img-src': ("'self'", "data:", "https:"),
    'font-src': ("'self'", "data:", "https://fonts.gstatic.com"),
    'frame-src': (
        "https://www.google.com",           # reCAPTCHA iframe
    ),
    'connect-src': ("'self'",),
}

if DEBUG:
    CONTENT_SECURITY_POLICY_REPORT_ONLY = {'DIRECTIVES': _CSP_DIRECTIVES}
else:
    CONTENT_SECURITY_POLICY = {'DIRECTIVES': _CSP_DIRECTIVES}

# ── File uploads ──────────────────────────────────────────────────────────────

FILE_UPLOAD_MAX_MEMORY_SIZE = 10485760   # 10 MB
DATA_UPLOAD_MAX_MEMORY_SIZE = 10485760   # 10 MB
FILE_UPLOAD_PERMISSIONS = 0o644

# ── django-axes (brute-force protection) ──────────────────────────────────────

AXES_FAILURE_LIMIT = 5
AXES_COOLOFF_TIME = 1                    # hours
# Lock per (username, ip) pair AND per username alone (prevents IP-rotation bypass)
AXES_LOCKOUT_PARAMETERS = [["username", "ip_address"], ["username"]]
AXES_USERNAME_FAILURE_LIMIT = 10         # Per-username global threshold
AXES_HANDLER = 'axes.handlers.database.AxesDatabaseHandler'
AXES_LOCK_OUT_AT_FAILURE = True
AXES_RESET_ON_SUCCESS = True
AXES_VERBOSE = True
AXES_LOCKOUT_TEMPLATE = 'accounts/lockout.html'
AXES_CACHE = 'default'
AXES_ENABLE_ACCESS_FAILURE_LOG = True
AXES_META_PRECEDENCE_ORDER = ['REMOTE_ADDR']