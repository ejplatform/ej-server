from django.core.exceptions import ValidationError

from ej_configurations.validators import validate_icon_name

INVALID_FA_ICON_NAME_MSG = [
    'Invalid font awesome icon name. Please use the full format like '
    'in "fab fa-facebook-f"'
]

INVALID_FA_ICON_MSG = [
    'fa fa-test is an invalid Icones Font-awesome icon!'
]


def test_invalid_fa_icon_name():
    try:
        validate_icon_name('invalid_icon_name')
    except ValidationError as e:
        assert e.messages == INVALID_FA_ICON_NAME_MSG


def test_non_existent_fa_icon():
    try:
        validate_icon_name('fa fa-test')
    except ValidationError as e:
        assert e.messages == INVALID_FA_ICON_MSG
