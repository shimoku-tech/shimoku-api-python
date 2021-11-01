""""""

from abc import ABC
from typing import List, Dict

import datetime as dt

from shimoku_api_python.api.explorer_api import AppExplorerApi


class AppMetadataApi(AppExplorerApi, ABC):
    """
    """

    def __init__(self, api_client):
        self.api_client = api_client

    def has_app_report(self, app_id: str) -> bool:
        """"""
        reports: List[str] = self.get_app_all_reports(app_id)
        if reports:
            return True
        else:
            return False

    def get_report_last_update(self, app_id: str) -> dt.datetime:
        """"""
        app: Dict = self.get_app(app_id)
        # TODO check it returns dt.date
        return app_id['updatedAt']

    def change_app_name(
        self, app_id: str, new_app_name: str,
    ) -> None:
        """Update path name
        """
        app_data = {'name': new_app_name}
        self.update_app(
            app_id=app_id,
            app_data=app_data,
        )

    def change_hide_title(self, app_id: str, hide_title: bool = True) -> None:
        """Hide / show app title

        See https://trello.com/c/8e11jso4/ for further info
        """
        app_data = {'hideTitle': hide_title}
        self.update_app(
            app_id=app_id,
            app_data=app_data,
        )

    # TODO sigue siendo una gran duda para mi como gestionaremos los AppType!!
    def get_app_apptype(self, app_id: str) -> Dict:
        """Given an app retrieve its `AppType`
        :param app_id: app UUID
        """
        raise NotImplemented
