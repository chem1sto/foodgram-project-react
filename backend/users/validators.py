import re

from django.core.exceptions import ValidationError


MESSAGE_REGEX = 'Некорректные символы: {}'
USERNAME_REGEX = r'([\w.@+-]+)'


def regex_validator(value):
    invalid_simbols = ''.join(set(re.sub(USERNAME_REGEX, '', str(value))))
    if invalid_simbols:
        raise ValidationError(MESSAGE_REGEX.format(invalid_simbols))
    return value
