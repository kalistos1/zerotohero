"""
Reusable file upload validators for the Zero to Hero platform.
Enforces extension, content-type, and size limits on all uploaded files.
"""
from django.core.exceptions import ValidationError
import filetype

ALLOWED_IMAGE_EXTENSIONS = {'jpg', 'jpeg', 'png', 'webp', 'gif'}
ALLOWED_IMAGE_CONTENT_TYPES = {
    'image/jpeg', 'image/png', 'image/webp', 'image/gif',
}
MAX_IMAGE_SIZE = 5 * 1024 * 1024   # 5 MB

ALLOWED_VIDEO_EXTENSIONS = {'mp4', 'webm', 'ogg', 'mov'}
ALLOWED_VIDEO_CONTENT_TYPES = {
    'video/mp4', 'video/webm', 'video/ogg', 'video/quicktime',
}
MAX_VIDEO_SIZE = 50 * 1024 * 1024  # 50 MB


def validate_image_upload(file):
    """Validate that an uploaded file is a legitimate image within size limits."""
    if not file:
        return

    if file.size > MAX_IMAGE_SIZE:
        raise ValidationError(
            f"File size cannot exceed 5MB. Current size: {file.size / (1024 * 1024):.1f}MB"
        )

    ext = file.name.rsplit('.', 1)[-1].lower() if '.' in file.name else ''
    if ext not in ALLOWED_IMAGE_EXTENSIONS:
        raise ValidationError(
            f"Unsupported file type '.{ext}'. Allowed types: {', '.join(sorted(ALLOWED_IMAGE_EXTENSIONS))}"
        )

    if hasattr(file, 'content_type') and file.content_type not in ALLOWED_IMAGE_CONTENT_TYPES:
        raise ValidationError(
            f"Invalid file content type '{file.content_type}'. Only image files are allowed."
        )

    file.seek(0)
    kind = filetype.guess(file.read(2048))
    mime = kind.mime if kind else None
    file.seek(0)
    if mime not in ALLOWED_IMAGE_CONTENT_TYPES:
        raise ValidationError(f"Invalid file content type '{mime}'. Only image files are allowed.")


def validate_video_upload(file):
    """Validate that an uploaded file is a legitimate video within size limits.

    """
    if not file:
        return

    if file.size > MAX_VIDEO_SIZE:
        raise ValidationError(
            f"Video file must be under 50MB. Current size: {file.size / (1024 * 1024):.1f}MB"
        )

    ext = file.name.rsplit('.', 1)[-1].lower() if '.' in file.name else ''
    if ext not in ALLOWED_VIDEO_EXTENSIONS:
        raise ValidationError(
            f"Unsupported video type '.{ext}'. Allowed types: {', '.join(sorted(ALLOWED_VIDEO_EXTENSIONS))}"
        )

    if hasattr(file, 'content_type') and file.content_type not in ALLOWED_VIDEO_CONTENT_TYPES:
        raise ValidationError(
            f"Invalid content type '{file.content_type}'. Only video files are allowed."
        )

    file.seek(0)
    kind = filetype.guess(file.read(2048))
    mime = kind.mime if kind else None
    file.seek(0)
    if mime not in ALLOWED_VIDEO_CONTENT_TYPES:
        raise ValidationError(f"Invalid file content type '{mime}'. Only video files are allowed.")