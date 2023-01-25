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
    for group in fresh_groups:
        StudyGroup.objects.create(name=group)


def update_students() -> None:
    """ update Student() model info in db """

    # creating API object
    api = API()

    # getting fresh list of students from https://e.mospolytech.ru/old/lk_api_mapp.php
    fresh_students = []
    for group in api.get_groups():
        fresh_students += [
            {"name": name, "group": group}
            for name in api.get_students([group])
        ]

    # getting queryset of students from db
    db_students = Student.objects.all()

    # updating existing students "is_active" field
    fresh_names = [student["name"] for student in fresh_students]
    for student in db_students:
        if student.name in fresh_names:
            student.active = True
        else:
            student.active = False
        student.save()
        fresh_names.remove(student.name)
    fresh_students = [student for student in fresh_students if student["name"] in fresh_names]

    # adding students to db
    for student in fresh_students:
        Student.objects.create(
            name=student["name"],
            study_group_id=StudyGroup.objects.get_or_create(name=student["group"])[0].id
        )


if __name__ == "__main__":
    update_study_groups()
    update_students()
