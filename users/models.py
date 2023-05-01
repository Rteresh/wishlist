import random

from django.core.mail import send_mail
from django.db import models
from django.contrib.auth.models import AbstractUser, Group, Permission
from django.urls import reverse
from django.conf import settings
from django.utils.timezone import now
from django.utils.translation import gettext_lazy as _


# Create your models here.


class User(AbstractUser):
    image = models.ImageField(upload_to='user_images', blank=True, null=True)
    is_verified_email = models.BooleanField(default=False)
    email = models.EmailField(_('email address'), unique=True)
    is_matched = models.BooleanField(default=False)
    matched_user = models.OneToOneField('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='match')
    count_attempts_in_week = models.IntegerField(default=0)

    def __str__(self):
        return self.username

    def delete(self, *args, **kwargs):
        # обновляем поле is_matched у всех пользователей,
        # у которых matched_user равен удаляемому пользователю
        User.objects.filter(matched_user=self).update(is_matched=False)
        super().delete(*args, **kwargs)

    def active_wishes(self):
        from wish.models import ActiveWish
        return ActiveWish.objects.filter(user_to_execute_wish=self)


class EmailVerification(models.Model):
    code = models.UUIDField(unique=True)
    user = models.ForeignKey(to=User, on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True)
    expiration = models.DateTimeField()

    def __str__(self):
        return f'Email verification object for {self.user.email}'

    class Meta:
        verbose_name = 'Верификацию'
        verbose_name_plural = 'Верификация емейлов'

    def send_verification_email(self):
        link = reverse('users:email_verification', kwargs={'email': self.user.email,
                                                           'code': self.code})
        verification_link = f'{settings.DOMAIN_NAME}{link}'
        subject = f'Подтверждение учетной записи для {self.user.username}'
        message = f'Для подтверждения учетной записи для {self.user.username} перейдите по ссылке:{verification_link}'

        send_mail(
            subject=subject,
            message=message,
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[self.user.email],
            fail_silently=False,
        )

    def is_expired(self):
        return self.expiration <= now()


class UsersMatches(models.Model):
    user_main = models.ForeignKey(User, on_delete=models.CASCADE, related_name='matches_as_user1')
    user_requested = models.ForeignKey(User, on_delete=models.CASCADE, related_name='matches_as_user2')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user_main', 'user_requested')

    def __str__(self):
        return f"Пара {self.user_main.username} и  {self.user_requested.username}"


class RequestMatchVerification(models.Model):
    code = models.UUIDField(unique=True)
    main_user = models.ForeignKey(to=User, on_delete=models.CASCADE, related_name='main_user')
    requested_user = models.ForeignKey(to=User, on_delete=models.CASCADE, related_name='requested_user')
    created_at = models.DateTimeField(auto_now=True)
    expiration = models.DateTimeField()
    email_sent = models.BooleanField(default=False)

    def __str__(self):
        return f'Match verification object for {self.main_user} and {self.requested_user}'

    class Meta:
        verbose_name = 'Верификацию'
        verbose_name_plural = 'Создание пары'

    def send_email_to_response_match(self):
        link = reverse('users:match_verification', kwargs={'username': self.requested_user.username,
                                                           'code': self.code})
        verification_link = f'{settings.DOMAIN_NAME}{link}'
        subject = f'Подтверждение учетной записи для {self.requested_user.username}'
        message = f'Для подтверждения создания пары для пользователя ' \
                  f'{self.requested_user.username}  от пользователя' \
                  f'{self.main_user.username} ' \
                  f'перейдите по ссылке:{verification_link}'

        send_mail(
            subject=subject,
            message=message,
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[self.requested_user.email],
            fail_silently=False,
        )

        self.email_sent = True
        self.save()

    def is_expired(self):
        return self.expiration <= now()
