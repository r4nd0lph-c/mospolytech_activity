import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "activity.settings")
import django
django.setup()
from datetime import datetime, date, timedelta
from main.models import *
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


if __name__ == "__main__":
    parser = ScheduleParser("201-721", 2022)
    parser.count_subjects()
    subjects_count = parser.get_subjects_count()
    total_lessons = parser.get_total_lessons()
    print("Количество занятий по каждому предмету:")
    for subject, count in subjects_count.items():
        print(f"Предмет '{subject}': {count} занятий")
    print(f"Общее количество минут занятий: {total_lessons}")