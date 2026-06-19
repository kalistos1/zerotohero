from django.urls import path
from . import views

app_name = "dashboard"

urlpatterns = [
    # ── Home ──────────────────────────────────────────────────────────────────
    path("", views.dash_index, name="dash_index"),

    # ── Profile (all roles) ───────────────────────────────────────────────────
    path("profile/", views.profile, name="profile"),

    # ── Site Settings (admin only) ────────────────────────────────────────────
    path("settings/", views.store_settings, name="store-settings"),

    # ── FAQs (admin only) ─────────────────────────────────────────────────────
    path("faqs/", views.faq_list, name="faq-list"),
    path("faqs/create/", views.faq_create, name="faq-create"),
    path("faqs/<int:pk>/edit/", views.faq_edit, name="faq-edit"),
    path("faqs/<int:pk>/delete/", views.faq_delete, name="faq-delete"),
    path("faqs/<int:pk>/toggle/", views.faq_toggle, name="faq-toggle"),

    # ── Testimonials (admin only) ─────────────────────────────────────────────
    path("testimonials/", views.testimonial_list, name="testimonial-list"),
    path("testimonials/create/", views.testimonial_create, name="testimonial-create"),
    path("testimonials/<int:pk>/edit/", views.testimonial_edit, name="testimonial-edit"),
    path("testimonials/<int:pk>/delete/", views.testimonial_delete, name="testimonial-delete"),

    # ── About Page singleton (admin only) ─────────────────────────────────────
    path("about/", views.about_page_edit, name="about-page"),

    # ── Events (admin only) ───────────────────────────────────────────────────
    path("events/", views.event_list, name="event-list"),
    path("events/create/", views.event_create, name="event-create"),
    path("events/<int:pk>/edit/", views.event_edit, name="event-edit"),
    path("events/<int:pk>/delete/", views.event_delete, name="event-delete"),

    # ── Gallery (admin only) ──────────────────────────────────────────────────
    path("gallery/", views.gallery_list, name="gallery-list"),
    path("gallery/create/", views.gallery_create, name="gallery-create"),
    path("gallery/<int:pk>/edit/", views.gallery_edit, name="gallery-edit"),
    path("gallery/<int:pk>/delete/", views.gallery_delete, name="gallery-delete"),
    path("gallery/categories/", views.gallery_category_list, name="gallery-category-list"),
    path("gallery/categories/create/", views.gallery_category_create, name="gallery-category-create"),
    path("gallery/categories/<int:pk>/edit/", views.gallery_category_edit, name="gallery-category-edit"),
    path("gallery/categories/<int:pk>/delete/", views.gallery_category_delete, name="gallery-category-delete"),

    # ── Blog (admin + mentor) ─────────────────────────────────────────────────
    path("blog/", views.blog_post_list, name="blog-post-list"),
    path("blog/create/", views.blog_post_create, name="blog-post-create"),
    path("blog/<int:pk>/edit/", views.blog_post_edit, name="blog-post-edit"),
    path("blog/<int:pk>/delete/", views.blog_post_delete, name="blog-post-delete"),
    path("blog/categories/", views.blog_category_list, name="blog-category-list"),
    path("blog/categories/create/", views.blog_category_create, name="blog-category-create"),
    path("blog/categories/<int:pk>/delete/", views.blog_category_delete, name="blog-category-delete"),

    # ── Users (admin only) ────────────────────────────────────────────────────
    path("users/", views.user_list, name="user-list"),
    path("users/create/", views.user_create, name="user-create"),
    path("users/<str:username>/edit/", views.user_edit, name="user-edit"),
    path("users/<int:user_id>/delete/", views.user_delete, name="user-delete"),

    # ── Contact Messages (admin only) ─────────────────────────────────────────
    path("messages/", views.contact_list, name="contact-messages"),
    path("messages/<int:pk>/read/", views.contact_message_read, name="contact-message-read"),
    path("messages/<int:pk>/reply/", views.contact_message_reply, name="contact-message-reply"),
    path("messages/<int:pk>/delete/", views.contact_delete, name="contact-delete"),

    # ── Tickets (all roles) ───────────────────────────────────────────────────
    path("tickets/", views.ticket_list, name="ticket-list"),
    path("tickets/create/", views.ticket_create, name="ticket-create"),
    path("tickets/<int:pk>/", views.ticket_detail, name="ticket-detail"),
    path("tickets/<int:pk>/assign/", views.ticket_assign, name="ticket-assign"),
    path("tickets/<int:pk>/status/", views.ticket_status_update, name="ticket-status-update"),

    # ── Team (admin only) ─────────────────────────────────────────────────────
    path("team/", views.team_list, name="team-list"),
    path("team/create/", views.team_create, name="team-create"),
    path("team/<int:pk>/edit/", views.team_edit, name="team-edit"),
    path("team/<int:pk>/delete/", views.team_delete, name="team-delete"),

    # ── Mentorship Applications (admin only) ──────────────────────────────────
    path("mentorships/", views.mentorship_list, name="mentorship-list"),
    path("mentorships/<int:pk>/", views.mentorship_detail, name="mentorship-detail"),
    path("mentorships/<int:pk>/email/<str:decision>/", views.mentorship_send_email, name="mentorship-send-email"),

    # ── Sponsorship Inquiries (admin only) ────────────────────────────────────
    path("sponsorships/", views.sponsorship_list, name="sponsorship-list"),
    path("sponsorships/<int:pk>/edit/", views.sponsorship_edit, name="sponsorship-edit"),
    path("sponsorships/<int:pk>/delete/", views.sponsorship_delete, name="sponsorship-delete"),

    # ── Sponsorship Tiers (admin only) ──────────────────────────────────────
    path("sponsorship-tiers/", views.sponsorship_tier_list, name="sponsorship-tier-list"),
    path("sponsorship-tiers/create/", views.sponsorship_tier_create, name="sponsorship-tier-create"),
    path("sponsorship-tiers/<int:pk>/edit/", views.sponsorship_tier_edit, name="sponsorship-tier-edit"),
    path("sponsorship-tiers/<int:pk>/delete/", views.sponsorship_tier_delete, name="sponsorship-tier-delete"),
]
