import os
from datetime import datetime
from hashlib import md5
import django
from mospolytech_api.api import API

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "activity.settings")
django.setup()

from main.models import *


def logs_error(args) -> None:
    """ keeps an error log for daily_updates.py """

    with open("daily_updates_error.log", "a", encoding="utf-8") as f:
        f.write(f"[{datetime.now().strftime('%d.%m.%Y, %H:%M:%S')}] ({', '.join(args)})\n")


def update_study_groups() -> None:
    """ updates StudyGroup() model info in db """

    try:
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

    except Exception as e:
        logs_error(e.args)


# TODO: exception handler for update_students()
def update_students() -> None:
    """ updates Student() model info in db """

    try:
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
                fresh_names.remove(student.name)
                student.active = True
            else:
                student.active = False
            student.save()
        fresh_students = [student for student in fresh_students if student["name"] in fresh_names]

        # adding students to db
        for student in fresh_students:
            Student.objects.create(
                name=student["name"],
                study_group_id=StudyGroup.objects.get_or_create(name=student["group"])[0].id
            )

    except Exception as e:
        logs_error(e.args)


def update_schedules() -> None:
    """ updates Schedule() model info in db """

    def signature(obj: dict) -> str:
        """ creates signature (md5 hex-string) for schedule object """

        s = f"{obj['group']}{obj['type']}{obj['is_session']}{obj['dates'][0]}{obj['dates'][1]}"
        r = md5(s.encode())
        return r.hexdigest()

    # creating API object
    api = API()

    # getting fresh schedules from https://rasp.dmami.ru/site/group
    for group in api.get_groups():
        for is_session in [False, True]:
            try:
                schedule = api.get_schedule(group, is_session)
                schedule["signature"] = signature(schedule)

                # trying to find schedule in db by signature
                db_schedules = Schedule.objects.filter(signature=schedule["signature"])

                # change schedule object in db
                if db_schedules:
                    # already exists - update
                    db_obj = db_schedules[0]
                    db_obj.grid = schedule["grid"]
                else:
                    # does not exist - create
                    db_obj = Schedule.objects.create(
                        study_group_id=StudyGroup.objects.get_or_create(name=schedule["group"])[0].id,
                        type_id=ScheduleType.objects.get_or_create(name=schedule["type"])[0].id,
                        is_session=schedule["is_session"],
                        date_start=datetime.strptime(schedule["dates"][0], "%d.%m.%Y").date(),
                        date_end=datetime.strptime(schedule["dates"][1], "%d.%m.%Y").date(),
                        grid=schedule["grid"],
                        signature=schedule["signature"]
                    )
                db_obj.save()

            except Exception as e:
                logs_error(e.args)


if __name__ == "__main__":
    update_study_groups()
    update_students()
    update_schedules()
