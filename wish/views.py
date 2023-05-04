import random
from datetime import timedelta

from django.contrib.auth.decorators import login_required
from django.contrib.messages.views import SuccessMessageMixin
from django.http import HttpResponseRedirect
from django.shortcuts import render, reverse
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import TemplateView, FormView
from django.contrib import messages
from django.db.models import Q
from django.utils.timezone import now

from users.models import User, UsersMatches
from users.forms import MatchForm

from wish.forms import WishForm
from wish.models import Wish, ActiveWish, HistoryExecutionWishes


# Create your views here.


class IndexView(TemplateView):
    template_name = 'wish/index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        context['users'] = User.objects.all()
        return context


class ActiveWishView(TemplateView):
    template_name = 'wish/active_wish.html'

    def dispatch(self, request, *args, **kwargs):
        if request.user.id != self.kwargs['pk']:
            print(self.kwargs['pk'])
            # If the user is not accessing their own profile, redirect them to the login page
            return HttpResponseRedirect(reverse_lazy('wish:profile', args=(request.user.id,)))

        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)  # Include the **kwargs argument
        user_id = self.kwargs['pk']
        user = User.objects.get(id=user_id)
        context['history'] = HistoryExecutionWishes.objects.filter(user_to_execute_wish=user)
        return context


class MatchFormView(SuccessMessageMixin, FormView):
    template_name = 'wish/succes_match.html'
    form_class = MatchForm
    success_url = reverse_lazy('wish:wishes')

    def form_valid(self, form):
        user = User.objects.get(id=self.request.user.id)
        if not user.is_matched:
            success, message = form.send_email_and_create_record(user)
            if success:
                messages.success(self.request, message)
            else:
                messages.warning(self.request, message)
        else:
            messages.warning(self.request, 'Вы уже состоите в паре ')
        return super().form_valid(form)


class MakeWishList(FormView):
    template_name = 'wish/make_wish_list.html'
    form_class = WishForm
    success_url = reverse_lazy('wish:wish_list')

    def form_valid(self, form):
        # Сохранение желания
        wish = form.save(commit=False)
        wish.user = self.request.user
        wish.save()

        return super().form_valid(form)


@login_required
def create_active_wish(request):
    user = User.objects.get(id=request.user.id)
    random_wish = get_random_wish(user)
    if random_wish is None:
        return HttpResponseRedirect(request.META['HTTP_REFERER'])
    days_to_finished = random.randint(5, 10)
    target_date = now() + timedelta(days=days_to_finished)
    if user.active_wishes().exists():
        return HttpResponseRedirect(request.META['HTTP_REFERER'])

    ActiveWish.objects.create(name_wish=random_wish,
                              user_to_execute_wish=user,
                              user_whose_wish_to_execute=user.matched_user,
                              expiration=target_date)

    return HttpResponseRedirect(request.META['HTTP_REFERER'])


def get_random_wish(user):
    # Если у пользователя нет ни одного совпадения, возвращаем None
    wishes = Wish.objects.filter(user=user.matched_user)
    if not wishes:
        return None
    random_wish = wishes.order_by('?').first()
    return random_wish


def complete_wish(request):
    user = User.objects.get(id=request.user.id)
    active_wish = ActiveWish.objects.get(user_to_execute_wish=user)
    if active_wish.expiration > now():
        active_wish.wish_execution_state = True
        active_wish.save()
        return HttpResponseRedirect(request.META['HTTP_REFERER'])

    return HttpResponseRedirect(request.META['HTTP_REFERER'])


def checkout_wish(request):
    user = User.objects.get(id=request.user.id)
    active_wish = user.matched_user.active_wishes().first()
    if active_wish.wish_execution_state:
        HistoryExecutionWishes.objects.create(
            user_to_execute_wish=user.matched_user,
            wish=active_wish.name_wish,
        )
        HistoryExecutionWishes.objects.create(
            user_to_execute_wish=user,
            wish=active_wish.name_wish
        )
        active_wish.delete()
    return HttpResponseRedirect(request.META['HTTP_REFERER'])


def detected_match(request):
    user = User.objects.get(id=request.user.id)
    if user.is_matched:
        matches = UsersMatches.objects.filter(
            (Q(user_main=user) | Q(user_requested=user))
        )
        matches.first().delete()
        return HttpResponseRedirect(request.META['HTTP_REFERER'])
    return HttpResponseRedirect(request.META['HTTP_REFERER'])

#
# from users.models import User, UsersMatches
# from wish.models import Wish, ActiveWish
#
# user = User.objects.get(id=1)
# matches = UsersMatches.objects.filter(
#     (Q(user_main=user) | Q(user_requested=user))
# )
# from django.db.models import Q
# from django.utils.timezone import now
#
# matches = UsersMatches.objects.filter(
#     (Q(user_main=user) | Q(user_requested=user))
# )
# from wish.views import get_random_wish
#
# random_wish = get_random_wish(user)
# import random
#
# days_to_finished = random.randint(5, 10)
# from django.utils.timezone import now
# from datetime import timedelta
#
# target_date = now() + timedelta(days=days_to_finished)
#
# active_wish = ActiveWish.objects.create(name_wish=random_wish,
#                                         user_to_execute_wish=user,
#                                         user_whose_wish_to_execute=matches.first().user_requested,
#                                         expiration=target_date)
