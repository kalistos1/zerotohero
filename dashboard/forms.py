from django import forms

from blog.models import BlogCategory, Post
from core.models import (
    FAQ,
    AboutPage,
    Event,
    Gallery,
    GalleryCategory,
    Testimonial,
    TeamMember,
    MentorshipApplication,
)


class FAQForm(forms.ModelForm):
    class Meta:
        model = FAQ
        fields = ["question", "answer", "is_active"]
        widgets = {
            "question": forms.TextInput(attrs={"class": "form-control"}),
            "is_active": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }

    # tags handled separately — django-taggit field is not a standard form field


class TestimonialForm(forms.ModelForm):
    class Meta:
        model = Testimonial
        fields = [
            "name", "role", "image",
            "rating", "media_type",
            "review_text", "chat_screenshot", "video_file",
            "is_active",
        ]
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control"}),
            "role": forms.TextInput(attrs={"class": "form-control"}),
            "image": forms.ClearableFileInput(attrs={"class": "form-control"}),
            "rating": forms.NumberInput(attrs={"class": "form-control", "min": 1, "max": 5}),
            "media_type": forms.Select(attrs={"class": "form-select", "id": "id_media_type"}),
            "chat_screenshot": forms.ClearableFileInput(attrs={"class": "form-control"}),
            "video_file": forms.ClearableFileInput(attrs={"class": "form-control"}),
            "is_active": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }
        labels = {
            "image": "Profile Photo",
            "chat_screenshot": "Chat / DM Screenshot",
            "video_file": "Video File (MP4 recommended)",
            "review_text": "Text Review",
        }
        help_texts = {
            "media_type": "Select how this testimonial will be displayed on the site.",
            "review_text": "Required for 'Text Review'. Optional caption for Screenshot/Video types.",
            "chat_screenshot": "Required for 'Chat Screenshot' type. Upload the screenshot image.",
            "video_file": "Required for 'Video Testimonial' type. Keep under 50 MB.",
        }


class AboutPageForm(forms.ModelForm):
    class Meta:
        model = AboutPage
        fields = [
            "title",
            "subtitle",
            "description",
            "image_1",
            "image_2",
            "ceo_name",
            "ceo_title",
            "ceo_image",
            "signature_image",
            "highlight_1_title",
            "highlight_1_description",
            "highlight_2_title",
            "highlight_2_description",
        ]
        widgets = {
            "title": forms.TextInput(attrs={"class": "form-control"}),
            "subtitle": forms.TextInput(attrs={"class": "form-control"}),
            "image_1": forms.ClearableFileInput(attrs={"class": "form-control"}),
            "image_2": forms.ClearableFileInput(attrs={"class": "form-control"}),
            "ceo_name": forms.TextInput(attrs={"class": "form-control"}),
            "ceo_title": forms.TextInput(attrs={"class": "form-control"}),
            "ceo_image": forms.ClearableFileInput(attrs={"class": "form-control"}),
            "signature_image": forms.ClearableFileInput(attrs={"class": "form-control"}),
            "highlight_1_title": forms.TextInput(attrs={"class": "form-control"}),
            "highlight_1_description": forms.TextInput(attrs={"class": "form-control"}),
            "highlight_2_title": forms.TextInput(attrs={"class": "form-control"}),
            "highlight_2_description": forms.TextInput(attrs={"class": "form-control"}),
        }


class EventForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = [
            "title",
            "description",
            "image",
            "venue",
            "start_datetime",
            "end_datetime",
            "is_free",
            "entry_fee",
            "status",
            "is_active",
        ]
        widgets = {
            "title": forms.TextInput(attrs={"class": "form-control"}),
            "image": forms.ClearableFileInput(attrs={"class": "form-control"}),
            "venue": forms.TextInput(attrs={"class": "form-control"}),
            "start_datetime": forms.DateTimeInput(
                attrs={"class": "form-control", "type": "datetime-local"},
                format="%Y-%m-%dT%H:%M",
            ),
            "end_datetime": forms.DateTimeInput(
                attrs={"class": "form-control", "type": "datetime-local"},
                format="%Y-%m-%dT%H:%M",
            ),
            "is_free": forms.CheckboxInput(attrs={"class": "form-check-input"}),
            "entry_fee": forms.NumberInput(attrs={"class": "form-control", "min": "0", "step": "0.01"}),
            "status": forms.Select(attrs={"class": "form-select"}),
            "is_active": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }


class GalleryCategoryForm(forms.ModelForm):
    class Meta:
        model = GalleryCategory
        fields = ["name", "description", "is_active"]
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control"}),
            "description": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
            "is_active": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }


class GalleryItemForm(forms.ModelForm):
    class Meta:
        model = Gallery
        fields = ["title", "caption", "media_type", "image", "media_url", "category", "alt_text", "position", "is_active"]
        widgets = {
            "title": forms.TextInput(attrs={"class": "form-control"}),
            "caption": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
            "media_type": forms.Select(attrs={"class": "form-select"}),
            "image": forms.ClearableFileInput(attrs={"class": "form-control"}),
            "media_url": forms.URLInput(attrs={"class": "form-control", "placeholder": "https://..."}),
            "category": forms.Select(attrs={"class": "form-select"}),
            "alt_text": forms.TextInput(attrs={"class": "form-control"}),
            "position": forms.NumberInput(attrs={"class": "form-control", "min": 0}),
            "is_active": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }


class BlogPostForm(forms.ModelForm):
    class Meta:
        model = Post
        # author, slug, thumbnail set in the view — not exposed to the user
        fields = ["title", "body", "image", "status", "category"]
        widgets = {
            "title": forms.TextInput(attrs={"class": "form-control"}),
            "image": forms.ClearableFileInput(attrs={"class": "form-control"}),
            "status": forms.Select(attrs={"class": "form-select"}),
            "category": forms.Select(attrs={"class": "form-select"}),
        }


class BlogCategoryForm(forms.ModelForm):
    class Meta:
        model = BlogCategory
        # slug auto-generated in model.save()
        fields = ["name", "parent"]
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control"}),
            "parent": forms.Select(attrs={"class": "form-select"}),
        }


class TeamMemberForm(forms.ModelForm):
    class Meta:
        model = TeamMember
        fields = [
            "name",
            "role",
            "image",
            "bio",
            "linkedin_url",
            "twitter_url",
            "is_active",
        ]
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control"}),
            "role": forms.TextInput(attrs={"class": "form-control"}),
            "image": forms.ClearableFileInput(attrs={"class": "form-control"}),
            "bio": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
            "linkedin_url": forms.URLInput(attrs={"class": "form-control", "placeholder": "https://linkedin.com/in/..."}),
            "twitter_url": forms.URLInput(attrs={"class": "form-control", "placeholder": "https://twitter.com/..."}),
            "is_active": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }


class MentorshipAdminReviewForm(forms.ModelForm):
    class Meta:
        model = MentorshipApplication
        fields = ["status", "internal_score", "admin_notes"]
        
    def clean_internal_score(self):
        score = self.cleaned_data.get("internal_score", 0)
        if score is not None and not (0 <= score <= 5):
            raise forms.ValidationError("Score must be between 0 and 5.")
        return score
        
    def clean_admin_notes(self):
        notes = self.cleaned_data.get("admin_notes", "")
        if len(notes) > 5000:
            raise forms.ValidationError("Admin notes cannot exceed 5000 characters.")
        return notes
