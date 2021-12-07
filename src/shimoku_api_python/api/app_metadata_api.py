""""""

from abc import ABC
from typing import List, Dict, Union

from shimoku_api_python.api.explorer_api import AppExplorerApi


class AppMetadataApi(AppExplorerApi, ABC):
    """
    """

    def __init__(self, api_client):
        self.api_client = api_client

    def has_app_report(self, business_id: str, app_id: str) -> bool:
        """"""
        reports: List[str] = (
            self.get_app_reports(
                business_id=business_id,
                app_id=app_id,
            )
        )
        if reports:
            return True
        else:
            return False

    def get_app_by_type(
        self, business_id: str, app_type_id: str,
    ) -> Union[Dict, List[Dict]]:
        """
        :param business_id: business UUID
        :param app_type_id: appType UUID
        """
        apps: List[Dict] = self._get_business_apps(business_id=business_id)

        # Is expected to be a single item (Dict) but an App
        # could have several reports with the same name
        result: Union[Dict, List[Dict]] = {}
        for app in apps:
            if app['type']['id'] == app_type_id:
                if result:
                    if len(result) == 1:
                        result: List[Dict] = [result] + [app]
                    else:
                        result: List[Dict] = result + [app]
                else:
                    result: Dict = app
        return result

    def hide_title(
        self, business_id: str, app_id: str, hide_title: bool = True
    ) -> Dict:
        """Hide / show app title
        """
        app_data = {'hideTitle': hide_title}
        return (
            self.update_app(
                business_id=business_id,
                app_id=app_id,
                app_data=app_data,
            )
        )

    def show_title(self, business_id: str, app_id: str) -> Dict:
        return self.hide_title(
            business_id=business_id,
            app_id=app_id,
            hide_title=False,
        )
