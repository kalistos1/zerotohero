import logging

from django.contrib import messages
from django.contrib.auth import get_user_model, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.core.mail import EmailMessage
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST
from django.contrib.sessions.models import Session
from django.utils import timezone

from accounts.forms import (
    CreateUserForm,
    EditUserForm,
    PasswordChangeForm,
    ProfileForm,
    TicketAssignmentForm,
    TicketForm,
    MessageForm,
    UserProfileForm,
)
from accounts.models import Profile
from blog.models import BlogCategory, Post
from core.forms import ContactReplyForm, SiteSettingsForm
from core.models import (
    FAQ,
    AboutPage,
    Contact,
    Event,
    Gallery,
    GalleryCategory,
    SiteSettings,
    Testimonial,
    TeamMember,
)
from .forms import (
    AboutPageForm,
    BlogCategoryForm,
    BlogPostForm,
    EventForm,
    FAQForm,
    GalleryCategoryForm,
    GalleryItemForm,
    TestimonialForm,
    TeamMemberForm,
)

logger = logging.getLogger(__name__)
User = get_user_model()


# ── Helpers ────────────────────────────────────────────────────────────────────

def _admin_required(request):
    """Raise PermissionDenied if the user is not admin. Use at top of views."""
    if not request.user.is_admin:
        raise PermissionDenied


def _htmx_or_full(request, partial_template, full_template, context):
    """Return partial for HTMX requests, full page otherwise."""
    template = partial_template if request.htmx else full_template
    return render(request, template, context)


# ── Dashboard home ─────────────────────────────────────────────────────────────

@login_required
def dash_index(request):
    _admin_required(request)
    context = {
        "total_faqs": FAQ.objects.filter(is_active=True).count(),
        "total_events": Event.objects.filter(is_active=True).count(),
        "total_testimonials": Testimonial.objects.filter(is_active=True).count(),
        "total_contacts": Contact.objects.count(),
        "unread_contacts": Contact.objects.filter(read_status=False).count(),
        "total_users": User.objects.count(),
        "total_posts": Post.objects.filter(status="PUBLISHED").count(),
        # only() avoids pulling the full message body just for the preview list
        "recent_contacts": (
            Contact.objects
            .only("name", "subject", "message", "created_at", "read_status")
            .order_by("-created_at")[:5]
        ),
    }
    return render(request, "pages/dash_index.html", context)


# ── Profile ────────────────────────────────────────────────────────────────────

@login_required
def profile(request):
    user = request.user
    profile_obj, _ = Profile.objects.get_or_create(user=user)

    profile_form = UserProfileForm(instance=user)
    extra_form = ProfileForm(instance=profile_obj)
    password_form = PasswordChangeForm(user=user)

    if request.method == "POST":
        action = request.POST.get("action")

        if action == "update_profile":
            profile_form = UserProfileForm(request.POST, instance=user)
            extra_form = ProfileForm(request.POST, request.FILES, instance=profile_obj)
            if profile_form.is_valid() and extra_form.is_valid():
                profile_form.save()
                extra_form.save()
                messages.success(request, "Profile updated successfully.")
                return redirect("dashboard:profile")
            messages.error(request, "Please correct the errors below.")

        elif action == "change_password":
            password_form = PasswordChangeForm(user=user, data=request.POST)
            if password_form.is_valid():
                password_form.save()
                # Keep the user logged in after password change
                update_session_auth_hash(request, password_form.user)
                
                # Invalidate all other sessions for this user
                for session in Session.objects.filter(expire_date__gte=timezone.now()):
                    data = session.get_decoded()
                    if str(user.pk) == str(data.get('_auth_user_id', '')):
                        if session.session_key != request.session.session_key:
                            session.delete()
                            
                messages.success(request, "Password changed successfully.")
                return redirect("dashboard:profile")
            messages.error(request, "Please correct the errors below.")

    context = {
        "profile_form": profile_form,
        "extra_form": extra_form,
        "password_form": password_form,
        "profile_obj": profile_obj,
    }
    return render(request, "pages/pages-profile.html", context)


# ── Site Settings ──────────────────────────────────────────────────────────────

@login_required
def store_settings(request):
    _admin_required(request)
    instance = SiteSettings.load()

    if request.method == "POST":
        form = SiteSettingsForm(request.POST, instance=instance)
        if form.is_valid():
            form.save()
            context = {"form": form, "saved": True}
            return _htmx_or_full(
                request,
                "pages/partials/_store_settings_form.html",
                "pages/store_settings.html",
                context,
            )
        context = {"form": form, "saved": False}
        return _htmx_or_full(
            request,
            "pages/partials/_store_settings_form.html",
            "pages/store_settings.html",
            context,
        )

    form = SiteSettingsForm(instance=instance)
    return render(request, "pages/store_settings.html", {"form": form, "saved": False})


# ── FAQs ───────────────────────────────────────────────────────────────────────

@login_required
def faq_list(request):
    _admin_required(request)
    faqs = FAQ.objects.all().order_by("created_at")
    return render(request, "pages/faq_list.html", {"faqs": faqs, "form": FAQForm()})


@login_required
def faq_create(request):
    _admin_required(request)
    if request.method == "POST":
        form = FAQForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "FAQ created.")
            if request.htmx:
                faqs = FAQ.objects.all().order_by("created_at")
                return render(request, "pages/partials/_faq_list_rows.html", {"faqs": faqs})
            return redirect("dashboard:faq-list")
        if request.htmx:
            return render(request, "pages/partials/_faq_form.html", {"form": form})
    return redirect("dashboard:faq-list")


@login_required
def faq_edit(request, pk):
    _admin_required(request)
    faq = get_object_or_404(FAQ, pk=pk)
    if request.method == "POST":
        form = FAQForm(request.POST, instance=faq)
        if form.is_valid():
            form.save()
            messages.success(request, "FAQ updated.")
            if request.htmx:
                faqs = FAQ.objects.all().order_by("created_at")
                return render(request, "pages/partials/_faq_list_rows.html", {"faqs": faqs})
            return redirect("dashboard:faq-list")
        if request.htmx:
            return render(request, "pages/partials/_faq_form.html", {"form": form, "faq": faq})
        return render(request, "pages/faq_list.html", {"form": form, "faq": faq, "faqs": FAQ.objects.all()})
    # GET — return inline edit form
    form = FAQForm(instance=faq)
    if request.htmx:
        return render(request, "pages/partials/_faq_form.html", {"form": form, "faq": faq})
    return render(request, "pages/faq_list.html", {"form": form, "faq": faq, "faqs": FAQ.objects.all()})


@login_required
@require_POST
def faq_delete(request, pk):
    _admin_required(request)
    faq = get_object_or_404(FAQ, pk=pk)
    faq.delete()
    messages.success(request, "FAQ deleted.")
    if request.htmx:
        faqs = FAQ.objects.all().order_by("created_at")
        return render(request, "pages/partials/_faq_list_rows.html", {"faqs": faqs})
    return redirect("dashboard:faq-list")


@login_required
@require_POST
def faq_toggle(request, pk):
    _admin_required(request)
    faq = get_object_or_404(FAQ, pk=pk)
    faq.is_active = not faq.is_active
    faq.save(update_fields=["is_active"])
    if request.htmx:
        faqs = FAQ.objects.all().order_by("created_at")
        return render(request, "pages/partials/_faq_list_rows.html", {"faqs": faqs})
    return redirect("dashboard:faq-list")


# ── Testimonials ───────────────────────────────────────────────────────────────

@login_required
def testimonial_list(request):
    _admin_required(request)
    testimonials = Testimonial.objects.all().order_by("-created_at")
    return render(request, "pages/testimonial_list.html", {"testimonials": testimonials, "form": TestimonialForm()})


@login_required
def testimonial_create(request):
    _admin_required(request)
    if request.method == "POST":
        form = TestimonialForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, "Testimonial added.")
            return redirect("dashboard:testimonial-list")
        return render(request, "pages/testimonial_list.html", {
            "form": form,
            "testimonials": Testimonial.objects.all().order_by("-created_at"),
        })
    return redirect("dashboard:testimonial-list")


@login_required
def testimonial_edit(request, pk):
    _admin_required(request)
    obj = get_object_or_404(Testimonial, pk=pk)
    if request.method == "POST":
        form = TestimonialForm(request.POST, request.FILES, instance=obj)
        if form.is_valid():
            form.save()
            messages.success(request, "Testimonial updated.")
            return redirect("dashboard:testimonial-list")
        return render(request, "pages/testimonial_edit.html", {"form": form, "obj": obj})
    form = TestimonialForm(instance=obj)
    return render(request, "pages/testimonial_edit.html", {"form": form, "obj": obj})


@login_required
@require_POST
def testimonial_delete(request, pk):
    _admin_required(request)
    obj = get_object_or_404(Testimonial, pk=pk)
    obj.delete()
    messages.success(request, "Testimonial deleted.")
    return redirect("dashboard:testimonial-list")


# ── About Page (singleton) ─────────────────────────────────────────────────────

@login_required
def about_page_edit(request):
    _admin_required(request)
    instance = AboutPage.load()
    if request.method == "POST":
        form = AboutPageForm(request.POST, request.FILES, instance=instance)
        if form.is_valid():
            form.save()
            messages.success(request, "About page updated.")
            return redirect("dashboard:about-page")
        return render(request, "pages/about_page_edit.html", {"form": form})
    form = AboutPageForm(instance=instance)
    return render(request, "pages/about_page_edit.html", {"form": form})


# ── Events ─────────────────────────────────────────────────────────────────────

@login_required
def event_list(request):
    _admin_required(request)
    events = Event.objects.all().order_by("-start_datetime")
    return render(request, "pages/event_list.html", {"events": events, "form": EventForm()})


@login_required
def event_create(request):
    _admin_required(request)
    if request.method == "POST":
        form = EventForm(request.POST, request.FILES)
        if form.is_valid():
            event = form.save(commit=False)
            event.created_by = request.user
            event.save()
            messages.success(request, "Event created.")
            return redirect("dashboard:event-list")
        return render(request, "pages/event_list.html", {
            "form": form,
            "events": Event.objects.all().order_by("-start_datetime"),
        })
    return redirect("dashboard:event-list")


@login_required
def event_edit(request, pk):
    _admin_required(request)
    event = get_object_or_404(Event, pk=pk)
    if request.method == "POST":
        form = EventForm(request.POST, request.FILES, instance=event)
        if form.is_valid():
            form.save()
            messages.success(request, "Event updated.")
            return redirect("dashboard:event-list")
        return render(request, "pages/event_edit.html", {"form": form, "event": event})
    form = EventForm(instance=event)
    # Fix datetime-local input format
    if event.start_datetime:
        form.initial["start_datetime"] = event.start_datetime.strftime("%Y-%m-%dT%H:%M")
    if event.end_datetime:
        form.initial["end_datetime"] = event.end_datetime.strftime("%Y-%m-%dT%H:%M")
    return render(request, "pages/event_edit.html", {"form": form, "event": event})


@login_required
@require_POST
def event_delete(request, pk):
    _admin_required(request)
    event = get_object_or_404(Event, pk=pk)
    event.delete()
    messages.success(request, "Event deleted.")
    return redirect("dashboard:event-list")


# ── Gallery ────────────────────────────────────────────────────────────────────

@login_required
def gallery_list(request):
    _admin_required(request)
    items = Gallery.objects.select_related("category").all()
    categories = GalleryCategory.objects.all()
    return render(request, "pages/gallery_list.html", {
        "items": items,
        "categories": categories,
        "form": GalleryItemForm(),
    })


@login_required
def gallery_create(request):
    _admin_required(request)
    if request.method == "POST":
        form = GalleryItemForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, "Gallery item added.")
            return redirect("dashboard:gallery-list")
        return render(request, "pages/gallery_list.html", {
            "form": form,
            "items": Gallery.objects.select_related("category").all(),
            "categories": GalleryCategory.objects.all(),
        })
    return redirect("dashboard:gallery-list")


@login_required
def gallery_edit(request, pk):
    _admin_required(request)
    item = get_object_or_404(Gallery, pk=pk)
    if request.method == "POST":
        form = GalleryItemForm(request.POST, request.FILES, instance=item)
        if form.is_valid():
            form.save()
            messages.success(request, "Gallery item updated.")
            return redirect("dashboard:gallery-list")
        return render(request, "pages/gallery_edit.html", {"form": form, "item": item})
    form = GalleryItemForm(instance=item)
    return render(request, "pages/gallery_edit.html", {"form": form, "item": item})


@login_required
@require_POST
def gallery_delete(request, pk):
    _admin_required(request)
    item = get_object_or_404(Gallery, pk=pk)
    item.delete()
    messages.success(request, "Gallery item deleted.")
    return redirect("dashboard:gallery-list")


@login_required
def gallery_category_list(request):
    _admin_required(request)
    categories = GalleryCategory.objects.all()
    return render(request, "pages/gallery_category_list.html", {
        "categories": categories,
        "form": GalleryCategoryForm(),
    })


@login_required
def gallery_category_create(request):
    _admin_required(request)
    if request.method == "POST":
        form = GalleryCategoryForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Gallery category created.")
            return redirect("dashboard:gallery-category-list")
        return render(request, "pages/gallery_category_list.html", {
            "form": form,
            "categories": GalleryCategory.objects.all(),
        })
    return redirect("dashboard:gallery-category-list")


@login_required
def gallery_category_edit(request, pk):
    _admin_required(request)
    category = get_object_or_404(GalleryCategory, pk=pk)
    if request.method == "POST":
        form = GalleryCategoryForm(request.POST, instance=category)
        if form.is_valid():
            form.save()
            messages.success(request, "Category updated.")
            return redirect("dashboard:gallery-category-list")
        return render(request, "pages/gallery_category_edit.html", {"form": form, "category": category})
    form = GalleryCategoryForm(instance=category)
    return render(request, "pages/gallery_category_edit.html", {"form": form, "category": category})


@login_required
@require_POST
def gallery_category_delete(request, pk):
    _admin_required(request)
    category = get_object_or_404(GalleryCategory, pk=pk)
    category.delete()
    messages.success(request, "Category deleted.")
    return redirect("dashboard:gallery-category-list")


# ── Blog ───────────────────────────────────────────────────────────────────────

@login_required
def blog_post_list(request):
    if not (request.user.is_admin or request.user.is_mentor):
        raise PermissionDenied
    qs = Post.objects.select_related("author", "category").order_by("-date_created")
    # Mentors only see their own posts
    if request.user.is_mentor and not request.user.is_admin:
        qs = qs.filter(author=request.user)
    paginator = Paginator(qs, 20)
    page = paginator.get_page(request.GET.get("page"))
    return render(request, "pages/blog_post_list.html", {"page_obj": page})


@login_required
def blog_post_create(request):
    if not (request.user.is_admin or request.user.is_mentor):
        raise PermissionDenied
    if request.method == "POST":
        form = BlogPostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            # taggit requires save() first
            form.save_m2m()
            messages.success(request, "Post created.")
            return redirect("dashboard:blog-post-list")
        return render(request, "pages/blog_post_form.html", {"form": form})
    form = BlogPostForm()
    return render(request, "pages/blog_post_form.html", {"form": form})


@login_required
def blog_post_edit(request, pk):
    if not (request.user.is_admin or request.user.is_mentor):
        raise PermissionDenied
    post = get_object_or_404(Post, pk=pk)
    # Mentors can only edit their own posts
    if request.user.is_mentor and not request.user.is_admin and post.author != request.user:
        raise PermissionDenied
    if request.method == "POST":
        form = BlogPostForm(request.POST, request.FILES, instance=post)
        if form.is_valid():
            form.save()
            messages.success(request, "Post updated.")
            return redirect("dashboard:blog-post-list")
        return render(request, "pages/blog_post_form.html", {"form": form, "post": post})
    form = BlogPostForm(instance=post)
    return render(request, "pages/blog_post_form.html", {"form": form, "post": post})


@login_required
@require_POST
def blog_post_delete(request, pk):
    if not (request.user.is_admin or request.user.is_mentor):
        raise PermissionDenied
    post = get_object_or_404(Post, pk=pk)
    if request.user.is_mentor and not request.user.is_admin and post.author != request.user:
        raise PermissionDenied
    post.delete()
    messages.success(request, "Post deleted.")
    return redirect("dashboard:blog-post-list")


@login_required
def blog_category_list(request):
    _admin_required(request)
    categories = BlogCategory.objects.select_related("parent__parent__parent").all()
    return render(request, "pages/blog_category_list.html", {
        "categories": categories,
        "form": BlogCategoryForm(),
    })


@login_required
def blog_category_create(request):
    _admin_required(request)
    if request.method == "POST":
        form = BlogCategoryForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Blog category created.")
            return redirect("dashboard:blog-category-list")
        return render(request, "pages/blog_category_list.html", {
            "form": form,
            "categories": BlogCategory.objects.select_related("parent__parent__parent").all(),
        })
    return redirect("dashboard:blog-category-list")


@login_required
@require_POST
def blog_category_delete(request, pk):
    _admin_required(request)
    category = get_object_or_404(BlogCategory, pk=pk)
    category.delete()
    messages.success(request, "Blog category deleted.")
    return redirect("dashboard:blog-category-list")


# ── Users ──────────────────────────────────────────────────────────────────────

@login_required
def user_list(request):
    _admin_required(request)
    users = User.objects.all().order_by("-date_joined")
    paginator = Paginator(users, 25)
    page = paginator.get_page(request.GET.get("page"))
    return render(request, "pages/user_list.html", {"page_obj": page})


@login_required
def user_create(request):
    _admin_required(request)
    if request.method == "POST":
        form = CreateUserForm(request.POST)
        if form.is_valid():
            role = form.cleaned_data.get('user_role')
            if role == 'admin' and not request.user.is_superuser:
                messages.error(request, "Only superusers can create admin accounts.")
                return render(request, "pages/user_form.html", {"form": form})
                
            user = form.save()
            messages.success(request, f"User '{user.username}' created.")
            return redirect("dashboard:user-list")
        return render(request, "pages/user_form.html", {"form": form})
    form = CreateUserForm()
    return render(request, "pages/user_form.html", {"form": form})


@login_required
def user_edit(request, username):
    _admin_required(request)
    user = get_object_or_404(User, username=username)

    if user.is_superuser and not request.user.is_superuser:
        raise PermissionDenied("Only superusers can edit superuser accounts.")
    if user.is_admin and user != request.user and not request.user.is_superuser:
        raise PermissionDenied("Admins cannot edit other admin accounts.")

    if request.method == "POST":
        form = EditUserForm(request.POST, instance=user)
        if form.is_valid():
            role = form.cleaned_data.get('user_role')
            if role == 'admin' and not request.user.is_superuser and not user.is_admin:
                messages.error(request, "Only superusers can grant admin privileges.")
                return render(request, "pages/user_form.html", {"form": form, "edit_user": user})
                
            form.save()
            messages.success(request, f"User '{user.username}' updated.")
            return redirect("dashboard:user-list")
        return render(request, "pages/user_form.html", {"form": form, "edit_user": user})
    form = EditUserForm(instance=user)
    return render(request, "pages/user_form.html", {"form": form, "edit_user": user})


@login_required
@require_POST
def user_delete(request, user_id):
    _admin_required(request)
    user = get_object_or_404(User, id=user_id)
    if user == request.user:
        messages.error(request, "You cannot delete your own account.")
        return redirect("dashboard:user-list")
    username = user.username
    user.delete()
    messages.success(request, f"User '{username}' deleted.")
    return redirect("dashboard:user-list")


# ── Contact Messages ───────────────────────────────────────────────────────────

@login_required
def contact_list(request):
    _admin_required(request)
    qs = Contact.objects.order_by("-created_at")
    paginator = Paginator(qs, 20)
    page = paginator.get_page(request.GET.get("page"))
    return render(request, "pages/apps-email.html", {"page": page})


@login_required
def contact_message_read(request, pk):
    _admin_required(request)
    message = get_object_or_404(Contact, pk=pk)
    if not message.read_status:
        message.read_status = True
        message.save(update_fields=["read_status"])
    replies = message.replies.all()
    context = {"m": message, "replies": replies, "reply_form": ContactReplyForm()}
    if request.htmx:
        return render(request, "pages/partials/_contact_detail.html", context)
    return render(request, "pages/apps-email.html", context)


@login_required
@require_POST
def contact_message_reply(request, pk):
    _admin_required(request)
    message = get_object_or_404(Contact, pk=pk)
    form = ContactReplyForm(request.POST)
    if form.is_valid():
        reply = form.save(commit=False)
        reply.contact = message
        reply.replied_by = request.user
        reply.save()
        # Send reply email to the original sender
        try:
            email = EmailMessage(
                subject=(reply.subject.replace('\n', '').replace('\r', '')[:200]) or f"Re: {message.subject}",
                body=reply.body,
                to=[message.email],
                reply_to=[request.user.email] if request.user.email else [],
            )
            email.send(fail_silently=False)
            status, msg = "success", "Reply sent successfully."
        except Exception:
            logger.exception("Failed to send reply email to %s", message.email)
            status, msg = "warning", "Reply saved (email delivery failed — check SMTP config)."

        if request.htmx:
            return render(request, "pages/partials/_contact_reply_result.html", {"status": status, "message": msg})
        messages.success(request, msg)
        return redirect("dashboard:contact-messages")

    if request.htmx:
        return render(request, "pages/partials/_contact_reply_result.html", {
            "status": "error",
            "message": "Invalid form. Please fill in the reply body.",
        })
    messages.error(request, "Invalid form.")
    return redirect("dashboard:contact-messages")


@login_required
@require_POST
def contact_delete(request, pk):
    _admin_required(request)
    message = get_object_or_404(Contact, pk=pk)
    message.delete()
    messages.success(request, "Message deleted.")
    return redirect("dashboard:contact-messages")


# ── Tickets ────────────────────────────────────────────────────────────────────

@login_required
def ticket_list(request):
    from accounts.models import Ticket
    qs = Ticket.objects.select_related("user", "assigned_to").order_by("-created_at")
    # Non-admins only see their own tickets
    if not request.user.is_admin:
        qs = qs.filter(user=request.user)
    paginator = Paginator(qs, 20)
    page = paginator.get_page(request.GET.get("page"))
    return render(request, "pages/ticket_list.html", {"page_obj": page})


@login_required
def ticket_create(request):
    if request.method == "POST":
        form = TicketForm(request.POST)
        if form.is_valid():
            ticket = form.save(commit=False)
            ticket.user = request.user
            ticket.save()
            messages.success(request, f"Ticket {ticket.ticket_id} created.")
            return redirect("dashboard:ticket-detail", pk=ticket.pk)
        return render(request, "pages/ticket_create.html", {"form": form})
    form = TicketForm()
    return render(request, "pages/ticket_create.html", {"form": form})


@login_required
def ticket_detail(request, pk):
    from accounts.models import Ticket
    ticket = get_object_or_404(Ticket, pk=pk)
    if not request.user.is_admin and ticket.user != request.user:
        raise PermissionDenied

    if request.method == "POST":
        msg_form = MessageForm(request.POST)
        if msg_form.is_valid():
            msg = msg_form.save(commit=False)
            msg.ticket = ticket
            msg.sender = request.user
            msg.save()
            if request.htmx:
                return render(request, "pages/partials/_ticket_messages.html", {"ticket": ticket})
            return redirect("dashboard:ticket-detail", pk=pk)
        messages.error(request, "Could not send message.")
    else:
        msg_form = MessageForm()

    assign_form = TicketAssignmentForm(instance=ticket) if request.user.is_admin else None
    context = {
        "ticket": ticket,
        "msg_form": msg_form,
        "assign_form": assign_form,
    }
    return render(request, "pages/ticket_detail.html", context)


@login_required
@require_POST
def ticket_assign(request, pk):
    _admin_required(request)
    from accounts.models import Ticket
    ticket = get_object_or_404(Ticket, pk=pk)
    form = TicketAssignmentForm(request.POST, instance=ticket)
    if form.is_valid():
        form.save()
        messages.success(request, "Ticket assigned.")
    else:
        messages.error(request, "Assignment failed.")
    return redirect("dashboard:ticket-detail", pk=pk)


@login_required
@require_POST
def ticket_status_update(request, pk):
    _admin_required(request)
    from accounts.models import Ticket
    ticket = get_object_or_404(Ticket, pk=pk)
    new_status = request.POST.get("status")
    valid_statuses = {s[0] for s in Ticket.STATUS_CHOICES}
    if new_status not in valid_statuses:
        messages.error(request, "Invalid status.")
        return redirect("dashboard:ticket-detail", pk=pk)
    ticket.status = new_status
    ticket.save(update_fields=["status"])
    messages.success(request, f"Status changed to {ticket.get_status_display()}.")
    return redirect("dashboard:ticket-detail", pk=pk)


# ── Team Members ───────────────────────────────────────────────────────────────

@login_required
def team_list(request):
    _admin_required(request)
    team_members = TeamMember.objects.all().order_by("-created_at")
    return render(request, "pages/team_list.html", {"team_members": team_members, "form": TeamMemberForm()})


@login_required
def team_create(request):
    _admin_required(request)
    if request.method == "POST":
        form = TeamMemberForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, "Team member added.")
            return redirect("dashboard:team-list")
        return render(request, "pages/team_list.html", {
            "form": form,
            "team_members": TeamMember.objects.all().order_by("-created_at"),
        })
    return redirect("dashboard:team-list")


@login_required
def team_edit(request, pk):
    _admin_required(request)
    member = get_object_or_404(TeamMember, pk=pk)
    if request.method == "POST":
        form = TeamMemberForm(request.POST, request.FILES, instance=member)
        if form.is_valid():
            form.save()
            messages.success(request, "Team member updated.")
            return redirect("dashboard:team-list")
        return render(request, "pages/team_edit.html", {"form": form, "member": member})
    form = TeamMemberForm(instance=member)
    return render(request, "pages/team_edit.html", {"form": form, "member": member})


@login_required
@require_POST
def team_delete(request, pk):
    _admin_required(request)
    member = get_object_or_404(TeamMember, pk=pk)
    member.delete()
    messages.success(request, "Team member deleted.")
    return redirect("dashboard:team-list")
# ── Mentorship Applications ──────────────────────────────────────────────────

@login_required
def mentorship_list(request):
    _admin_required(request)
    from core.models import MentorshipApplication
    from django.db.models import Count
    
    qs = MentorshipApplication.objects.all().order_by("-created_at")
    
    # Analytics data
    total_apps = qs.count()
    status_counts = list(qs.values("status").annotate(count=Count("status")))
    status_dict = {item["status"]: item["count"] for item in status_counts}
    
    tech_counts = {}
    for app in qs:
        for tech in app.get_tech_interests_list():
            tech_counts[tech] = tech_counts.get(tech, 0) + 1
            
    sorted_tech = sorted(tech_counts.items(), key=lambda x: x[1], reverse=True)[:5]
    
    paginator = Paginator(qs, 50)
    page = paginator.get_page(request.GET.get("page"))
    
    context = {
        "page_obj": page,
        "total_apps": total_apps,
        "status_counts": status_dict,
        "top_tech": sorted_tech,
    }
    return render(request, "pages/mentorship_list.html", context)


@login_required
def mentorship_detail(request, pk):
    _admin_required(request)
    from core.models import MentorshipApplication
    from .forms import MentorshipAdminReviewForm
    
    app = get_object_or_404(MentorshipApplication, pk=pk)
    
    if request.method == "POST":
        form = MentorshipAdminReviewForm(request.POST, instance=app)
        if form.is_valid():
            form.save()
            messages.success(request, "Application updated successfully.")
            return redirect("dashboard:mentorship-detail", pk=pk)
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field.replace('_', ' ').title()}: {error}")
            return redirect("dashboard:mentorship-detail", pk=pk)
        
    return render(request, "pages/mentorship_detail.html", {"app": app})


from django.views.decorators.http import require_POST

@login_required
@require_POST
def mentorship_send_email(request, pk, decision):
    _admin_required(request)
    from core.models import MentorshipApplication
    from core.tasks import send_decision_email_task
    
    if decision not in ['accepted', 'rejected']:
        messages.error(request, "Invalid email decision type.")
        return redirect("dashboard:mentorship-detail", pk=pk)
        
    app = get_object_or_404(MentorshipApplication, pk=pk)
    
    # Dispatch the background task via Huey
    send_decision_email_task(app.id, decision)
    
    messages.success(request, f"{decision.capitalize()} email has been queued to send to {app.email}.")
    return redirect("dashboard:mentorship-detail", pk=pk)


from core.models import SponsorshipInquiry, SponsorshipTier
from core.forms import SponsorshipDashboardForm, SponsorshipTierForm


# ── Sponsorship Inquiries ──────────────────────────────────────────────────────

@login_required
def sponsorship_list(request):
    _admin_required(request)
    qs = SponsorshipInquiry.objects.select_related('tier').all()
    status_filter = request.GET.get('status')
    if status_filter:
        qs = qs.filter(status=status_filter)
    paginator = Paginator(qs, 20)
    page = paginator.get_page(request.GET.get('page'))
    return render(request, 'pages/sponsorship_list.html', {'page_obj': page, 'current_status': status_filter})


@login_required
def sponsorship_edit(request, pk):
    _admin_required(request)
    inquiry = get_object_or_404(SponsorshipInquiry, pk=pk)
    if request.method == 'POST':
        form = SponsorshipDashboardForm(request.POST, instance=inquiry)
        if form.is_valid():
            form.save()
            messages.success(request, 'Sponsorship inquiry updated.')
            return redirect('dashboard:sponsorship-list')
        for field, errors in form.errors.items():
            for error in errors:
                messages.error(request, f"{field.replace('_', ' ').title()}: {error}")
    else:
        form = SponsorshipDashboardForm(instance=inquiry)
    return render(request, 'pages/sponsorship_edit.html', {'form': form, 'inquiry': inquiry})


@login_required
@require_POST
def sponsorship_delete(request, pk):
    _admin_required(request)
    inquiry = get_object_or_404(SponsorshipInquiry, pk=pk)
    inquiry.delete()
    messages.success(request, 'Sponsorship inquiry deleted.')
    return redirect('dashboard:sponsorship-list')


# ── Sponsorship Tiers (admin CRUD) ─────────────────────────────────────────────

@login_required
def sponsorship_tier_list(request):
    _admin_required(request)
    tiers = SponsorshipTier.objects.all()
    return render(request, 'pages/sponsorship_tier_list.html', {'tiers': tiers})


@login_required
def sponsorship_tier_create(request):
    _admin_required(request)
    if request.method == 'POST':
        form = SponsorshipTierForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Sponsorship tier created.')
            return redirect('dashboard:sponsorship-tier-list')
        for field, errors in form.errors.items():
            for error in errors:
                messages.error(request, f"{field.replace('_', ' ').title()}: {error}")
    else:
        form = SponsorshipTierForm()
    return render(request, 'pages/sponsorship_tier_form.html', {'form': form, 'action': 'Create'})


@login_required
def sponsorship_tier_edit(request, pk):
    _admin_required(request)
    tier = get_object_or_404(SponsorshipTier, pk=pk)
    if request.method == 'POST':
        form = SponsorshipTierForm(request.POST, instance=tier)
        if form.is_valid():
            form.save()
            messages.success(request, 'Sponsorship tier updated.')
            return redirect('dashboard:sponsorship-tier-list')
        for field, errors in form.errors.items():
            for error in errors:
                messages.error(request, f"{field.replace('_', ' ').title()}: {error}")
    else:
        form = SponsorshipTierForm(instance=tier)
    return render(request, 'pages/sponsorship_tier_form.html', {'form': form, 'tier': tier, 'action': 'Edit'})


@login_required
@require_POST
def sponsorship_tier_delete(request, pk):
    _admin_required(request)
    tier = get_object_or_404(SponsorshipTier, pk=pk)
    tier.delete()
    messages.success(request, 'Sponsorship tier deleted.')
    return redirect('dashboard:sponsorship-tier-list')