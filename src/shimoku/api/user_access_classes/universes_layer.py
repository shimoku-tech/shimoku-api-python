from typing import Optional
from shimoku.api.resources.universe import Universe
from shimoku import ApiClient
from shimoku.exceptions import UniverseError

import logging
from shimoku.execution_logger import ClassWithLogging, log_error

logger = logging.getLogger(__name__)


class UniversesLayer(ClassWithLogging):
    """
    Class used to interact with the API at the universe level
    """

    _module_logger = logger
    _use_info_logging = True

    def __init__(self, api_client: ApiClient):
        self._api_client = api_client

    async def create_universe_api_key(self, uuid: str, description: str) -> dict:
        """
        Create a universe API key, this key has admin privileges.
        :param uuid: uuid of the universe
        :param description: description of the key
        """
        universe = Universe(api_client=self._api_client, uuid=uuid)
        return (await universe.create_universe_api_key(description)).cascade_to_dict()

    async def get_universe_api_keys(self, uuid: str) -> list[dict]:
        """
        Get the universe API keys.
        :param uuid: uuid of the universe
        """
        universe = Universe(api_client=self._api_client, uuid=uuid)
        return [
            universe_api_key.cascade_to_dict()
            for universe_api_key in await universe.get_universe_api_keys()
        ]

    async def delete_universe_api_key(self, uuid: str, api_key_uuid: str) -> bool:
        """
        Delete a universe API key.
        :param uuid: uuid of the universe
        :param api_key_uuid: uuid of the API key
        """
        universe = Universe(api_client=self._api_client, uuid=uuid)
        return await universe.delete_universe_api_key(api_key_uuid)

    async def get_universe_workspaces(self, uuid: str) -> list[dict]:
        """
        Get the universe workspaces.
        :param uuid: uuid of the universe
        """
        universe = Universe(api_client=self._api_client, uuid=uuid)
        return [b.cascade_to_dict() for b in await universe.get_businesses()]

    async def get_universe_activity_templates(self, uuid: str) -> list[dict]:
        """
        Get the universe activity templates as a list of dictionaries.
        :param uuid: uuid of the universe
        """
        universe = Universe(api_client=self._api_client, uuid=uuid)
        return [
            {
                "name": at["name"],
                "description": at["description"],
                "min_run_interval": at["minRunInterval"],
                "input_settings": [
                    {
                        "name": name,
                        "description": param["description"],
                        "datatype": param["datatype"],
                    }
                    for name, param in at["inputSettings"].items()
                    if isinstance(param, dict)
                ],
            }
            for at in await universe.get_activity_templates()
            if at["enabled"]
        ]

    async def get_universe_actions(self, uuid: Optional[str] = None) -> list[dict]:
        """
        Get the universe actions_execution as a list of dictionaries.
        :param uuid: uuid of the universe
        """
        if self._api_client.playground:
            uuid = "local"
        elif not uuid:
            log_error(
                logger,
                "If not in playground, a universe uuid is required",
                UniverseError,
            )
        universe = Universe(api_client=self._api_client, uuid=uuid)
        return [action.cascade_to_dict() for action in await universe.get_actions()]

    async def get_universe_action_templates(self, uuid: str) -> list[dict]:
        """
        Get the universe action templates as a list of dictionaries.
        :param uuid: uuid of the universe
        """
        universe = Universe(api_client=self._api_client, uuid=uuid)
        return [
            {
                "name": action_template["name"],
                "description": action_template["description"],
                "public": action_template["public"],
                "libraries": action_template["pythonLibraries"],
            }
            for action_template in await universe.get_action_templates()
        ]
