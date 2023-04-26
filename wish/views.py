from django.contrib.auth.decorators import login_required
from django.contrib.messages.views import SuccessMessageMixin
from django.http import HttpResponseRedirect
from django.shortcuts import render, reverse
from django.urls import reverse_lazy
from django.views.generic import TemplateView, FormView
from django.contrib import messages

from users.models import User
from users.forms import MatchForm


# Create your views here.


class IndexView(TemplateView):
    template_name = 'wish/index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        context['users'] = User.objects.all()
        return context


class MatchFormView(SuccessMessageMixin, FormView):
    template_name = 'wish/test_index.html'
    form_class = MatchForm
    success_url = reverse_lazy('wish:wishes')

    def form_valid(self, form):
        user = self.request.user
        success, message = form.send_email_and_create_record(user)
        if success:
            messages.success(self.request, message)
        else:
            messages.warning(self.request, message)
        return super().form_valid(form)