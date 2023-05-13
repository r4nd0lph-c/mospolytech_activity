# --------------------------------------------------------------------------------------------------------------------#
# ███╗   ███╗ ██████╗ ███████╗██████╗  ██████╗ ██╗  ██╗   ██╗████████╗███████╗ ██████╗██╗  ██╗     █████╗ ██████╗ ██╗ #
# ████╗ ████║██╔═══██╗██╔════╝██╔══██╗██╔═══██╗██║  ╚██╗ ██╔╝╚══██╔══╝██╔════╝██╔════╝██║  ██║    ██╔══██╗██╔══██╗██║ #
# ██╔████╔██║██║   ██║███████╗██████╔╝██║   ██║██║   ╚████╔╝    ██║   █████╗  ██║     ███████║    ███████║██████╔╝██║ #
# ██║╚██╔╝██║██║   ██║╚════██║██╔═══╝ ██║   ██║██║    ╚██╔╝     ██║   ██╔══╝  ██║     ██╔══██║    ██╔══██║██╔═══╝ ██║ #
# ██║ ╚═╝ ██║╚██████╔╝███████║██║     ╚██████╔╝███████╗██║      ██║   ███████╗╚██████╗██║  ██║    ██║  ██║██║     ██║ #
# ╚═╝     ╚═╝ ╚═════╝ ╚══════╝╚═╝      ╚═════╝ ╚══════╝╚═╝      ╚═╝   ╚══════╝ ╚═════╝╚═╝  ╚═╝    ╚═╝  ╚═╝╚═╝     ╚═╝ #
# author: https://t.me/rand0lphc                                                                                      #
# ------------------------------------------------------------------------------------------------------------------- #


from datetime import datetime, timedelta


class Schedule:
    """
    DESCRIPTION
        * class representing schedule of group
        * contains information about schedule and manipulates it
    -----
    ATTRIBUTES
        * (class) TIME_SECTIONS (dict): time sections for different forms of education
        * (instance) group (str): name of group
        * (instance) type (str): type of group
        * (instance) is_session (bool): session flag
        * (instance) dates (list[str]): range of available dates
        * (instance) grid (list[list]): modified grid
    -----
    ARGS
        * (required) schedule (dict): dict containing schedule information
    -----
    METHODS
        * get_day(date: str) -> dict
        * get_week(date: str, ignore_range_err: bool = False) -> dict
    """

    # attribute for class operations
    TIME_SECTIONS = {
        "morning": [
            ["09:00", "10:30"],
            ["10:40", "12:10"],
            ["12:20", "13:50"],
            ["14:30", "16:00"],
            ["16:10", "17:40"],
            ["17:50", "19:20"],
            ["19:30", "21:00"],
        ],
        "evening": [
            ["09:00", "10:30"],
            ["10:40", "12:10"],
            ["12:20", "13:50"],
            ["14:30", "16:00"],
            ["16:10", "17:40"],
            ["18:20", "19:40"],
            ["19:50", "21:10"],
        ],
    }

    def __init__(self, schedule: dict) -> None:
        """
        DESCRIPTION
            * initializes Schedule object
        -----
        ARGS
            * (required) schedule (dict): dict containing schedule information
        -----
        RETURNS
            * there is no return
        -----
        ERRORS
            * there are no custom errors
        """

        self.group = schedule["group"]
        self.type = schedule["type"]
        self.is_session = schedule["is_session"]
        self.dates = schedule["dates"]
        self.grid = schedule["grid"]

    @staticmethod
    def __d(date: str, frmt: str = "%d.%m.%Y") -> datetime:
        """
        DESCRIPTION
            * converts string to datetime object depending on given format
        -----
        ARGS
            * (required) date (str): string with recorded date
            * (optional) frmt (str): format of string with recorded date,
            by default is "%d.%m.%Y"
        -----
        RETURNS
            * date (datetime): datetime object
        -----
        ERRORS
            * there are no custom errors
        """

        # returning datetime object
        return datetime.strptime(date, frmt)

    @staticmethod
    def __s(date: datetime, frmt: str = "%d.%m.%Y") -> str:
        """
        DESCRIPTION
            * converts datetime object to string depending on given format
        -----
        ARGS
            * (required) date (datetime): datetime object
            * (optional) frmt (str): format of string with recorded date,
            by default is "%d.%m.%Y"
        -----
        RETURNS
            * date (str): string with recorded date
        -----
        ERRORS
            * there are no custom errors
        """

        # returning string with recorded date
        return date.strftime(frmt)

    def get_day(self, date: str) -> dict:
        """
        DESCRIPTION
            * returns dictionary with information about study day
        -----
        ARGS
            * (required) date (str): date of day (format: "%d.%m.%Y")
        -----
        RETURNS
            * day (dict): dictionary with information about study day
        -----
        ERRORS
            * ValueError(): if there is problem with range of available dates
        """

        # checking correctness of date
        if not (self.__d(self.dates[0]) <= self.__d(date) <= self.__d(self.dates[1])):
            raise ValueError(
                f"The specified date {date} is outside the range of available dates: \
                [{self.dates[0]} - {self.dates[1]}]."
            )

        # getting raw day from grid
        if len(self.grid) == 6:
            # first case (per-week schedule)
            w = self.__d(date).weekday()
            if w < 6:
                raw_day = self.grid[w]
            else:
                raw_day = [[] for _ in range(7)]
        else:
            # second case (per-day schedule)
            d = abs((self.__d(date) - self.__d(self.dates[0])).days)
            raw_day = self.grid[d]

        # creating day
        day = {
            "group": self.group,
            "type": self.type,
            "is_session": self.is_session,
            "date": date,
            "day": [],
        }

        # filling day["day"]
        for index, section in enumerate(raw_day):
            event = {"time": self.TIME_SECTIONS[self.type][index], "subject": None}
            for raw_sbj in section:
                if (
                    self.__d(raw_sbj["dates"][0])
                    <= self.__d(date)
                    <= self.__d(raw_sbj["dates"][1])
                ):
                    event["subject"] = dict(raw_sbj)
                    del event["subject"]["dates"]
                    break
            day["day"].append(event)

        # returning dictionary with information about study day
        return day

    def get_week(self, date: str, ignore_range_err: bool = False) -> dict:
        """
        DESCRIPTION
            * returns dictionary with information about study week
        -----
        ARGS
            * (required) date (str): date of day (format: "%d.%m.%Y")
            * (optional) ignore_range_err (bool): error flag,
            by default is False - considers range of available dates, True - ignores range of available dates
        -----
        RETURNS
            * week (dict): dictionary with information about study week
        -----
        ERRORS
            * ValueError(): if there is problem with range of available dates
        """

        # converting date
        date = self.__d(date)

        # creating list with dates
        weekframe = []
        weekday = date.weekday()
        for i in range(7):
            weekframe.append(self.__s(date - timedelta(days=weekday - i)))

        # creating week
        week = {
            "group": self.group,
            "type": self.type,
            "is_session": self.is_session,
            "dates": [weekframe[0], weekframe[-1]],
            "week": [],
        }

        # filling week["week"]
        for date in weekframe:
            try:
                subjects = self.get_day(date)["day"]
            except ValueError as e:
                if ignore_range_err:
                    subjects = []
                else:
                    raise e
            week["week"].append({"date": date, "day": subjects})

        # returning dictionary with information about study week
        return week


if __name__ == "__main__":
    pass
