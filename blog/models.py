import contextlib
from io import BytesIO

from django.core.files import File
from django.core.validators import MaxLengthValidator
from django.db import models
from django.utils.html import strip_tags
from django.utils.text import slugify
from django_prose_editor.fields import ProseEditorField

from PIL import Image
from taggit.managers import TaggableManager

from accounts.models import User
from core.models import _PROSE_EXTENSIONS
from core.validators import validate_image_upload


class BlogCategory(models.Model):
    name = models.CharField(max_length=250)
    slug = models.SlugField()
    parent = models.ForeignKey(
        "self",
        blank=True,
        null=True,
        related_name="children",
        on_delete=models.SET_NULL,
    )

    class Meta:
        unique_together = ("slug", "parent")
        verbose_name_plural = "blog_categories"
        db_table = "blog_categories"

    def __str__(self):
        full_path = [self.name]
        parent_cat = self.parent
        depth = 0
        while parent_cat is not None and depth < 10:
            full_path.append(parent_cat.name)
            parent_cat = parent_cat.parent
            depth += 1
        if parent_cat is not None:
            full_path.append('...')
        return " -> ".join(full_path[::-1])

    def save(self, *args, **kwargs):
        if not self.slug:
            base = slugify(self.name, allow_unicode=True)
            slug = base
            counter = 1
            while (
                BlogCategory.objects.filter(slug=slug, parent=self.parent)
                .exclude(pk=self.pk)
                .exists()
            ):
                slug = f"{base}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)


class Post(models.Model):
    STATUS_CHOICES = [
        ("DRAFT", "Draft"),
        ("PUBLISHED", "Published"),
        ("ARCHIVED", "Archived"),
    ]

    author = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=250)
    body = ProseEditorField(
        extensions=_PROSE_EXTENSIONS,
        sanitize=True,
    )


    slug = models.SlugField(unique=True)
    image = models.ImageField(
        null=True,
        blank=True,
        upload_to="post_images",
        validators=[validate_image_upload],
    )
    thumbnail = models.ImageField(
        blank=True,
        null=True,
        upload_to="post_images/",
        validators=[validate_image_upload],
    )
    tags = TaggableManager()
    # ── SEO fields ────────────────────────────────────────────────────────────
    seo_title = models.CharField(
        max_length=70,
        blank=True,
        help_text="Optional. Overrides the page &lt;title&gt;. Recommended max 60 characters.",
    )
    meta_description = models.CharField(
        max_length=165,
        blank=True,
        help_text="Optional. Overrides the meta description. Recommended max 155 characters.",
    )
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default="DRAFT",
        db_index=True,
        help_text="Only published posts are visible to the public",
    )
    category = models.ForeignKey(
        BlogCategory,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )
    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "posts"
        db_table = "posts"
        ordering = ["-date_created"]
        indexes = [
            models.Index(fields=["date_created"]),
            models.Index(fields=["author"]),
            models.Index(fields=["category"]),
            models.Index(fields=["status"]),
            models.Index(fields=["status", "date_created"]),
        ]

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            base = slugify(self.title, allow_unicode=True)
            slug = base
            counter = 1
            while Post.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base}-{counter}"
                counter += 1
            self.slug = slug

        if self.image and not self.thumbnail:
            with contextlib.suppress(Exception):
                self.thumbnail = self._make_thumbnail(self.image)

        super().save(*args, **kwargs)

    def snippet(self):
        """Return a plain-text preview of the post body."""
        plain_text = strip_tags(self.body)
        if len(plain_text) > 150:
            return plain_text[:150] + "..."
        return plain_text

    def get_cat_list(self):
        parent_cat = self.category
        breadcrumb = ["dummy"]
        while parent_cat is not None:
            breadcrumb.append(parent_cat.slug)
            parent_cat = parent_cat.parent

        for i in range(len(breadcrumb) - 1):
            breadcrumb[i] = "/".join(breadcrumb[-1 : i - 1 : -1])
        return breadcrumb[-1:0:-1]

    def get_imagethumbnail(self):
        """Return the thumbnail URL, the main image URL, or a static fallback."""
        if self.thumbnail:
            return self.thumbnail.url
        if self.image:
            return self.image.url
        return "/static/images/default-post.jpg"

    @staticmethod
    def _make_thumbnail(image, size=(300, 300)):
        """Create a JPEG thumbnail from the given image."""
        image.seek(0)
        img = Image.open(image)
        img = img.convert("RGB")
        img.thumbnail(size)

        thumb_io = BytesIO()
        img.save(thumb_io, "JPEG", quality=85)
        return File(thumb_io, name=image.name)


class Comment(models.Model):
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="blog_comments",
    )
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="comments")
    text = models.TextField(validators=[MaxLengthValidator(5000)])
    date_created = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "comments"
        db_table = "comments"
        ordering = ("-date_created",)

    def __str__(self):
        return self.text[:10]
