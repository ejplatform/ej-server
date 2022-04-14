from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _


def is_not_empty(text):
    if not text.strip():
        raise ValidationError(_("Field cannot be empty!"))
