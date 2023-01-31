from django.urls import path

from main.views import *

urlpatterns = [
    path("", Index.as_view(), name="index"),
    path("group_auto_complete/", GroupAutoComplete.as_view(), name="group_auto_complete"),
    path("auth/", Auth.as_view(redirect_authenticated_user=True), name="auth"),
    path("logout/", logout_user, name="logout"),
    path("get_groups/", get_groups, name="get_groups"),
    path("get_students/", get_students, name="get_students"),
    path("get_schedule/", get_schedule, name="get_schedule")
]
