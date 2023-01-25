import os
import django

from mospolytech_api.api import API

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "activity.settings")
django.setup()

from main.models import *


def update_study_groups() -> None:
    """ update StudyGroup() model info in db """

    # creating API object
    api = API()

    # getting fresh list of groups from https://rasp.dmami.ru/groups-list.json
    fresh_groups = api.get_groups()

    # getting queryset of groups from db
    db_groups = StudyGroup.objects.all()

    # updating existing groups "is_active" field
    for group in db_groups:
        if group.name in fresh_groups:
            fresh_groups.remove(group.name)
            group.active = True
        else:
            group.active = False
        group.save()

    # adding groups to db
    for name in fresh_groups:
        StudyGroup.objects.create(name=name)


def update_students() -> None:
    """ update Student() model info in db """

    # creating API object
    api = API()


if __name__ == "__main__":
    update_study_groups()
