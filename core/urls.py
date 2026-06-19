from django.urls import path
from . import views
from .sitemap_views import robots_txt, sitemap_xml

app_name = "core"

urlpatterns = [
    path('', views.index, name="index"),
    path('about/', views.about_us, name="about"),
    path('contact/', views.contact_us, name="contact"),
    path('faqs/', views.faqs, name="faqs"),
    path('events/', views.events, name="events"),
    path('testimonials/', views.testimonials, name="testimonials"),
    path('terms/', views.terms, name="terms"),
    path('privacy/', views.privacy_policy, name="privacy"),
    path('apply/', views.application_form, name="application_form"),
    path('apply/thank-you/', views.application_thank_you, name="application_thank_you"),
    # SEO
    path('robots.txt', robots_txt, name="robots_txt"),
    path('sitemap.xml', sitemap_xml, name="sitemap"),
    path('sponsorship/', views.sponsorship_landing, name="sponsorship"),
    path('sponsorship/apply/', views.sponsorship_apply, name="sponsorship_apply"),
]
