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
    wish_history = models.JSONField(default=list, null=True)
    wish_executed = models.JSONField(default=list, null=True)

    def __str__(self):
        return self.username

    def delete(self, *args, **kwargs):
        # обновляем поле is_matched у всех пользователей,
        # у которых matched_user равен удаляемому пользователю
        User.objects.filter(matched_user=self).update(is_matched=False)
        super().delete(*args, **kwargs)

    def get_active_wishes(self):
        from wish.models import ActiveWish
        return ActiveWish.objects.filter(executor=self)


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

    def is_expired_email_verification(self):
        return self.expiration <= now()


class MatchPair(models.Model):
    user1 = models.ForeignKey(User, on_delete=models.CASCADE, related_name='match_pair')
    user2 = models.ForeignKey(User, on_delete=models.CASCADE, )
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user1', 'user2')

    def __str__(self):
        return f"Пара между пользователем:{self.user1.username} и пользователем:{self.user2.username}"

    def delete(self, *args, **kwargs):
        # меняем состояние у пользователей, если они существуют
        try:
            self.user1.is_matched = False
            self.user1.matched_user = None
            self.user1.save()
            if self.user1.get_active_wishes():
                self.user1.get_active_wishes().delete()

        except User.DoesNotExist:
            pass

        try:
            self.user2.is_matched = False
            self.user2.matched_user = None
            self.user2.save()
            if self.user2.get_active_wishes():
                self.user2.get_active_wishes().delete()
        except User.DoesNotExist:
            pass

        super().delete(*args, **kwargs)


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

    def send_verification_email(self):
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

    def is_expired_email_verification(self):
        return self.expiration <= now()
