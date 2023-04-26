from django.http import HttpResponseRedirect, HttpResponseBadRequest
from django.shortcuts import render
from django.contrib.auth.views import TemplateView, LoginView
from django.urls import reverse_lazy, reverse
from django.views.generic.edit import CreateView
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib import messages

from users.models import User, EmailVerification, RequestMatchVerification
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


class UserMatchVerificationView(TemplateView):
    template_name = 'wish/test.html'

    def get(self, request, *args, **kwargs):
        if 'code' not in kwargs:
            return HttpResponseBadRequest('Missing required parameter "code"')

        code = kwargs['code']
        try:
            match_request_verification = RequestMatchVerification.objects.get(code=code)
        except RequestMatchVerification.DoesNotExist:
            return HttpResponseBadRequest('Invalid code')

        if match_request_verification is not None and not match_request_verification.is_expired():
            user1 = match_request_verification.requested_user
            user2 = match_request_verification.main_user
            print('Welcome!')

        return super().get(request, *args, **kwargs)
