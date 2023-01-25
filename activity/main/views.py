from django.utils.translation import gettext_lazy as _
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.contrib.auth import logout
from django.contrib.auth.views import LoginView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView

from main.forms import AuthForm
from .models import *


class Index(LoginRequiredMixin, TemplateView):
    template_name = "main/index.html"
    login_url = reverse_lazy("auth")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = _("Main | Activity")
        context["logo_link"] = "main/graphics/" + _("logo_en") + ".svg"
        username = (self.request.user.first_name + " " + self.request.user.last_name).strip()
        context["username"] = self.request.user.username if username == "" else username
        return context


class Auth(LoginView):
    template_name = "main/auth.html"
    form_class = AuthForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = _("Authorization | Activity")
        context["logo_link"] = "main/graphics/" + _("logo_en") + ".svg"
        return context

    def form_valid(self, form):
        remember_me = form.cleaned_data["remember_me"]
        if not remember_me:
            self.request.session.set_expiry(0)
            self.request.session.modified = True
        return super(Auth, self).form_valid(form)

    # TODO: redirect to "?next=..."
    def get_success_url(self):
        return reverse_lazy("index")


def logout_user(request):
    logout(request)
    return redirect("auth")


def page_not_found(request, exception):
    response = render(
        request, "main/404.html",
        {
            "title": _("Page not Found | Activity"),
            "logo_link": "main/graphics/" + _("logo_en") + ".svg"
        }
    )
    response.status_code = 404
    return response
