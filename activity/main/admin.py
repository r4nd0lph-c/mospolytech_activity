from django.utils.translation import gettext_lazy as _
from django.contrib import admin
from django.contrib.admin import DateFieldListFilter

from admin_auto_filters.filters import AutocompleteFilter

from main.models import *
from main.views import Auth, logout_user


class AbstractLockedAdmin(admin.ModelAdmin):
    def has_add_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def get_actions(self, request):
        actions = super().get_actions(request)
        if "delete_selected" in actions:
            del actions["delete_selected"]
        return actions


class StudyGroupFilter(AutocompleteFilter):
    title = "Study Group"
    field_name = "study_group"


@admin.register(StudyGroup)
class StudyGroupAdmin(AbstractLockedAdmin):
    list_display = ("id", "name", "is_active", "date_created", "date_updated")
    list_display_links = ("id",)
    ordering = ("name",)
    list_filter = ("is_active",)
    search_fields = ["name"]


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "study_group", "is_active", "date_created", "date_updated")
    list_display_links = ("id",)
    ordering = ("study_group", "is_active", "name")
    list_filter = ("is_active",)


@admin.register(ScheduleType)
class ScheduleTypeAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "date_created", "date_updated")
    list_display_links = ("id",)
    ordering = ("id",)


@admin.register(Schedule)
class ScheduleAdmin(admin.ModelAdmin):
    list_display = (
        "id", "study_group", "type", "is_session", "date_start", "date_end")
    list_display_links = ("id",)
    ordering = ("study_group", "date_start")
    list_filter = (StudyGroupFilter, "is_session")


@admin.register(HistoryLog)
class HistoryLogAdmin(AbstractLockedAdmin):
    list_display = ("id", "user", "action", "date_created")
    ordering = ("-date_created",)
    list_filter = (("user", admin.RelatedOnlyFieldListFilter), ("date_created", DateFieldListFilter))


admin.site.site_title = _("Activity")
admin.site.site_header = _("Mospolytech Activity")
admin.site.index_title = _("Administration")

admin.site.login = Auth.as_view()
admin.site.logout = logout_user
