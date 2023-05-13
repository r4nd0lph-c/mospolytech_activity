# --------------------------------------------------------------------------------------------------------------------#
# ███╗   ███╗ ██████╗ ███████╗██████╗  ██████╗ ██╗  ██╗   ██╗████████╗███████╗ ██████╗██╗  ██╗     █████╗ ██████╗ ██╗ #
# ████╗ ████║██╔═══██╗██╔════╝██╔══██╗██╔═══██╗██║  ╚██╗ ██╔╝╚══██╔══╝██╔════╝██╔════╝██║  ██║    ██╔══██╗██╔══██╗██║ #
# ██╔████╔██║██║   ██║███████╗██████╔╝██║   ██║██║   ╚████╔╝    ██║   █████╗  ██║     ███████║    ███████║██████╔╝██║ #
# ██║╚██╔╝██║██║   ██║╚════██║██╔═══╝ ██║   ██║██║    ╚██╔╝     ██║   ██╔══╝  ██║     ██╔══██║    ██╔══██║██╔═══╝ ██║ #
# ██║ ╚═╝ ██║╚██████╔╝███████║██║     ╚██████╔╝███████╗██║      ██║   ███████╗╚██████╗██║  ██║    ██║  ██║██║     ██║ #
# ╚═╝     ╚═╝ ╚═════╝ ╚══════╝╚═╝      ╚═════╝ ╚══════╝╚═╝      ╚═╝   ╚══════╝ ╚═════╝╚═╝  ╚═╝    ╚═╝  ╚═╝╚═╝     ╚═╝ #
# author: https://t.me/rand0lphc                                                                                      #
# ------------------------------------------------------------------------------------------------------------------- #


import json
from hashlib import md5

import requests


class API:
    """
    DESCRIPTION
        * API for working with services of Moscow Polytechnic University
        * https://mospolytech.ru/en/
    -----
    ATTRIBUTES
        * (instance) headers (dict): additional context about requests
    -----
    ARGS
        * (optional) user_agent (str): string that lets servers identify application,
        by default is __DEFAULT_USER_AGENT
        * (optional) hash_salt_path (str): string that is required for some requests,
        by default is __DEFAULT_HASH_SALT_PATH
    -----
    METHODS
        * get_groups() -> list[str]
        * get_students(groups: list = None) -> dict
        * get_semester() -> dict
        * get_session() -> dict
        * get_schedule(group: str, is_session: bool = False) -> dict
    """

    # attributes for class operations
    __DEFAULT_USER_AGENT = (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/86.0.4240.75 Safari/537.36"
    )
    __DEFAULT_HASH_SALT_PATH = "hash_salt.txt"
    __URLS = {
        "referer": "https://rasp.dmami.ru/",
        "groups": "https://rasp.dmami.ru/groups-list.json",
        "students": "https://e.mospolytech.ru/old/lk_api_mapp.php",
        "semester": "https://rasp.dmami.ru/semester.json",
        "session": "https://rasp.dmami.ru/session-file.json",
        "schedule": "https://rasp.dmami.ru/site/group",
    }

    def __init__(
        self,
        user_agent: str = __DEFAULT_USER_AGENT,
        hash_salt_path: str = __DEFAULT_HASH_SALT_PATH,
    ) -> None:
        """
        DESCRIPTION
            * initializes API object
        -----
        ARGS
            * (optional) user_agent (str): string that lets servers identify application,
            by default is __DEFAULT_USER_AGENT
            * (optional) hash_salt_path (str): string that is required for some requests,
            by default is __DEFAULT_HASH_SALT_PATH
        -----
        RETURNS
            * there is no return
        -----
        ERRORS
            * there are no custom errors
        """

        # setting headers
        self.headers = {"referer": self.__URLS["referer"], "user-agent": user_agent}

        # setting hash salt
        with open(hash_salt_path, "r", encoding="utf-8") as f:
            self.__hash_salt = f.readline()

    @staticmethod
    def __check_status_code(code: int) -> None:
        """
        DESCRIPTION
            * checks correctness of response status code
        -----
        ARGS
            * (required) code (int): response status code
        -----
        RETURNS
            * there is no return
        -----
        ERRORS
            * ConnectionError(): if there is problem with connection
        """

        # checking status code
        if code != 200:
            raise requests.ConnectionError(f"Expected status code 200, but got {code}.")

    def __create_token(self, group: str) -> str:
        """
        DESCRIPTION
            * creates token (md5-str object) for given group and returns it
        -----
        ARGS
            * (required) group (str): name of group
        -----
        RETURNS
            * token (str): token (md5-str object) for given group
        -----
        ERRORS
            * there are no custom errors
        """

        # creating token (md5-hash object)
        string = group + self.__hash_salt
        token = md5(md5(string.encode()).hexdigest().encode())

        # returning token (md5-str object) for given group
        return token.hexdigest()

    def __make_request(self, url: str) -> str:
        """
        DESCRIPTION
            * makes request to given url and returns content
        -----
        ARGS
            * (required) url (str): url for request
        -----
        RETURNS
            * content (str): decoded content of response
        -----
        ERRORS
            * ConnectionError(): if there is problem with connection
        """

        # making request
        r = requests.get(url=url, headers=self.headers)

        # checking status code
        self.__check_status_code(r.status_code)

        # decoding content
        content = r.content.decode("utf-8")

        # returning decoded content of response
        return content

    @staticmethod
    def __parse_grid(grid_source: dict) -> list[list]:
        """
        DESCRIPTION
            * modifies given grid into form comfortable for interactions and returns it
        -----
        ARGS
            * (required) grid_source (dict): grid object contained in content of some requests
        -----
        RETURNS
            * grid_modified (list[list]): modified grid
        -----
        ERRORS
            * there are no custom errors
        """

        # creating modified grid
        grid_modified = []
        for key_i in grid_source:
            day = []
            for key_j in grid_source[key_i]:
                section = []
                for obj in grid_source[key_i][key_j]:
                    # preparing link for event
                    link = obj["e_link"]
                    if link is None:
                        dirty_link = obj["auditories"][0]["title"]
                        if dirty_link[0:7] == "<a href":
                            link = dirty_link[9:].split('"')[0]
                    # preparing dates for event
                    if len(key_i) == 10:
                        dates = [".".join(d.split("-")[::-1]) for d in [key_i] * 2]
                    else:
                        dates = [
                            ".".join(d.split("-")[::-1]) for d in [obj["df"], obj["dt"]]
                        ]
                    # creating event
                    event = {
                        "title": obj["sbj"].strip(),
                        "type": obj["type"],
                        "teachers": [
                            " ".join(t.strip().split())
                            for t in obj["teacher"].split(",")
                        ],
                        "location": obj["location"].strip(),
                        "rooms": [
                            r.strip().replace("_", "") for r in obj["shortRooms"]
                        ],
                        "link": link,
                        "dates": dates,
                    }
                    # clearing event fields
                    event["teachers"] = list(
                        filter(lambda t: t != "", event["teachers"])
                    )
                    # appending
                    section.append(event)
                day.append(section)
            grid_modified.append(day)

        # returning modified grid
        return grid_modified

    def get_groups(self) -> list[str]:
        """
        DESCRIPTION
            * gets sorted list of group names that are existing and returns it
        -----
        ARGS
            * there are no args
        -----
        RETURNS
            * groups (list[str]): sorted list of group names
        -----
        ERRORS
            * ConnectionError(): if there is problem with connection
        """

        # making complex request
        data = json.loads(self.__make_request(self.__URLS["groups"]))

        # returning sorted list of group names
        return sorted([name for name in data["groups"]])

    def get_students(self, groups: list = None) -> dict:
        """
        DESCRIPTION
            * gets sorted dict of students for given groups and returns it
        -----
        ARGS
            * (optional) groups (list[str]): sorted list of group names,
            by default is None - search across all groups
        -----
        RETURNS
            * students (dict): sorted dict of students for given groups
        -----
        ERRORS
            * ConnectionError(): if there is problem with connection
        """

        # getting group names
        if groups is None:
            groups = self.get_groups()

        # creating students
        students = {}
        for group in sorted(groups):
            # creating token
            token = self.__create_token(group)
            # making complex request
            url = (
                self.__URLS["students"]
                + f"?group={group.replace(' ', '%20')}&token={token}"
            )
            batch = json.loads(self.__make_request(url))
            batch = sorted(batch, key=lambda item: item["fio"])
            # adding batch to dict of students
            students[group] = [
                {"guid": item["guid"], "student": item["fio"]} for item in batch
            ]

        # returning sorted dict of students for given groups
        return students

    def get_semester(self) -> dict:
        """
        DESCRIPTION
            * gets sorted dictionary containing semester information and returns it
        -----
        ARGS
            * there are no args
        -----
        RETURNS
            * semester (dict): sorted dictionary containing semester information
        -----
        ERRORS
            * ConnectionError(): if there is problem with connection
        """

        # making complex request
        data = json.loads(self.__make_request(self.__URLS["semester"]))

        # creating semester
        semester = {}
        for obj_key in data["contents"]:
            obj = data["contents"][obj_key]
            semester[obj_key] = {
                "type": "evening" if obj["group"]["evening"] else "morning",
                "dates": [
                    ".".join(d.split("-")[::-1])
                    for d in [obj["group"]["dateFrom"], obj["group"]["dateTo"]]
                ],
                "grid": self.__parse_grid(obj["grid"]),
            }

        # returning sorted dictionary containing semester information
        return dict(sorted(semester.items()))

    def get_session(self) -> dict:
        """
        DESCRIPTION
            * gets sorted dictionary containing session information and returns it
        -----
        ARGS
            * there are no args
        -----
        RETURNS
            * session (dict): sorted dictionary containing session information
        -----
        ERRORS
            * ConnectionError(): if there is problem with connection
        """

        # making complex request
        data = json.loads(self.__make_request(self.__URLS["session"]))

        # creating session
        session = {}
        for obj in data["contents"]:
            session[obj["group"]["title"]] = {
                "type": "evening" if obj["group"]["evening"] else "morning",
                "dates": [
                    ".".join(d.split("-")[::-1])
                    for d in [obj["group"]["dateFrom"], obj["group"]["dateTo"]]
                ],
                "grid": self.__parse_grid(obj["grid"]),
            }

        # returning sorted dictionary containing session information
        return dict(sorted(session.items()))

    def get_schedule(self, group: str, is_session: bool = False) -> dict:
        """
        DESCRIPTION
            * gets dictionary containing schedule information and returns it
        -----
        ARGS
            * (required) group (str): name of group
            * (optional) is_session (bool): session flag,
            by default is False - try to get general schedule, True - try to get session schedule
        -----
        RETURNS
            * schedule (dict): dictionary containing schedule information
        -----
        ERRORS
            * ConnectionError(): if there is problem with connection
            * ValueError(): if there is problem with response content
        """

        # making complex request
        url = (
            self.__URLS["schedule"]
            + f"?group={group.replace(' ', '%20')}&session={1 if is_session else 0}"
        )
        content = self.__make_request(url)

        # checking correctness of response (1)
        SCHEDULE_NOT_EXIST = "Еще не готово расписание для группы"
        if content == SCHEDULE_NOT_EXIST:
            raise ValueError(f"The schedule for the '{group}' group does not exist.")

        # loading content to data dict
        data = json.loads(content)

        # checking correctness of response (2)
        SCHEDULE_EMPTY = "Не нашлось расписание для группы"
        if "message" in data:
            if data["message"] == SCHEDULE_EMPTY:
                raise ValueError(f"The schedule for the '{group}' group is empty.")

        # creating schedule
        schedule = {
            "group": group,
            "type": "evening" if data["group"]["evening"] else "morning",
            "is_session": data["isSession"],
            "dates": [
                ".".join(d.split("-")[::-1])
                for d in [data["group"]["dateFrom"], data["group"]["dateTo"]]
            ],
            "grid": self.__parse_grid(data["grid"]),
        }

        # returning dictionary containing schedule information
        return schedule


if __name__ == "__main__":
    pass
