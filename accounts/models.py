import uuid

from django.contrib.auth.models import AbstractUser
from django.core.validators import MinLengthValidator, RegexValidator
from django.db import models
from django.utils import timezone

from core.validators import validate_image_upload


class User(AbstractUser):
    email = models.EmailField(unique=True)
    phone = models.CharField(
        max_length=20,
        null=True,
        blank=True,
        validators=[
            RegexValidator(
                r"^\+?[0-9\s\-]{7,20}$",
                "Enter a valid phone number (e.g. +2348012345678).",
            )
        ],
    )
    is_admin = models.BooleanField(default=False)
    is_mentor = models.BooleanField(default=False)
    is_mentee = models.BooleanField(default=False)
    accepted_terms = models.BooleanField(default=False)
    is_verified = models.BooleanField(default=False)
    profile_completed = models.BooleanField(default=False)

    class Meta:
        indexes = [
            models.Index(fields=["username"]),
            models.Index(fields=["email"]),
        ]

    def __str__(self):
        return self.username

    @property
    def is_registered_user(self):
        """Check if user has a registered profile."""
        return hasattr(self, "profile") and hasattr(self.profile, "registeredprofile")

    @property
    def registeredprofile(self):
        """Return the registered profile if it exists."""
        try:
            return self.profile.registeredprofile
        except AttributeError:
            return None


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    profile_picture = models.ImageField(
        upload_to="profiles",
        blank=True,
        null=True,
        validators=[validate_image_upload],
    )
    date_of_birth = models.DateField(null=True, blank=True)
    gender = models.CharField(
        max_length=10,
        choices=[("Male", "Male"), ("Female", "Female")],
        null=True,
        blank=True,
    )
    address = models.TextField(null=True, blank=True)
    nationality = models.CharField(max_length=100, null=True, blank=True)
    state_of_origin = models.CharField(max_length=100, null=True, blank=True)
    current_city = models.CharField(max_length=100, null=True, blank=True)
    current_state = models.CharField(max_length=100, null=True, blank=True)

    class Meta:
        db_table = "profiles"
        verbose_name = "profile"
        verbose_name_plural = "profiles"

    def __str__(self):
        return self.user.username

    @property
    def age(self):
        if self.date_of_birth:
            today = timezone.now().date()
            return (
                today.year
                - self.date_of_birth.year
                - (
                    (today.month, today.day)
                    < (self.date_of_birth.month, self.date_of_birth.day)
                )
            )
        return None


class TempUrl(models.Model):
    url_hash = models.CharField("Url", blank=False, max_length=64, unique=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    date_created = models.DateTimeField(auto_now_add=True)
    expires = models.DateTimeField("Expires")

    class Meta:
        db_table = "temp_urls"

    def __str__(self):
        return f"{self.url_hash} ({self.user})"


class Ticket(models.Model):
    STATUS_CHOICES = [
        ("OPEN", "Open"),
        ("IN_PROGRESS", "In Progress"),
        ("RESOLVED", "Resolved"),
        ("CLOSED", "Closed"),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="tickets")
    ticket_id = models.CharField(max_length=30, unique=True, editable=False)
    subject = models.CharField(max_length=200, validators=[MinLengthValidator(5)])
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="OPEN")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    assigned_to = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        limit_choices_to=(models.Q(is_admin=True) | models.Q(is_mentor=True)),
        related_name="assigned_tickets",
    )

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["status"]),
            models.Index(fields=["created_at"]),
            models.Index(fields=["user"]),
        ]

    def __str__(self):
        return f"{self.ticket_id} - {self.subject}"

    def save(self, *args, **kwargs):
        if not self.ticket_id:
            now = timezone.now()
            self.ticket_id = (
                f"TICKET-{now.strftime('%Y%m%d')}-{uuid.uuid4().hex[:8].upper()}"
            )
        super().save(*args, **kwargs)


class Message(models.Model):
    ticket = models.ForeignKey(
        Ticket, on_delete=models.CASCADE, related_name="messages"
    )
    sender = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="sent_messages"
    )
    content = models.TextField(validators=[MinLengthValidator(1)])
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)
    parent = models.ForeignKey(
        "self",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="replies",
    )

    class Meta:
        ordering = ["created_at"]
        indexes = [
            models.Index(fields=["ticket", "is_read"]),
            models.Index(fields=["created_at"]),
            models.Index(fields=["sender"]),
        ]

    def __str__(self):
        return f"Message in {self.ticket.ticket_id} at {self.created_at}"
