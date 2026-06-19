"""
sitemap.xml and robots.txt views for Zero to Hero — Python Mentorship Platform.
"""
from django.conf import settings
from django.http import HttpResponse
from django.urls import reverse
from django.utils import timezone


def _base_url(request):
    """
    Prevents host header injection in sitemap <loc> elements and robots.txt.
    """
    if not settings.DEBUG and settings.ALLOWED_HOSTS:
        host = settings.ALLOWED_HOSTS[0]
        return f"https://{host}"
    return f"{request.scheme}://{request.get_host()}"


# ── robots.txt ─────────────────────────────────────────────────────────────────

def robots_txt(request):
    """Serve robots.txt for search engine crawlers."""
    base_url = _base_url(request)
    lines = [
        "User-agent: *",
        "Allow: /",
        "",
        "# Private areas — do not index",
        "Disallow: /admin/",
        "Disallow: /site-admin-hq/",
        "Disallow: /dashboard/",
        "Disallow: /accounts/",
        "",
        f"Sitemap: {base_url}/sitemap.xml",
    ]
    return HttpResponse("\n".join(lines), content_type="text/plain")


# ── sitemap.xml ────────────────────────────────────────────────────────────────

def sitemap_xml(request):
    """
    Dynamically generate sitemap.xml for all public pages.
    Includes: static pages + all published blog posts.
    """
    base_url = _base_url(request)
    today = timezone.now().strftime("%Y-%m-%d")

    urls = []

    # ── Helper ─────────────────────────────────────────────────────────────────
    def add_url(loc, lastmod=today, changefreq="weekly", priority="0.7"):
        urls.append(
            f"""  <url>
    <loc>{loc}</loc>
    <lastmod>{lastmod}</lastmod>
    <changefreq>{changefreq}</changefreq>
    <priority>{priority}</priority>
  </url>"""
        )

    # ── Static pages ───────────────────────────────────────────────────────────
    static_pages = [
        # (url_name,  changefreq,  priority)
        ("core:index",        "daily",   "1.0"),
        ("core:about",        "monthly", "0.8"),
        ("core:faqs",         "weekly",  "0.8"),
        ("core:events",       "daily",   "0.8"),
        ("core:testimonials", "monthly", "0.6"),
        ("core:contact",      "monthly", "0.6"),
        ("core:terms",        "yearly",  "0.3"),
        ("core:privacy",      "yearly",  "0.3"),
    ]

    for name, changefreq, priority in static_pages:
        try:
            path = reverse(name)
            add_url(base_url + path, today, changefreq, priority)
        except Exception:
            continue

    # ── Blog list page ─────────────────────────────────────────────────────────
    try:
        blog_path = reverse("blog:blog-list")
        add_url(base_url + blog_path, today, "daily", "0.9")
    except Exception:
        pass

    # ── Published blog posts ───────────────────────────────────────────────────
    try:
        from blog.models import Post

        posts = (
            Post.objects.filter(status="PUBLISHED")
            .only("slug", "date_updated")
            .order_by("-date_updated")
        )
        for post in posts:
            try:
                path = reverse("blog:blog-detail", args=[post.slug])
                lastmod = post.date_updated.strftime("%Y-%m-%d")
                add_url(base_url + path, lastmod, "weekly", "0.8")
            except Exception:
                continue
    except Exception:
        pass

    xml_content = (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        + "\n".join(urls)
        + "\n</urlset>"
    )
    return HttpResponse(xml_content, content_type="application/xml")