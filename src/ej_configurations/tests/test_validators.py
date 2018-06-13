import pytest
from django.core.exceptions import ValidationError

from ej_configurations.validators import validate_icon_name


def test_invalid_fa_icon_name():
    with pytest.raises(ValidationError):
        validate_icon_name('invalid_icon_name')


def test_non_existent_fa_icon():
    with pytest.raises(ValidationError):
        validate_icon_name('fa fa-test')
