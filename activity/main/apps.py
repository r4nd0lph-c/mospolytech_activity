from django.utils.translation import gettext_lazy as _
from django.apps import AppConfig


class MainConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "main"
    verbose_name = _("Entities")
