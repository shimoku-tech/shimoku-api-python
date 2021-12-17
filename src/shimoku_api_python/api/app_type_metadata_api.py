""""""

from abc import ABC
from typing import Dict

from shimoku_api_python.api.explorer_api import AppTypeExplorerApi


class AppTypeMetadataApi(AppTypeExplorerApi, ABC):
    """
    """
    def __init__(self, api_client):
        self.api_client = api_client

    def rename_apps_types(self, app_type_id: str, new_name: str) -> Dict:
        return self.update_app_type(
            app_type_id=app_type_id,
            app_type_metadata={'name': new_name}
        )

    def get_app_type_by_name(self, name: str) -> Dict:
        app_types: List[Dict] = self.get_universe_app_types()
        app_type: Dict = [
            app_type
            for app_type in app_types
            if app_type['name'] == name
        ]

        if app_type:
            assert len(app_type) == 1
            return app_type[0]
        else:
            return {}
