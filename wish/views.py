import random
from datetime import timedelta

from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.urls import reverse_lazy, reverse
from django.views.generic import TemplateView, FormView
from django.contrib import messages
from django.utils.timezone import now

from users.models import User
from users.forms import MatchForm

from wish.forms import WishForm
from wish.models import Wish, ActiveWish


# Create your views here.


class IndexView(TemplateView):
    template_name = 'wish/index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        context['users'] = User.objects.all()
        return context


class WishListView(TemplateView):
    template_name = 'wish/list_wishes.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        context['list_wish'] = Wish.objects.filter(user_id=self.request.user.id)
        # context['log_executed_wish_history'] = User.objects.get(id=self.request.user.id).wish_history.
        return context


class WishListHistoryView(TemplateView):
    template_name = 'wish/history.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        user = User.objects.get(id=self.request.user.id)
        context['my_completed_wishes'] = user.wish_executed
        context['wishes_completed_for_me'] = user.wish_history
        return context


class MatchFormView(FormView):
    """Класс MatchFormView наследуется от FormView, и отвечает за обработку формы подбора пары (MatchForm)."""

    template_name = 'wish/success_match.html'  # переименовать html
    form_class = MatchForm
    success_url = reverse_lazy('wish:wishes')

    def form_valid(self, form):
        """Метод form_valid(self, form) вызывается, если форма прошла валидацию. Метод получает данные формы,
        извлекает объект пользователя (user) и проверяет, не имеет ли пользователь уже пару (is_matched). Если у
        пользователя уже есть пара, то выводится сообщение об ошибке, иначе отправляется письмо с уведомлением и
        создается запись в базе данных о запросе на подбор пары. В случае успеха выводится сообщение об успешной
        отправке письма. Если возникают ошибки, выводится сообщение об ошибке."""
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
    """Класс MakeWishList представляет собой форму, которая отображает страницу создания нового желания. Пользователь
    может заполнить форму и отправить ее, чтобы сохранить новое желание в базе данных."""
    template_name = 'wish/make_wish_list.html'
    form_class = WishForm
    success_url = reverse_lazy('wish:make_wish')

    def form_valid(self, form):
        if not self.request.user.is_authenticated:
            # Если пользователь не аутентифицирован, перенаправляем его на страницу входа
            return HttpResponseRedirect(reverse('users:login'))
            # Сохранение желания
        wish = form.save(commit=False)
        wish.user = self.request.user
        wish.save()

        return super().form_valid(form)


@login_required
def create_active_wish_view(request):
    """Функция create_active_wish создает активное желание для пользователя, который должен выполнить желание пары.
    Если пользователь уже имеет активное желание, то функция перенаправляет его на предыдущую страницу.

"""
    user = User.objects.get(id=request.user.id)
    random_wish = get_random_wish(user)
    if random_wish is None:
        return HttpResponseRedirect(request.META['HTTP_REFERER'])
    days_to_finished = random.randint(5, 10)
    target_date = now() + timedelta(days=days_to_finished)
    if user.get_active_wishes().exists():
        return HttpResponseRedirect(request.META['HTTP_REFERER'])

    ActiveWish.objects.create(wish=random_wish,
                              executor=user,
                              owner=user.matched_user,
                              expiration=target_date)

    return HttpResponseRedirect(request.META['HTTP_REFERER'])


def get_random_wish(user):
    """Возвращает случайное желание пары"""
    wishes = Wish.objects.filter(user=user.matched_user)
    if not wishes:
        return None
    random_wish = wishes.order_by('?').first()
    return random_wish


def complete_wish_view(request):
    """Принимает запрос пользователя и отмечает активное желание как выполненное."""
    user = User.objects.get(id=request.user.id)
    active_wish = ActiveWish.objects.get(executor=user)
    if active_wish.expiration > now():
        active_wish.is_executed = True
        active_wish.save()
        return HttpResponseRedirect(request.META['HTTP_REFERER'])

    return HttpResponseRedirect(request.META['HTTP_REFERER'])


def checkout_wish_view(request):
    """Принимает запрос пользователя и подтверждает выполнение активного желание"""

    user = User.objects.get(id=request.user.id)
    active_wish = user.matched_user.get_active_wishes().first()
    if active_wish.is_executed:
        active_wish.log_executed_wish_history()
        active_wish.log_wish_history()
        active_wish.wish.delete()
    return HttpResponseRedirect(request.META['HTTP_REFERER'])


def detected_match_view(request):
    """Разрывание пары test"""
    user = User.objects.get(id=request.user.id)
    if user.is_matched:
        matches = user.matchpair_set.first()
        matches.delete()
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
