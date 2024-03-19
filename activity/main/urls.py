from django.contrib.staticfiles.storage import staticfiles_storage
from django.urls import path
from django.views.generic import RedirectView

from main.views import *

urlpatterns = [
    path("favicon.ico", RedirectView.as_view(url=staticfiles_storage.url("main/graphics/favicons/favicon.ico"))),
    path("", Index.as_view(), name="index"),
    path("group_auto_complete/", GroupAutoComplete.as_view(), name="group_auto_complete"),
    path("student_auto_complete/", StudentAutoComplete.as_view(), name="student_auto_complete"),
    path("auth/", Auth.as_view(redirect_authenticated_user=True), name="auth"),
    path("logout/", logout_user, name="logout"),
    path("get_groups/", get_groups, name="get_groups"),
    path("get_students/", get_students, name="get_students"),
    path("get_schedule/", get_schedule, name="get_schedule"),
    path("get_schedule_group/", get_schedule_group, name="get_schedule_group"),
    path("get_year_activity/", get_year_activity, name="get_year_activity"),
    path('students_rating/', StudentsRatingView.as_view(), name='student_rating'),
    path('students_rating/get_rating/', get_rating , name='get_students_rating'),
]
