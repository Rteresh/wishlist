import uuid
from datetime import timedelta

from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserChangeForm, UserCreationForm
from django.core.exceptions import ValidationError
from django.utils.timezone import now

from users.models import User, EmailVerification, UsersMatches, RequestMatchVerification


class UserAuthForm(AuthenticationForm):
    """Форма ацетификации пользователя"""
    username = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-control py-4',
        'placeholder': 'Введите имя пользователя'
    }))
    password = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'form-control py-4',
        'placeholder': 'Введите ваш пароль'
    }))

    class Meta:
        model = User
        fields = (
            'username',
            'password'
        )


class UserRegistrationForm(UserCreationForm):
    """Форма регистрации пользователя"""
    first_name = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-control py-4',
        'placeholder': 'Введите имя'
    }))
    last_name = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-control py-4',
        'placeholder': 'Введите фамилию'
    }))
    username = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-control py-4',
        'placeholder': 'Введите имя пользователя'
    }))
    email = forms.CharField(widget=forms.EmailInput(attrs={
        'class': 'form-control py-4',
        'placeholder': 'Введите адрес эл.почты'
    }))
    password1 = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-control py-4',
        'placeholder': 'Введите пароль'
    }))
    password2 = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-control py-4',
        'placeholder': 'Подтвердите пароль'
    }))

    class Meta:
        model = User
        fields = (
            'first_name',
            'last_name',
            'username',
            'email',
            'password1',
            'password2'
        )

    def save(self, commit=True):
        """Отправка запроса на эл.почту и создание записи для верификации эл.почты"""

        user = super().save(commit=True)
        # email verification
        expiration = now() + timedelta(hours=48)
        record = EmailVerification.objects.create(code=uuid.uuid4(), user=user, expiration=expiration)
        record.send_verification_email()
        return user


class MatchForm(forms.Form):
    """Определяет форму для запроса на соответствие (match request) между пользователями и отправляет письмо для
    подтверждения запроса на почту"""
    username = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-control py-4',
        'placeholder': 'Введите имя пользователя'
    }))

    def send_email_and_create_record(self, user):
        """Отправка запроса на эл.почту и создание записи для верификации запроса на создании пары"""

        username = self.cleaned_data['username']
        requested_user = User.objects.filter(username=username).first()
        if not requested_user:
            message = 'Пользователь с указанным именем не существует'
            return False, message
        if user == requested_user:
            message = 'Вы не можете запросить соответствие сами с собой'
            return False, message
        if requested_user.is_matched:
            message = 'Это пользователь уже состоит в паре'
            return False, message
        if not requested_user.is_verified_email:
            message = 'Этот пользователь не верифицирован'
            return False, message

        expiration = now() + timedelta(hours=48)
        record = RequestMatchVerification.objects.create(
            code=uuid.uuid4(),
            main_user=user,
            requested_user=requested_user,
            expiration=expiration
        )
        record.send_email_to_response_match()
        message = 'Запрос отправлен успешно'
        return True, message
