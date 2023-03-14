from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _

from .validators import regex_validator


USER = 'user'
ADMIN = 'admin'

ROLES = (
    (USER, 'Пользователь'),
    (ADMIN, 'Администратор'),
)


class CustomUser(AbstractUser):
    """Кастомная модель User."""
    username = models.CharField(
        verbose_name=_('username'),
        max_length=settings.USERNAME_LENGTH,
        validators=(regex_validator,),
        unique=True
    )
    email = models.EmailField(
        verbose_name=_('email'),
        max_length=settings.EMAIL_LENGTH,
    )
    role = models.CharField(
        verbose_name=_('роль'),
        choices=ROLES,
        max_length=max(len(role) for role, _ in ROLES),
        default=USER
    )

    class Meta(AbstractUser.Meta):
        ordering = ('username',)

    def __str__(self):
        return self.username

    @property
    def is_admin(self):
        return self.is_staff or self.role == ADMIN


class Subscription(models.Model):
    subscriber = models.ForeignKey(
        verbose_name=_('подписчик'),
        to=CustomUser,
        on_delete=models.CASCADE,
        related_name='subscriber'
    )
    subscribing = models.ForeignKey(
        verbose_name=_('подписка'),
        to=CustomUser,
        on_delete=models.CASCADE,
        related_name='subscribing'
    )
    add_date = models.DateTimeField(
        verbose_name=_('дата добавления'),
        auto_now_add=True
    )

    class Meta:
        verbose_name = _('подписка')
        verbose_name_plural = _('подписки')
        ordering = ('-add_date',)
        constraints = [
            models.UniqueConstraint(
                fields=['subscriber', 'subscribing'], name='unique_subscribing'
            )
        ]
