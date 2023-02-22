from datetime import datetime
from django.utils.translation import gettext_lazy as _
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.contrib.auth import logout
from django.contrib.auth.views import LoginView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView
from main.services.mospolytech_api.schedule import Schedule as ScheduleAPI
from main.services.logs_writer import LogsWriter
from main.forms import *


class Index(LoginRequiredMixin, TemplateView):
    template_name = "main/index.html"
    login_url = reverse_lazy("auth")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = _("Main | Activity")
        context["logo_link"] = "main/graphics/" + _("logo_en") + ".svg"
        username = (self.request.user.first_name + " " + self.request.user.last_name).strip()
        context["username"] = self.request.user.username if username == "" else username
        context["search_info_form"] = SearchInfoForm()
        return context


class GroupAutoComplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        qs = StudyGroup.objects.filter(is_active=True).order_by("name")
        if self.q:
            qs = qs.filter(name__contains=self.q)
        return qs


class StudentAutoComplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        qs = Student.objects.filter(is_active=True).order_by("study_group__name", "name")
        groups = self.forwarded.get("group", None)
        if groups:
            qs = qs.filter(study_group_id__in=[int(g) for g in groups])
        if self.q:
            qs = qs.filter(name__contains=self.q)
        return qs


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
        LogsWriter.auth(self.request.user)
        return reverse_lazy("index")


def logout_user(request):
    logout(request)
    return redirect("auth")


def get_groups(request):
    """ returns all StudyGroup() objects from db """

    if request.method == "POST":
        groups = [g.name for g in StudyGroup.objects.filter(is_active=True)]
        return JsonResponse({"groups": groups})
    return JsonResponse({"message": "you don't have enough rights!"})


def get_students(request):
    """ returns Student() objects from db (all active or from given groups) """

    if request.method == "POST":
        requested_groups = request.POST.getlist("groups[]", None)
        if requested_groups:
            db_students = Student.objects.filter(is_active=True, study_group__name__in=requested_groups)
        else:
            db_students = Student.objects.filter(is_active=True)
        return JsonResponse({"students": [{"name": s.name, "group": s.study_group.name} for s in db_students]})
    return JsonResponse({"message": "you don't have enough rights!"})


def get_schedule(request):
    """ returns formatted Schedule() objects from db and additional info """

    if request.method == "POST":
        student = {"name": request.POST.get("name", None), "group": request.POST.get("group", None)}
        dates = sorted([datetime.strptime(d, "%d.%m.%Y") for d in request.POST.getlist("dates[]", None)])
        db_schedules = Schedule.objects.filter(study_group__name=student["group"]).order_by("date_start")

        # TODO: optimize loops
        schedule = []
        for date in dates:
            for db_schedule in db_schedules:
                if db_schedule.date_start <= date.date() <= db_schedule.date_end:
                    obj = {
                        "group": db_schedule.study_group.name,
                        "type": db_schedule.type.name,
                        "is_session": db_schedule.is_session,
                        "dates": [
                            db_schedule.date_start.strftime("%d.%m.%Y"),
                            db_schedule.date_end.strftime("%d.%m.%Y")
                        ],
                        "grid": db_schedule.grid
                    }
                    schedule.append(ScheduleAPI(obj).get_day(date.strftime("%d.%m.%Y")))
        return JsonResponse({
            "student": student,
            "schedule": schedule
        })
    return JsonResponse({"message": "you don't have enough rights!"})


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
