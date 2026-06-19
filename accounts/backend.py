import logging

from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend
from django.db.models import Q

logger = logging.getLogger(__name__)

UserModel = get_user_model()


class EmailBackend(ModelBackend):
    """Allow login with either username or email (case-insensitive)."""

    def authenticate(self, request, username=None, password=None, **kwargs):
        if username is None or password is None:
            return None

        try:
            user = UserModel.objects.get(
                Q(username__iexact=username) | Q(email__iexact=username)
            )
        except UserModel.DoesNotExist:
            return None
        except UserModel.MultipleObjectsReturned:
            # Should never happen given DB constraints, but must not silently
            # pick the wrong account — log and refuse rather than guess.
            logger.warning(
                "Multiple users matched login identifier — login refused. "
                "Add a case-insensitive unique constraint on username."
            )
            return None

        if user.check_password(password) and self.user_can_authenticate(user):
            return user

        return None
