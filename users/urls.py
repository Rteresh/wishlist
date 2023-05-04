"""wishlist URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LogoutView
from django.urls import path

from users.views import UsersRegistrationView, UserLoginView, EmailVerificationView, UserMatchVerificationView, \
    ProfileVIew

app_name = 'users'

urlpatterns = [
    path('registration/', UsersRegistrationView.as_view(), name='registration'),
    path('login/', UserLoginView.as_view(), name='login'),
    path('verify/<str:email>/<uuid:code>', EmailVerificationView.as_view(), name="email_verification"),
    path('match/<str:username>/<uuid:code>', UserMatchVerificationView.as_view(), name="match_verification"),
    path('logout/', LogoutView.as_view(), name="logout"),
    path('profile/<int:pk>', login_required(ProfileVIew.as_view()), name='profile'),

]
