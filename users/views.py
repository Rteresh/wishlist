from django.http import HttpResponseRedirect, HttpResponseBadRequest
from django.shortcuts import render
from django.contrib.auth.views import TemplateView, LoginView
from django.urls import reverse_lazy, reverse
from django.views.generic.edit import CreateView
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib import messages

from users.models import User, EmailVerification, RequestMatchVerification, UsersMatches
from users.forms import UserRegistrationForm, UserAuthForm


# Create your views here.

class UsersRegistrationView(SuccessMessageMixin, CreateView):
    template_name = 'users/register.html'
    model = User
    form_class = UserRegistrationForm
    success_url = reverse_lazy('users:login')
    success_message = 'Вы успешно зарегистрировались'


class UserLoginView(LoginView):
    template_name = 'users/login.html'
    form_class = UserAuthForm
    tittle = 'Login'


class EmailVerificationView(SuccessMessageMixin, TemplateView):
    tittle = 'Верификация почты'
    template_name = 'users/email_verification.html'

    def get(self, request, *args, **kwargs):
        code = kwargs['code']
        user = User.objects.get(email=kwargs['email'])
        email_verifications = EmailVerification.objects.filter(user=user, code=code)
        if email_verifications.exists() and not email_verifications.first().is_expired():
            if user.is_verified_email:
                messages.success(request, 'Вы уже верифицированы')
                return HttpResponseRedirect(reverse('users:login'))
            user.is_verified_email = True
            user.save()
            # Из-за того, что мы переписали метод гет. Необходимо, чтобы он вернулся в исходное положение
            return super().get(request, *args, **kwargs)
        else:
            return HttpResponseRedirect(reverse('index'))


def user_change(main_user, matched_user):
    """Функция user_change принимает два аргумента: main_user (пользователь, который запросил соответствие) и
    matched_user (пользователь, с которым он совпал). Функция устанавливает флаг is_matched пользователя main_user в
    значение True и сохраняет его в базе данных. Также сохраняется ссылка на matched_user в поле matched_user объекта
    main_user.
"""
    main_user.is_matched = True
    main_user.matched_user = matched_user
    main_user.save()


class UserMatchVerificationView(TemplateView):
    """
      View class that handles the user match verification process. When a user clicks on the link in their email, they are
      directed to this view. It checks the validity of the verification code in the URL, and if it is valid and not expired,
      the two users are matched, and their information is stored in the database.
      """
    template_name = 'wish/test.html'

    def get(self, request, *args, **kwargs):
        """
                Handle GET requests to the view.

                Parameters:
                    request (HttpRequest): The HTTP request object.
                    args: Additional arguments.
                    kwargs: Additional keyword arguments.

                Returns:
                    HttpResponse: The HTTP response object.
                """
        if 'code' not in kwargs:
            return HttpResponseBadRequest('Missing required parameter "code"')

        code = kwargs['code']
        try:
            match_request_verification = RequestMatchVerification.objects.get(code=code)
        except RequestMatchVerification.DoesNotExist:
            return HttpResponseBadRequest('Invalid code')

        if match_request_verification is not None and not match_request_verification.is_expired():
            user1 = match_request_verification.main_user
            user2 = match_request_verification.requested_user

            UsersMatches.objects.create(user_main=user1, user_requested=user2)

            user_change(main_user=user1, matched_user=user2)
            user_change(main_user=user2, matched_user=user1)
        return super().get(request, *args, **kwargs)
