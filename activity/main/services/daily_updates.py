import os
import django

from mospolytech_api.api import API

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "mospolytech_activity.settings")
django.setup()

from main.models import *


def update_study_groups() -> None:
    pass


def update_students() -> None:
    pass


if __name__ == "__main__":
    pass
