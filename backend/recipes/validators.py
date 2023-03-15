import re
import webcolors

from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError


MESSAGE_REGEX = 'Некорректные символы: {}'
USERNAME_REGEX = r'([-a-zA-Z0-9]+)'
MESSAGE_NO_COLOR_NAME = _('Для этого цвета нет имени')


def tag_regex_validator(value):
    invalid_simbols = ''.join(set(re.sub(USERNAME_REGEX, '', str(value))))
    if invalid_simbols:
        raise ValidationError(MESSAGE_REGEX.format(invalid_simbols))
    return value


def tag_color_validator(value):
    try:
        data = webcolors.hex_to_name(value)
    except ValueError:
        raise ValidationError(MESSAGE_NO_COLOR_NAME)
    return data
