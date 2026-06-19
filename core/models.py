from django.core.cache import cache
from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator, URLValidator
from django.db import models, transaction
from django.utils import timezone
from django.utils.html import strip_tags
from django.utils.text import slugify
from django_prose_editor.fields import ProseEditorField
from taggit.managers import TaggableManager

from core.validators import validate_video_upload


# Shared rich-text extensions used across all ProseEditorField instances
_PROSE_EXTENSIONS = {
    "Bold": {},
    "Italic": {},
    "Heading": {"levels": [1, 2, 3]},
    "Link": {},
    "BulletList": {},
    "OrderedList": {},
    "ListItem": {},
    "Blockquote": {},
    "History": {},
}


class MentorshipApplication(models.Model):
    EXPERIENCE_CHOICES = [
        ('complete_beginner', 'Complete beginner (I have never coded in Python)'),
        ('beginner', 'Beginner (I have written basic Python — print statements, variables)'),
        ('intermediate', 'Intermediate (I am familiar with loops, functions, and basic projects)'),
        ('advanced', 'Advanced (I am comfortable with OOP, data structures, and libraries)'),
    ]

    STREAM_CHOICES = [
        ('beginner', 'Stream 1: Beginner Zero to Hero (no prior Python knowledge needed)'),
        ('specialty', 'Stream 2: Specialty Zero to Hero (requires at least intermediate Python knowledge)'),
    ]

    TECH_FIELD_CHOICES = [
        ('backend_development', 'Backend Development'),
        ('data_analysis', 'Data Analysis'),
        ('scripting_automation', 'Scripting & Automation'),
        ('cybersecurity', 'Cyber Security'),
        ('data_engineering', 'Data Engineering'),
    ]

    COMMUNITY_CHOICES = [
        ('yes', 'Yes'),
        ('no', 'No'),
    ]

    SCHEDULE_CHOICES = [
        ('yes', 'Yes, I can commit'),
        ('no', 'No, I cannot commit'),
        ('unsure', "I'm not sure"),
    ]

    DEVICE_ACCESS_CHOICES = [
        ('yes', 'Yes, I have reliable access'),
        ('no', 'No'),
        ('partial', 'I have partial access (shared device or inconsistent internet)'),
    ]

    REFERRAL_CHOICES = [
        ('black_python_dev', 'Black Python Dev website / social media'),
        ('friend_colleague', 'Friend or colleague'),
        ('whatsapp_group', 'WhatsApp group'),
        ('online_search', 'Online search'),
        ('other', 'Other'),
    ]

    full_name = models.CharField(max_length=200)
    email = models.EmailField(unique=True)
    address = models.CharField(max_length=300)
    phone_number = models.CharField(max_length=25)
    country = models.CharField(max_length=100)
    python_community_member = models.CharField(max_length=3, choices=COMMUNITY_CHOICES)
    # Only required when python_community_member == 'yes'
    python_community_name = models.CharField(max_length=200, blank=True)
    experience_level = models.CharField(max_length=20, choices=EXPERIENCE_CHOICES)
    programming_experience = models.TextField(blank=True)
    mentorship_stream = models.CharField(max_length=20, choices=STREAM_CHOICES)
    # Comma-separated values from TECH_FIELD_CHOICES, e.g. "backend_development,data_analysis"
    tech_interests = models.JSONField(default=list)
    reason_for_joining = models.TextField()
    schedule_commitment = models.CharField(max_length=10, choices=SCHEDULE_CHOICES)
    device_access = models.CharField(max_length=10, choices=DEVICE_ACCESS_CHOICES)
    referral_source = models.CharField(max_length=20, choices=REFERRAL_CHOICES)
    
    # Optional field if they choose "Other"
    referral_other = models.CharField(max_length=200, blank=True)

    # Admin Management Fields
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('under_review', 'Under Review'),
        ('interview', 'Interviewing'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
        ('waitlisted', 'Waitlisted'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    internal_score = models.IntegerField(default=0, help_text="Score from 1 to 5")
    admin_notes = models.TextField(blank=True, help_text="Private internal notes")

    questions_concerns = models.TextField(blank=True)
    agreed_to_terms = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.full_name} — {self.email}"

    def get_tech_interests_list(self):
        # Already a list because of JSONField, but map to readable names
        interests = self.tech_interests if isinstance(self.tech_interests, list) else []
        mapping = dict(self.TECH_FIELD_CHOICES)
        return [mapping.get(i, i) for i in interests]


class Testimonial(models.Model):
    MEDIA_TEXT = "text"
    MEDIA_SCREENSHOT = "screenshot"
    MEDIA_VIDEO = "video"

    MEDIA_TYPE_CHOICES = [
        (MEDIA_TEXT, "Text Review"),
        (MEDIA_SCREENSHOT, "Chat Screenshot"),
        (MEDIA_VIDEO, "Video Testimonial"),
    ]

    # ── Person details ─────────────────────────────────────────────────
    name = models.CharField(max_length=255)
    role = models.CharField(max_length=255)
    # Profile photo of the person giving the testimonial
    image = models.ImageField(upload_to="testimonials/profiles/", blank=True, null=True)
    rating = models.PositiveIntegerField(
        default=5,
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text="Rating should be between 1 and 5.",
    )

    # ── Testimonial content ────────────────────────────────────────────
    # Determines which content field is rendered on the frontend
    media_type = models.CharField(
        max_length=20,
        choices=MEDIA_TYPE_CHOICES,
        default=MEDIA_TEXT,
        db_index=True,
        help_text="How the testimonial content is displayed",
    )
    # Always store the text review — used when media_type=text, or as caption
    review_text = ProseEditorField(blank=True, extensions=_PROSE_EXTENSIONS, sanitize=True)
    # Screenshot of a WhatsApp / DM / email chat sent to your inbox
    chat_screenshot = models.ImageField(
        upload_to="testimonials/screenshots/",
        blank=True,
        null=True,
        help_text="Screenshot of a chat or message from this person",
    )
    video_file = models.FileField(
        upload_to="testimonials/videos/",
        blank=True,
        null=True,
        validators=[validate_video_upload],
        help_text="Short testimonial video (MP4/WebM/OGG/MOV, ≤50 MB)",
    )

    # ── Metadata ───────────────────────────────────────────────────────
    is_active = models.BooleanField(default=True, db_index=True)
    user = models.ForeignKey(
        "accounts.User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="testimonials",
        help_text="Link to platform user if testimonial is from a registered user",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["is_active", "-created_at"]),
        ]

    def __str__(self):
        return f"{self.name} - {self.role}"

    def get_rating_range(self):
        """Return a range for template star rendering."""
        return range(self.rating)

    def clean(self):
        if self.media_type == self.MEDIA_SCREENSHOT and not self.chat_screenshot:
            raise ValidationError(
                {"chat_screenshot": "A screenshot image is required for 'Chat Screenshot' type."}
            )
        if self.media_type == self.MEDIA_VIDEO and not self.video_file:
            raise ValidationError(
                {"video_file": "A video file is required for 'Video Testimonial' type."}
            )
        if self.media_type == self.MEDIA_TEXT and not strip_tags(self.review_text).strip():
            raise ValidationError(
                {"review_text": "Review text is required for 'Text Review' type."}
            )


class FAQ(models.Model):
    """Frequently Asked Questions for customer support."""

    question = models.CharField(max_length=255)
    answer = ProseEditorField(extensions=_PROSE_EXTENSIONS, sanitize=True)
    tags = TaggableManager()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["created_at"]

    def __str__(self):
        return self.question

    def get_answer_snippet(self, length=50):
        text = strip_tags(self.answer)
        return text if len(text) <= length else text[:length] + '…'

    @classmethod
    def search_faqs(cls, query):
        return cls.objects.filter(
            models.Q(question__icontains=query) | models.Q(answer__icontains=query)
        )


class Contact(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=20, null=True, blank=True)
    subject = models.CharField(max_length=200)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    read_status = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.name} - {self.subject}"

    def has_reply(self):
        """Check if this inquiry has been replied to."""
        return self.replies.exists()

    @property
    def snippet(self):
        """A short preview of the message."""
        return self.message[:30] + "..." if len(self.message) > 30 else self.message


class ContactReply(models.Model):
    """A staff reply to a contact inquiry."""

    contact = models.ForeignKey(
        Contact,
        on_delete=models.CASCADE,
        related_name="replies",
    )
    subject = models.CharField(max_length=200, blank=True)
    body = models.TextField()
    replied_by = models.ForeignKey(
        "accounts.User",
        on_delete=models.SET_NULL,
        null=True,
        related_name="contact_replies",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["created_at"]

    def __str__(self):
        return f"Reply to {self.contact} by {self.replied_by}"




class GalleryCategory(models.Model):
    """Category for organizing gallery items."""

    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True, blank=True)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "Gallery Categories"
        ordering = ["name"]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            base = slugify(self.name)
            slug = base
            counter = 1
            while (
                GalleryCategory.objects.filter(slug=slug).exclude(pk=self.pk).exists()
            ):
                slug = f"{base}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)


class Gallery(models.Model):
    MEDIA_TYPE_CHOICES = [
        ("image", "Image"),
        ("video", "Video"),
        ("other", "Other"),
    ]

    title = models.CharField(max_length=200, blank=True)
    caption = models.TextField(blank=True)
    media_type = models.CharField(
        max_length=10,
        choices=MEDIA_TYPE_CHOICES,
        default="image",
    )
    image = models.ImageField(
        upload_to="gallery/%Y/%m/%d/",
        blank=True,
        null=True,
        help_text="Upload high-quality images (recommended size: 1920x1080)",
    )
    media_url = models.URLField(
        blank=True,
        help_text="URL for embedded content (YouTube/Vimeo videos)",
        validators=[URLValidator(schemes=['https'])],
    )
    category = models.ForeignKey(
        GalleryCategory,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="items",
    )
    alt_text = models.CharField(
        max_length=200,
        blank=True,
        help_text="Alternative text for accessibility",
    )
    position = models.PositiveIntegerField(
        default=0,
        help_text="Position in category ordering (lower numbers first)",
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "Gallery Items"
        ordering = ["position", "-created_at"]

    def __str__(self):
        return self.title or f"Gallery Item #{self.id}"

    def save(self, *args, **kwargs):
        if not self.alt_text and self.image:
            self.alt_text = (
                f"{self.title or 'Gallery image'} - {self.category or 'Uncategorized'}"
            )
        super().save(*args, **kwargs)

    def clean(self):
        super().clean()
        if self.media_url:
            from urllib.parse import urlparse
            domain = urlparse(self.media_url).netloc.lower()
            if not domain.endswith('youtube.com') and not domain.endswith('vimeo.com') and domain != 'youtu.be':
                raise ValidationError({'media_url': 'Only YouTube and Vimeo URLs are allowed.'})
        if self.media_type == "image" and not self.image:
            raise ValidationError("Image is required for image media type")
        if self.media_type == "video" and not self.media_url:
            raise ValidationError("Media URL is required for video media type")

    def is_recent(self):
        return (timezone.now() - self.created_at).days < 7

    @property
    def media_type_icon(self):
        icons = {
            "image": "fa-image",
            "video": "fa-video",
            "other": "fa-file",
        }
        return icons.get(self.media_type, "fa-question")


class AboutPage(models.Model):
    """Singleton model for editable About Us page content."""

    title = models.CharField(max_length=200, default="About Us")
    subtitle = models.CharField(max_length=300, blank=True)
    description = ProseEditorField(blank=True, extensions=_PROSE_EXTENSIONS, sanitize=True)
    image_1 = models.ImageField(
        upload_to="about/", blank=True, null=True, help_text="Primary about image"
    )
    image_2 = models.ImageField(
        upload_to="about/", blank=True, null=True, help_text="Secondary about image"
    )
    ceo_name = models.CharField(max_length=100, blank=True)
    ceo_title = models.CharField(max_length=100, blank=True)
    ceo_image = models.ImageField(upload_to="about/", blank=True, null=True)
    signature_image = models.ImageField(upload_to="about/", blank=True, null=True)
    highlight_1_title = models.CharField(
        max_length=100, blank=True, default="Super Quality Food"
    )
    highlight_1_description = models.CharField(max_length=255, blank=True)
    highlight_2_title = models.CharField(
        max_length=100, blank=True, default="Qualified Chef"
    )
    highlight_2_description = models.CharField(max_length=255, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "About Page"
        verbose_name_plural = "About Page"

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        with transaction.atomic():
            if not self.pk and AboutPage.objects.select_for_update().exists():
                existing = AboutPage.objects.select_for_update().first()
                self.pk = existing.pk
            super().save(*args, **kwargs)

    @classmethod
    def load(cls):
        with transaction.atomic():
            obj, _ = cls.objects.select_for_update().get_or_create(pk=1)
        return obj


class Event(models.Model):
    STATUS_UPCOMING = "upcoming"
    STATUS_ONGOING = "ongoing"
    STATUS_PAST = "past"
    STATUS_CANCELLED = "cancelled"

    STATUS_CHOICES = [
        (STATUS_UPCOMING, "Upcoming"),
        (STATUS_ONGOING, "Ongoing"),
        (STATUS_PAST, "Past"),
        (STATUS_CANCELLED, "Cancelled"),
    ]

    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=220, unique=True, blank=True)
    description = ProseEditorField(extensions=_PROSE_EXTENSIONS, sanitize=True)
    image = models.ImageField(
        upload_to="events/%Y/%m/",
        blank=True,
        null=True,
        help_text="Recommended size 800x500",
    )
    venue = models.CharField(max_length=200, blank=True, help_text="Specific venue")
    start_datetime = models.DateTimeField(help_text="Event start date & time")
    end_datetime = models.DateTimeField(
        null=True, blank=True, help_text="Event end date & time (optional)"
    )
    is_free = models.BooleanField(default=True)
    entry_fee = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Leave blank for free events",
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=STATUS_UPCOMING,
        db_index=True,
    )
    is_active = models.BooleanField(default=True)
    created_by = models.ForeignKey(
        "accounts.User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="events_created",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["start_datetime"]
        verbose_name_plural = "Events"
        indexes = [
            models.Index(fields=["status", "start_datetime"]),
            models.Index(fields=["is_active", "status"]),
        ]

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            base = slugify(self.title)
            slug = base
            counter = 1
            while Event.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)

    def auto_update_status(self):
        """Update status based on current time. Call from a management command or celery task."""
        now = timezone.now()
        if self.status == self.STATUS_CANCELLED:
            return
        if self.end_datetime and now > self.end_datetime:
            self.status = self.STATUS_PAST
        elif now >= self.start_datetime:
            self.status = self.STATUS_ONGOING
        elif now < self.start_datetime:
            self.status = self.STATUS_UPCOMING

    @property
    def computed_status(self):
        """Return real-time status derived from datetimes."""
        now = timezone.now()
        if self.status == self.STATUS_CANCELLED:
            return self.STATUS_CANCELLED
        if self.end_datetime and now > self.end_datetime:
            return self.STATUS_PAST
        if now >= self.start_datetime:
            return self.STATUS_ONGOING
        return self.STATUS_UPCOMING

    @property
    def is_upcoming(self):
        return self.computed_status == self.STATUS_UPCOMING

    @property
    def is_past(self):
        return self.computed_status == self.STATUS_PAST

    @property
    def formatted_date(self):
        return self.start_datetime.strftime("%b %d, %Y")

    @property
    def formatted_time(self):
        return self.start_datetime.strftime("%I:%M %p")


class SiteSettings(models.Model):
    """Singleton model for site-wide settings."""

    site_name = models.CharField(max_length=255, blank=True, null=True)
    support_email = models.EmailField(blank=True, null=True)
    support_phone = models.CharField(max_length=50, blank=True, null=True)
    whatsapp_number = models.CharField(max_length=50, blank=True, null=True)
    address = models.CharField(max_length=255, blank=True, null=True)
    working_hours = models.CharField(max_length=255, blank=True, null=True)
    facebook_url = models.URLField(blank=True, null=True)
    twitter_url = models.URLField(blank=True, null=True)
    instagram_url = models.URLField(blank=True, null=True)
    linkedin_url = models.URLField(blank=True, null=True)
    youtube_url = models.URLField(blank=True, null=True)

    class Meta:
        verbose_name = "Site Settings"
        verbose_name_plural = "Site Settings"

    def __str__(self):
        return self.site_name or "Site settings"

    def save(self, *args, **kwargs):
        with transaction.atomic():
            if not self.pk and SiteSettings.objects.select_for_update().exists():
                existing = SiteSettings.objects.select_for_update().first()
                self.pk = existing.pk
            super().save(*args, **kwargs)
        # Bust the context-processor cache so the next request picks up changes.
        cache.delete('site_settings')

    @classmethod
    def load(cls):
        with transaction.atomic():
            obj, _ = cls.objects.select_for_update().get_or_create(pk=1)
        return obj


class TeamMember(models.Model):
    name = models.CharField(max_length=100)
    role = models.CharField(max_length=100)
    image = models.ImageField(upload_to="team/")
    bio = models.TextField(blank=True)
    linkedin_url = models.URLField(blank=True)
    twitter_url = models.URLField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Team Member"
        verbose_name_plural = "Team Members"
        ordering = ["-created_at"]

    def __str__(self):
        return self.name


class SponsorshipTier(models.Model):
    name = models.CharField(max_length=50)
    price_display = models.CharField(max_length=100, blank=True)
    description = models.TextField()
    features = models.TextField(help_text="Enter each feature on a new line")
    is_recommended = models.BooleanField(default=False)
    icon_class = models.CharField(max_length=50, default="fas fa-gem")
    bg_class = models.CharField(max_length=50, blank=True, help_text="e.g. bronze-bg, silver-bg")
    order = models.IntegerField(default=0)
    
    class Meta:
        ordering = ['order']

    def __str__(self):
        return self.name

    @property
    def feature_list(self):
        return [f.strip() for f in self.features.split('\n') if f.strip()]


class SponsorshipInquiry(models.Model):
    STATUS_CHOICES = [
        ('new', 'New'),
        ('contacted', 'Contacted'),
        ('in_progress', 'In Progress'),
        ('closed', 'Closed'),
        ('rejected', 'Rejected'),
    ]

    company_name = models.CharField(max_length=200)
    contact_person = models.CharField(max_length=200)
    email = models.EmailField()
    whatsapp_number = models.CharField(max_length=25, blank=True)
    tier = models.ForeignKey(SponsorshipTier, on_delete=models.SET_NULL, null=True, blank=True)
    message = models.TextField(blank=True, help_text="Specific goals or in-kind details")
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='new', db_index=True)
    internal_notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = "Sponsorship Inquiries"

    def __str__(self):
        tier_name = self.tier.name if self.tier else "No Tier Selected"
        return f"{self.company_name} ({tier_name})"