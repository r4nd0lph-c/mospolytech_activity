# TODO: periodic task with daily updates

import os
from datetime import datetime
from hashlib import md5
import django
from mospolytech_api.api import API

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "activity.settings")
django.setup()

from main.models import *


class DailyUpdates:
    """
    class for updating information in database:
      * study groups
      * students
      * schedules
    """

    # path to file with logs
    LOGS_FILE = "daily_updates.log"

    def __init__(self) -> None:
        """ initializes API object for work & splits logs file """

        # creating API object
        self.api = API()

        # splitting logs
        with open(DailyUpdates.LOGS_FILE, "a", encoding="utf-8") as f:
            f.write("-" * 20 + "\n")

    @staticmethod
    def logs(success: bool, *args) -> None:
        """ keeps logs of information processing functions """

        with open(DailyUpdates.LOGS_FILE, "a", encoding="utf-8") as f:
            f.write(
                f"[{datetime.now().strftime('%d.%m.%Y, %H:%M:%S')}] "
                f"[{'V' if success else 'X'}] "
                f"({', '.join(args)})\n"
            )

    def update_study_groups(self) -> None:
        """ updates StudyGroup() model info in db """

        try:
            # getting fresh list of groups from https://rasp.dmami.ru/groups-list.json
            fresh_groups = self.api.get_groups()
            log_arg_1 = len(fresh_groups)

            # getting queryset of groups from db
            db_groups = StudyGroup.objects.all()

            # updating existing groups "is_active" field
            for group in db_groups:
                if group.name in fresh_groups:
                    fresh_groups.remove(group.name)
                    group.is_active = True
                else:
                    group.is_active = False
                group.save()
            log_arg_2 = len(fresh_groups)

            # adding groups to db
            for group in fresh_groups:
                StudyGroup.objects.create(name=group)

            # writing logs
            all_groups = StudyGroup.objects.all().count()
            DailyUpdates.logs(
                True,
                f"GROUPS -> all: {all_groups}",
                f"fresh: {log_arg_1}",
                f"new: {log_arg_2}",
                f"hidden: {all_groups - log_arg_1}"
            )
        except Exception as e:
            DailyUpdates.logs(False, *e.args)

    def update_students(self) -> None:
        """ updates Student() model info in db """

        try:
            # getting fresh list of students from https://e.mospolytech.ru/old/lk_api_mapp.php
            fresh_students = []
            for group in self.api.get_groups():
                fresh_students += [
                    {"name": name, "group": group}
                    for name in self.api.get_students([group])
                ]
            log_arg_1 = len(fresh_students)

            # getting queryset of students from db
            db_students = Student.objects.all()

            # updating existing students "is_active" field
            fresh_names = [student["name"] for student in fresh_students]
            for student in db_students:
                if student.name in fresh_names:
                    fresh_names.remove(student.name)
                    student.is_active = True
                else:
                    student.is_active = False
                student.save()
            fresh_students = [student for student in fresh_students if student["name"] in fresh_names]
            log_arg_2 = len(fresh_students)

            # adding students to db
            for student in fresh_students:
                Student.objects.create(
                    name=student["name"],
                    study_group_id=StudyGroup.objects.get_or_create(name=student["group"])[0].id
                )

            # writing logs
            all_students = Student.objects.all().count()
            DailyUpdates.logs(
                True,
                f"STUDENTS -> all: {all_students}",
                f"fresh: {log_arg_1}",
                f"new: {log_arg_2}",
                f"hidden: {all_students - log_arg_1}"
            )
        except Exception as e:
            DailyUpdates.logs(False, *e.args)

    def update_schedules(self) -> None:
        """ updates Schedule() model info in db """

        def signature(obj: dict) -> str:
            """ creates signature (md5 hex-string) for schedule object """

            s = f"{obj['group']}{obj['type']}{obj['is_session']}{obj['dates'][0]}{obj['dates'][1]}"
            r = md5(s.encode())
            return r.hexdigest()

        # getting fresh schedules from https://rasp.dmami.ru/site/group
        for group in self.api.get_groups():
            for is_session in [False, True]:
                try:
                    schedule = self.api.get_schedule(group, is_session)
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

                    # writing logs
                    DailyUpdates.logs(
                        True,
                        f"is_session: {'true ' if is_session else 'false'}",
                        f"The schedule for the '{group}' group is created / updated"
                    )
                except Exception as e:
                    DailyUpdates.logs(False, f"is_session: {'true ' if is_session else 'false'}", *e.args)


if __name__ == "__main__":
    du = DailyUpdates()
    du.update_study_groups()
    du.update_students()
    du.update_schedules()
