from django.contrib.auth.models import User as djUser
from main.models import HistoryLog


class LogsWriter:
    """
    class for interacting with HistoryLog model in database,
    adds the history of user's:
      * authorizations
      * searches
      * exports
    """

    @staticmethod
    def auth(user: djUser) -> None:
        """ adds history of user authorizations to system """

        # TODO: localization
        HistoryLog.objects.create(
            user=user,
            action="is logged in"
        )

    @staticmethod
    def search(user: djUser) -> None:
        """ adds history of user searches in system """

        # TODO: add "search" log function logic
        pass

    @staticmethod
    def export(user: djUser) -> None:
        """ adds history of user exports in system """

        # TODO: add "export" log function logic
        pass


if __name__ == "__main__":
    pass
