from shimoku.api.resources.universe import Universe
from shimoku import ApiClient

import logging
from shimoku.execution_logger import ClassWithLogging
logger = logging.getLogger(__name__)


class UniversesLayer(ClassWithLogging):
    """
    Class used to interact with the API at the universe level
    """

    _module_logger = logger
    _use_info_logging = True

    def __init__(
        self, api_client: ApiClient
    ):
        self._api_client = api_client

    async def create_universe_api_key(
        self, uuid: str, description: str
    ) -> dict:
        """
        Create a universe API key, this key has admin privileges.
        :param uuid: uuid of the universe
        :param description: description of the key
        """
        universe = Universe(api_client=self._api_client, uuid=uuid)
        return await universe.create_universe_api_key(description)

    async def get_universe_api_keys(
        self, uuid: str
    ) -> list[dict]:
        """
        Get the universe API keys.
        :param uuid: uuid of the universe
        """
        universe = Universe(api_client=self._api_client, uuid=uuid)
        return await universe.get_universe_api_keys()

    async def delete_universe_api_key(
        self, uuid: str, api_key_uuid: str
    ) -> bool:
        """
        Delete a universe API key.
        :param uuid: uuid of the universe
        :param api_key_uuid: uuid of the API key
        """
        universe = Universe(api_client=self._api_client, uuid=uuid)
        return await universe.delete_universe_api_key(api_key_uuid)

    async def get_universe_workspaces(
        self, uuid: str
    ) -> list[dict]:
        """
        Get the universe workspaces.
        :param uuid: uuid of the universe
        """
        universe = Universe(api_client=self._api_client, uuid=uuid)
        return [b.cascade_to_dict() for b in await universe.get_businesses()]

    async def get_universe_activity_templates(
        self, uuid: str
    ) -> list[dict]:
        """
        Get the universe activity templates as a list of dictionaries.
        :param uuid: uuid of the universe
        """
        universe = Universe(api_client=self._api_client, uuid=uuid)
        return [{
            'name': at['name'], 'description': at['description'],
            'min_run_interval': at['minRunInterval'],
            'input_settings': [{
                'name': name,
                'description': param['description'],
                'datatype': param['datatype']
            } for name, param in at['inputSettings'].items() if isinstance(param, dict)]
        } for at in await universe.get_activity_templates() if at['enabled']]
