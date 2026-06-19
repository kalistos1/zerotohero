"""
SEO utilities for Zero to Hero — Python Mentorship Platform.
Provides schema.org JSON-LD helpers and meta-tag data generators.
"""
import json

from django.utils.html import strip_tags


def _safe_base_url(request):
    """Build base URL using ALLOWED_HOSTS[0] in production to prevent host header injection.

    Falls back to request.get_host() only in DEBUG mode where ALLOWED_HOSTS is empty.
    """
    from django.conf import settings
    if not settings.DEBUG and settings.ALLOWED_HOSTS:
        host = settings.ALLOWED_HOSTS[0]
        scheme = 'https' if not settings.DEBUG else request.scheme
        return f"{scheme}://{host}"
    return f"{request.scheme}://{request.get_host()}"



# ── Constants ──────────────────────────────────────────────────────────────────

SITE_NAME = "Zero to Hero"
SITE_DESCRIPTION = (
    "A global Python mentorship platform offering cohort-based, "
    "instructor-led programmes in Software Engineering, Data Analysis, "
    "Backend Development, Data Engineering, and Cybersecurity."
)
AREA_SERVED = "Worldwide"
KNOWS_ABOUT = [
    "Python",
    "Software Engineering",
    "Data Analysis",
    "Data Engineering",
    "Backend Development",
    "Cybersecurity",
]


# ── Schema helpers ─────────────────────────────────────────────────────────────

def get_organization_schema(request, site_settings=None):
    """
    Generate EducationalOrganization schema.org JSON-LD for the homepage / base.
    """
    base_url = _safe_base_url(request)

    schema = {
        "@context": "https://schema.org",
        "@type": "EducationalOrganization",
        "name": SITE_NAME,
        "url": base_url,
        "description": SITE_DESCRIPTION,
        "areaServed": AREA_SERVED,
        "knowsAbout": KNOWS_ABOUT,
    }

    if site_settings:
        if getattr(site_settings, "support_email", None):
            schema["email"] = site_settings.support_email
        if getattr(site_settings, "support_phone", None):
            schema["telephone"] = site_settings.support_phone
        if getattr(site_settings, "address", None):
            schema["address"] = {
                "@type": "PostalAddress",
                "streetAddress": site_settings.address,
            }

    # Sitelinks Search Box
    schema["potentialAction"] = {
        "@type": "SearchAction",
        "target": {
            "@type": "EntryPoint",
            "urlTemplate": f"{base_url}/blog/?q={{search_term_string}}",
        },
        "query-input": "required name=search_term_string",
    }

    return json.dumps(schema, indent=2)


def get_article_schema(post, request):
    """
    Generate Article schema.org JSON-LD for a blog post detail page.
    """
    base_url = _safe_base_url(request)
    post_url = request.build_absolute_uri()
    description = (
        post.meta_description
        if hasattr(post, "meta_description") and post.meta_description
        else post.snippet()
    )

    schema = {
        "@context": "https://schema.org",
        "@type": "Article",
        "headline": post.title,
        "description": description,
        "datePublished": post.date_created.isoformat(),
        "dateModified": post.date_updated.isoformat(),
        "author": {
            "@type": "Person",
            "name": post.author.get_full_name() or post.author.username,
        },
        "publisher": {
            "@type": "EducationalOrganization",
            "name": SITE_NAME,
            "url": base_url,
        },
        "url": post_url,
        "mainEntityOfPage": {
            "@type": "WebPage",
            "@id": post_url,
        },
    }

    if post.image:
        schema["image"] = base_url + post.image.url

    return json.dumps(schema, indent=2)


def get_faqpage_schema(faqs):
    """
    Generate FAQPage schema.org JSON-LD for the FAQ page.
    Accepts a queryset or list of FAQ model instances.

    faq.answer is a ProseEditorField (HTML). strip_tags() converts it to
    plain text before embedding in JSON-LD, preventing </script> injection
    when the JSON block is rendered inside a <script> tag.
    """
    schema = {
        "@context": "https://schema.org",
        "@type": "FAQPage",
        "mainEntity": [
            {
                "@type": "Question",
                "name": faq.question,
                "acceptedAnswer": {
                    "@type": "Answer",
                    "text": strip_tags(faq.answer),
                },
            }
            for faq in faqs
        ],
    }
    # ensure_ascii=True escapes <, >, & as \u003c, \u003e, \u0026 — safe inside <script>.
    return json.dumps(schema, indent=2, ensure_ascii=True)


def get_event_schema(event, request):
    """
    Generate Event schema.org JSON-LD for an individual event.
    """
    base_url = _safe_base_url(request)

    schema = {
        "@context": "https://schema.org",
        "@type": "Event",
        "name": event.title,
        "description": event.description[:500] if event.description else "",
        "startDate": event.start_datetime.isoformat(),
        "organizer": {
            "@type": "Organization",
            "name": SITE_NAME,
            "url": base_url,
        },
        "isAccessibleForFree": event.is_free,
        "eventAttendanceMode": "https://schema.org/OnlineEventAttendanceMode",
        "eventStatus": "https://schema.org/EventScheduled",
    }

    if event.end_datetime:
        schema["endDate"] = event.end_datetime.isoformat()

    if event.venue:
        schema["location"] = {
            "@type": "Place",
            "name": event.venue,
        }

    if not event.is_free and event.entry_fee:
        schema["offers"] = {
            "@type": "Offer",
            "price": str(event.entry_fee),
            "priceCurrency": "NGN",
        }

    return json.dumps(schema, indent=2)


def get_breadcrumb_schema(items, request):
    """
    Generate BreadcrumbList schema.org JSON-LD.
    items: list of (name, url_path) tuples, e.g. [('Home', '/'), ('Blog', '/blog/')]
    """
    base_url = _safe_base_url(request)
    schema = {
        "@context": "https://schema.org",
        "@type": "BreadcrumbList",
        "itemListElement": [
            {
                "@type": "ListItem",
                "position": i + 1,
                "name": name,
                "item": base_url + url_path,
            }
            for i, (name, url_path) in enumerate(items)
        ],
    }
    return json.dumps(schema, indent=2)


def generate_seo_meta(
    title=None,
    description=None,
    og_type="website",
    og_image=None,
    canonical_url=None,
    robots="index, follow",
):
    """
    Return a dict of SEO meta values to pass as template context.
    Use in views that need fine-grained control over per-page SEO.
    """
    return {
        "seo_title": title or f"{SITE_NAME} — Python Mentorship Platform",
        "seo_description": description or SITE_DESCRIPTION,
        "og_type": og_type,
        "og_image": og_image,
        "canonical_url": canonical_url,
        "seo_robots": robots,
        "twitter_card": "summary_large_image",
    }