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
            app_type_data={'name': new_name}  # TODO check 'name' is correct
        )
