""""""

from abc import ABC

from shimoku_api_python.api.explorer_api import UniverseExplorerApi


class UniverseMetadataApi(UniverseExplorerApi, ABC):
    """
    """
    def __init__(self, api_client):
        self.api_client = api_client
