from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.views.generic.base import RedirectView, TemplateView, View


class CalendarView(View):
    login_url = "accounts:signin"
    template_name = 'calendars/index.html'

    def get(self, request, *args, **kwargs):
        event_list = []
        context = {
            'events': event_list,
        }
        return render(request, self.template_name, context)
