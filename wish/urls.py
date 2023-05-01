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
from django.urls import path

from wish.views import IndexView, MatchFormView, MakeWishList, create_active_wish, complete_wish, checkout_wish

app_name = 'wish'

urlpatterns = [
    # Wish
    path('', MatchFormView.as_view(), name='wishes'),
    path('makewish', MakeWishList.as_view(), name='wish_list'),
    path('active_wish', create_active_wish, name='active_wish'),
    path('complete_wish', complete_wish, name='complete_wish'),
    path('checkout_wish', checkout_wish, name='checkout_wish'),
]
