from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator


class User(AbstractUser):

    username = models.CharField(
        verbose_name='Имя пользователя',
        max_length=150,
        blank=False,
        unique=True,
        validators=[RegexValidator(
            regex=r'^[\w.@+-]+$',
            message='Имя пользователя содержит недопустимые символы'
        )]
    )
    first_name = models.CharField(
        verbose_name='Имя',
        max_length=150,
        blank=True,
    )
    last_name = models.CharField(
        verbose_name='Фамилия',
        max_length=150,
        blank=True,
    )
    email = models.EmailField(
        verbose_name='Адрес электронной почты',
        max_length=254,
        blank=False,
        unique=True,
    )
    password = models.CharField(
        verbose_name="Пароль",
        max_length=150,
    )

    class Meta:
        ordering = ['id']
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return self.username


class Subscribe(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE, null=True, blank=True,
        related_name='follower'
    )
    following = models.ForeignKey(
        User,
        on_delete=models.CASCADE, null=True, blank=True,
        related_name='following'
    )

    class Meta:
        ordering = ['following']
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'

        constraints = (
            models.UniqueConstraint(
                fields=('user', 'following'),
                name='unique_subscribe'
            ),
        )

    def __str__(self):
        return f'Пользователь {self.user} подписан на {self.following}'
