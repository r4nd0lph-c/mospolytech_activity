from datetime import datetime, timedelta
from background_task import background
from services.daily_updates import DailyUpdates


def get_next_day_schedule():
    tomorrow = datetime.now() + timedelta(days=1)
    tomorrow_6am = datetime(year=tomorrow.year, month=tomorrow.month, day=tomorrow.day, hour=6, minute=0, second=0)

    time_difference = tomorrow_6am - datetime.now()
    seconds_difference = time_difference.total_seconds()

    return int(seconds_difference)


@background(schedule=get_next_day_schedule(), remove_existing_tasks=True)
def update():
    du = DailyUpdates()
    du.update_study_groups()
    du.update_students()
    du.update_schedules()
