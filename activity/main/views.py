from datetime import datetime, timedelta, date as ddate
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
from main.services.schedule_parser import ScheduleParser
from django.db.models import Min

class Index(LoginRequiredMixin, TemplateView):
    template_name = "main/index.html"
    login_url = reverse_lazy("auth")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = _("Main | Activity")
        context["logo_link"] = "main/graphics/logo/" + _("logo_en") + ".svg"
        username = (self.request.user.first_name + " " + self.request.user.last_name).strip()
        context["username"] = self.request.user.username if username == "" else username
        context["search_info_form"] = SearchInfoForm()
        return context


class StudentsRatingView(TemplateView):
    template_name = 'main/student_rating.html'
    login_url = reverse_lazy("auth")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = _("Main | Activity")
        context["logo_link"] = "main/graphics/logo/" + _("logo_en") + ".svg"
        username = (self.request.user.first_name + " " + self.request.user.last_name).strip()
        context["username"] = self.request.user.username if username == "" else username

        # Загрузка формы с рейтингом
        context["rating_display_form"] = RatingDisplayForm()

        return context

class GroupAutoComplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        if not self.request.user.is_authenticated:
            return StudyGroup.objects.none()
        qs = StudyGroup.objects.filter(is_active=True).order_by("name")
        if self.q:
            qs = qs.filter(name__contains=self.q)
        return qs


class StudentAutoComplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        if not self.request.user.is_authenticated:
            return Student.objects.none()
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
        context["logo_link"] = "main/graphics/logo/" + _("logo_en") + ".svg"
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
    def fill_schedule(group: str, d: datetime) -> list:
        sch = []
        db_schedules = Schedule.objects.filter(study_group__name=actual_group).order_by("date_start")
        for db_schedule in db_schedules:
            if db_schedule.date_start <= d.date() <= db_schedule.date_end:
                obj = {
                    "group": actual_group,
                    "type": db_schedule.type.name,
                    "is_session": db_schedule.is_session,
                    "dates": [
                        db_schedule.date_start.strftime("%d.%m.%Y"),
                        db_schedule.date_end.strftime("%d.%m.%Y")
                    ],
                    "grid": db_schedule.grid
                }
                sch.append(ScheduleAPI(obj).get_day(d.strftime("%d.%m.%Y")))
        return sch
    if request.method == "POST":
        study_group = request.POST.get("group", None)
        name = request.POST.get("name", None)
        if (study_group is not None) and (name is not None):
            student = Student.objects.filter(study_group__name=study_group).filter(name=name)[0]
            dates = sorted([datetime.strptime(d, "%d.%m.%Y") for d in request.POST.getlist("dates[]", None)])
            schedule = []
            group_history = StudyGroupOld.objects.filter(student=student)
            for date in dates:
                # if group history is empty
                if not group_history:
                    actual_group = student.study_group.name
                    schedule += fill_schedule(actual_group, date)
                # if group history is not empty
                else:
                    for gh in group_history:
                        if gh.date_start <= date.date() < gh.date_end:
                            actual_group = gh.study_group.name
                            break
                    else:
                        actual_group = student.study_group.name
                    schedule += fill_schedule(actual_group, date)
            return JsonResponse({
                "student": {"name": name, "group": study_group},
                "schedule": schedule
            })
    return JsonResponse({"message": "you don't have enough rights!"})
    
def get_schedule_group(request):
    """ returns formatted Schedule() objects from db and additional info """
    def fill_schedule(group: str, d: datetime) -> list:
        sch = []
        db_schedules = Schedule.objects.filter(study_group__name=actual_group).order_by("date_start")
        for db_schedule in db_schedules:
            if db_schedule.date_start <= d.date() <= db_schedule.date_end:
                obj = {
                    "group": actual_group,
                    "type": db_schedule.type.name,
                    "is_session": db_schedule.is_session,
                    "dates": [
                        db_schedule.date_start.strftime("%d.%m.%Y"),
                        db_schedule.date_end.strftime("%d.%m.%Y")
                    ],
                    "grid": db_schedule.grid
                }
                sch.append(ScheduleAPI(obj).get_day(d.strftime("%d.%m.%Y")))
        return sch
    if request.method == "POST":
        study_group = request.POST.get("group", None)
        if (study_group is not None):
            dates = sorted([datetime.strptime(d, "%d.%m.%Y") for d in request.POST.getlist("dates[]", None)])
            schedule = []
            group_history = StudyGroupOld.objects.filter()
            for date in dates:
                # if group history is empty
                if not group_history:
                    actual_group = study_group.name
                    schedule += fill_schedule(actual_group, date)
                # if group history is not empty
                else:
                    for gh in group_history:
                        if gh.date_start <= date.date() < gh.date_end:
                            actual_group = gh.study_group.name
                            break
                    else:
                        actual_group = study_group.name
                    schedule += fill_schedule(actual_group, date)
            return JsonResponse({
                "group": {"group": study_group},
                "schedule": schedule
            })
    return JsonResponse({"message": "yoKKKKKKKKKKKKKKKKKKKKKKKKsu don't hafvights!"})

def get_year_activity(request):
    """ returns info about student academic year activity """

    def special_days_from_month(start_date_str, end_date_str, weekday_num):
        """ returns the dates of the specified day of the week in the date range """

        start_date = datetime.strptime(start_date_str, "%d.%m.%Y")
        end_date = datetime.strptime(end_date_str, "%d.%m.%Y")

        dates_list = []
        delta = 1
        while start_date <= end_date:
            if start_date.weekday() == weekday_num:
                dates_list.append(start_date.strftime("%d.%m.%Y"))
                delta = 7
            start_date += timedelta(days=delta)

        return dates_list

    if request.method == "POST":
        study_group = request.POST.get("group", None)
        name = request.POST.get("name", None)

        if (study_group is not None) and (name is not None):
            student = Student.objects.filter(study_group__name=study_group).filter(name=name)[0]
            start_year = request.POST.get("start_year", None)
            if start_year:
                start_year = int(start_year)
            else:
                return JsonResponse({"message": "something went wrong!"})

            DP = [ddate(start_year, 9, 1), ddate(start_year + 1, 8, 30)]
            DM = ddate(start_year + 1, 1, 1)

            # search for all groups in which the student studied for the selected academic year
            required_groups = []
            group_history = StudyGroupOld.objects.filter(student=student).order_by("date_end")
            for group in group_history:
                if (group.date_start <= DP[0] <= group.date_end) or (
                        group.date_start >= DP[0] and group.date_end <= DP[1]) or (
                        group.date_start <= DP[1] <= group.date_end):
                    required_groups.append(group.study_group.name)
            ag = student.study_group.name
            if group_history:
                ag_ds = group_history[0].date_end
            else:
                ag_ds = ddate(int("20" + student.study_group.name[:2]), 9, 1)
            ag_de = datetime.today().date()
            if (ag_ds <= DP[0] <= ag_de) or (ag_ds >= DP[0] and ag_de <= DP[1]) or (ag_ds <= DP[1] <= ag_de):
                required_groups.append(ag)

            # format list to ["g1", "g2"] where "g1" - first semester group, "g2" - seconds semester group
            if len(required_groups) > 2:
                required_groups = required_groups[:2]
            if len(required_groups) < 2:
                required_groups.append(required_groups[0])

            # find required schedules
            schedules = [
                Schedule.objects.filter(
                    study_group__name=required_groups[0],
                    date_start__gte=DP[0],
                    date_end__lte=DM).first(),
                Schedule.objects.filter(
                    study_group__name=required_groups[1],
                    date_start__gte=DM,
                    date_end__lte=DP[1]).first()
            ]

            # find subjects
            subjects = []
            semester = 0
            for schedule in schedules:
                subjects_filter = []
                semester += 1
                if schedule is not None:
                    day_num = -1
                    for day in schedule.grid:
                        day_num += 1
                        for section in day:
                            for sbj in section:
                                if sbj["rooms"]:
                                    if sbj["title"] not in subjects_filter:
                                        subjects_filter.append(sbj["title"])
                                        visit_dates = special_days_from_month(sbj["dates"][0], sbj["dates"][1], day_num)
                                        subjects.append({
                                            "title": sbj["title"],
                                            "group": schedule.study_group.name,
                                            "semester": semester,
                                            "dates": sbj["dates"],
                                            "year": start_year + semester - 1,
                                            # TODO: fill "visits" status
                                            "visits": [{"date": d, "status": None} for d in visit_dates]
                                        })

            # format "activity" results
            activity = {
                "years": [start_year, start_year + 1],
                "semesters": {
                    1: {
                        "group": required_groups[0],
                        "date_start": schedules[0].date_start.strftime("%d.%m.%Y"),
                        "date_end": schedules[0].date_end.strftime("%d.%m.%Y")
                    } if schedules[0] else None,
                    2: {
                        "group": required_groups[1],
                        "date_start": schedules[1].date_start.strftime("%d.%m.%Y"),
                        "date_end": schedules[1].date_end.strftime("%d.%m.%Y")
                    } if schedules[1] else None},
                "subjects": subjects
            }

            return JsonResponse({
                "student": {"name": name, "group": study_group},
                "activity": activity
            })
    return JsonResponse({"message": "you don't have enough rights!"})

import random 


def filter_by_educational_program(queryset, educational_program_name):
    if educational_program_name:
        return queryset.filter(educational_program_name=educational_program_name)
    return queryset

def filter_by_department(queryset, department_name):
    if department_name:
        return queryset.filter(educational_program__department_name=department_name)
    return queryset

def filter_by_institution(queryset, institution_name):
    if institution_name:
        return queryset.filter(educational_program__department__institution_name=institution_name)
    return queryset

def get_rating(request):
    if request.method == "POST":
        display_choice = request.POST.get('display_choice', None)
        dates = request.POST.getlist('dates[]', None)
        educational_programs = EducationalProgram.objects.all()
        educational_program_name = request.POST.get('educational_program_name', None)
        department_name = request.POST.get('department_name', None)
        institution_name = request.POST.get('institution_name', None)
       
        if display_choice == "student":
            queryset = Student.objects.filter(is_active=True)[:100]
            queryset = filter_by_educational_program(queryset, educational_program_name)
            queryset = filter_by_department(queryset, department_name)
            queryset = filter_by_institution(queryset, institution_name)
            data = []
            for student in queryset:
                parser = ScheduleParser(student.study_group.name, 2022)  # Создаем экземпляр парсера для студента
                parser.count_subjects()  # Парсим расписание для студента
                subjects_count = parser.get_subjects_count()  # Получаем данные о занятиях
                total_lessons = parser.get_total_lessons()  # Получаем общее количество занятий
                educational_program = random.choice(educational_programs)
                filters_data = {
                    "name": educational_program.name,
                    "department": educational_program.department.name,
                    "institution": educational_program.department.parent.name,
                    "year": educational_program.year,      
                }
                subjects_visited_minutes = {}
                total_visited_minutes = 0
                for subject, count in subjects_count.items():
                    minutes = random.randint(0, count * 90) 
                    subjects_visited_minutes[subject] = minutes
                    total_visited_minutes += minutes
                data.append({"name": student.name, "group": student.study_group.name,"filters_data": filters_data , "minutes": total_lessons,"total_visited_minutes": total_visited_minutes, "subjects_count": subjects_count , 'subjects_visited_minutes' :subjects_visited_minutes})
            sorted_data = sorted(data, key=lambda x: x["total_visited_minutes"], reverse=True)
            return JsonResponse({"students": sorted_data})
        elif display_choice == "group":
            queryset = StudyGroup.objects.filter(is_active=True)[:100]
            queryset = filter_by_educational_program(queryset, educational_program_name)
            queryset = filter_by_department(queryset, department_name)
            queryset = filter_by_institution(queryset, institution_name)
            data = []
            for group in queryset:
                parser = ScheduleParser(group.name, 2022)  # Создаем экземпляр парсера для группы
                parser.count_subjects()  # Парсим расписание для группы
                subjects_count = parser.get_subjects_count()  # Получаем данные о занятиях
                total_lessons = parser.get_total_lessons()  # Получаем общее количество занятий
                subjects_visited_minutes = {}
                educational_program = random.choice(educational_programs)
                filters_data = {
                    "name": educational_program.name,
                    "department": educational_program.department.name,
                    "institution": educational_program.department.parent.name,
                    "year": educational_program.year,      
                }
                total_visited_minutes = 0
                for subject, count in subjects_count.items():
                    minutes = random.randint(0, count * 90) 
                    subjects_visited_minutes[subject] = minutes
                    total_visited_minutes += minutes
                data.append({"name": group.name , "filters_data": filters_data , "minutes": total_lessons,"total_visited_minutes": total_visited_minutes, "subjects_count": subjects_count , 'subjects_visited_minutes' :subjects_visited_minutes})
            sorted_data = sorted(data, key=lambda x: x["minutes"], reverse=True)
            return JsonResponse({"groups": sorted_data})
        else:
            return JsonResponse({"message": "Invalid display choice"})
    return JsonResponse({"message": "You don't have enough rights!"})



def page_not_found(request, exception):
    response = render(
        request, "main/404.html",
        {
            "title": _("Page not Found | Activity"),
            "logo_link": "main/graphics/logo" + _("logo_en") + ".svg"
        }
    )
    response.status_code = 404
    return response
