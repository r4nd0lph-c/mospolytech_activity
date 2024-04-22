import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "activity.settings")
import django
import calendar
django.setup()
from datetime import datetime, date, timedelta
from main.models import *
from main.services.mospolytech_api.schedule import Schedule as ScheduleAPI
from collections import defaultdict

class ScheduleParser:
    """
    Парсер расписаний для подсчета количества занятий по каждому предмету
    """

    def __init__(self, group: str, start_year: int):
        self.group = group
        self.start_year = start_year
        self.subjects_count = defaultdict(int)
        self.total_lessons = 0  # Общее количество занятий

    def parse_schedule(self):
        DP = [date(self.start_year, 9, 1), date(self.start_year + 1, 8, 30)]
        DM = date(self.start_year + 1, 1, 1)
        schedules = [
            Schedule.objects.filter(
                study_group__name=self.group,
                date_start__gte=DP[0],
                date_end__lte=DM
            ).first(),
            Schedule.objects.filter(
                study_group__name=self.group,
                date_start__gte=DM,
                date_end__lte=DP[1]
            ).first()
        ]

        for schedule in schedules:
            if schedule:
                #print(schedule.grid)
                grid_data = schedule.grid
                day_index = -1  # Начальное значение индекса дня
                for day in grid_data:
                    day_index += 1  # Инкрементировать индекс дня
                    for lessons in day:
                        for lesson in lessons:
                            rooms = lesson.get('rooms')
                            if rooms != []:  # Проверка на наличие комнат
                                subject = lesson.get('title')
                                start_date_str, end_date_str = lesson.get('dates')
                                start_date = datetime.strptime(start_date_str, '%d.%m.%Y')
                                end_date = datetime.strptime(end_date_str, '%d.%m.%Y')
                                # Вызываем метод для подсчета количества дней недели
                                weekday = day_index
                                weekday_count = self.count_weekday_between_dates(start_date, end_date, weekday)  # Понедельник
                                #print(f"Day index: {day_index}")
                                if subject:
                                    self.subjects_count[subject] += weekday_count
                                    self.total_lessons += weekday_count

    def count_weekday_between_dates(self, start_date, end_date, weekday):
        # Вычисляем количество полных недель
        weeks = 0
        current_date = start_date

        while current_date <= end_date:
            if current_date.weekday() == weekday:
                weeks += 1
            current_date += timedelta(days=1)

        return weeks
    
    def count_subjects(self):
        self.parse_schedule()

    def get_subjects_count(self):
        return self.subjects_count

    def get_total_lessons(self):
        return self.total_lessons * 90
    


class CustomScheduleParser:
    """
    Парсер расписаний для подсчета количества занятий по каждому предмету
    """

    def __init__(self) -> None:
        pass

    @staticmethod
    def __find_schedule(group: str, d: str) -> dict:
        d = datetime.strptime(d, "%d.%m.%Y")
        for sch in Schedule.objects.filter(study_group__name=group).order_by("date_start"):
            if sch.date_start <= d.date() <= sch.date_end:
                return {
                    "group": group,
                    "type": sch.type.name,
                    "is_session": sch.is_session,
                    "dates": [
                        sch.date_start.strftime("%d.%m.%Y"),
                        sch.date_end.strftime("%d.%m.%Y")
                    ],
                    "grid": sch.grid
                }

    @staticmethod
    def get_day(group: str, d: str) -> dict:
        schedule = CustomScheduleParser.__find_schedule(group, d)
        if schedule:
            day_data = ScheduleAPI(schedule).get_day(d)
            if day_data and "day" in day_data:
                lesson_count = sum(1 for lesson in day_data["day"] if lesson.get('subject') and lesson.get('subject').get('rooms')) * 90
                return (lesson_count)
        else:
            return {"error": "Schedule not found"}
        
    @staticmethod
    def get_week(group: str, d: str) -> dict:
        schedule = CustomScheduleParser.__find_schedule(group, d)
        if schedule:
            week_data = ScheduleAPI(schedule).get_week(d)
            if week_data and "week" in week_data:
                lesson_count = sum(1 for day_data in week_data["week"] for lesson in day_data.get("day", []) if lesson.get('subject') and lesson.get('subject').get('rooms')) * 90
                return (lesson_count)
        else:
            return {"error": "Schedule not found"}
    
    @staticmethod
    def get_month(group: str, month: str, year: int) -> dict:
        num_days_in_month = calendar.monthrange(year, int(month))[1]
        total_lesson_count = 0
        days_in_first_week = 7 - (date(year, int(month), 1).weekday() + 1)
        #print(days_in_first_week)
        
        # Получаем данные для первых 7 дней месяца
        for day in range(1, days_in_first_week + 1):
            date_str = f"{day:02d}.{month}.{year}"
            day_data = CustomScheduleParser.get_day(group, date_str)
            #print (date_str, day_data)
            if isinstance(day_data, int):
                total_lesson_count += day_data
            elif "lesson_count" in day_data:
                total_lesson_count += day_data["lesson_count"]
        
        # Получаем данные для последних 7 дней месяца
        last_day_of_month = date(year, int(month), num_days_in_month)
        last_day_of_week = last_day_of_month.weekday()  # 0 - понедельник, 6 - воскресенье
        #print(last_day_of_week)
        if last_day_of_week < 6:  # Если последний день месяца не воскресенье, значит есть еще дни в последней неделе
            first_day_of_last_week = num_days_in_month - last_day_of_week
            days_in_last_week = num_days_in_month - first_day_of_last_week + 1
            #print(days_in_last_week)
            for day in range(num_days_in_month - days_in_last_week + 1, num_days_in_month + 1):
                date_str = f"{day:02d}.{month}.{year}"
                day_data = CustomScheduleParser.get_day(group, date_str)
                #print (date_str, day_data)
                if isinstance(day_data, int):
                    total_lesson_count += day_data
                elif "lesson_count" in day_data:
                    total_lesson_count += day_data["lesson_count"]
        else:
            # Получаем данные для оставшихся недель месяца
            for day in range(days_in_first_week + 2, num_days_in_month, 7):
                date_str = f"{day:02d}.{month}.{year}"
                week_data = CustomScheduleParser.get_week(group, date_str)
                #print (date_str, week_data)
                if isinstance(week_data, int):
                    total_lesson_count += week_data
                elif "lesson_count" in week_data:
                    total_lesson_count += week_data["lesson_count"]

            return (total_lesson_count)
        
        # Получаем данные для оставшихся недель месяца
        for day in range(days_in_first_week + 2, num_days_in_month - 6, 7):
            date_str = f"{day:02d}.{month}.{year}"
            week_data = CustomScheduleParser.get_week(group, date_str)
            #print (date_str, week_data)
            if isinstance(week_data, int):
                total_lesson_count += week_data
            elif "lesson_count" in week_data:
                total_lesson_count += week_data["lesson_count"]

        return (total_lesson_count)


if __name__ == "__main__":
    parser = ScheduleParser("201-721", 2022)
    parser.count_subjects()
    subjects_count = parser.get_subjects_count()
    total_lessons = parser.get_total_lessons()
    print("Количество занятий по каждому предмету:")
    for subject, count in subjects_count.items():
        print(f"Предмет '{subject}': {count} занятий")
    print(f"Общее количество минут занятий: {total_lessons}")

    # Вызов функции count_lessons_on_date для подсчета занятий в указанный день и группе
    sp = CustomScheduleParser()
    day = sp.get_day("211-325", "11.05.2023")
    print("Общее количество минут занятий в день:", day)
    week = sp.get_week("211-325", "08.05.2023")
    print("Общее количество минут занятий в неделю:", week)
    month = sp.get_month("211-325", "05", 2023)
    print("Общее количество минут занятий в месяц:", month)