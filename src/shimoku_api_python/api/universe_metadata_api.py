from ..async_execution_pool import async_auto_call_manager, ExecutionPoolContext
from ..resources.universe import Universe
from typing import List, Dict

import logging
from ..execution_logger import logging_before_and_after
logger = logging.getLogger(__name__)


class UniverseMetadataApi:
    """
    This class is used to interact with the Universe metadata API.
    """
    @logging_before_and_after(logging_level=logger.debug)
    def __init__(self, api_client, execution_pool_context: ExecutionPoolContext):
        self.epc = execution_pool_context
        self._api_client = api_client

    @async_auto_call_manager(execute=True)
    @logging_before_and_after(logging_level=logger.info)
    async def create_universe_api_key(self, uuid: str, description: str):
        universe = Universe(api_client=self._api_client, uuid=uuid)
        return await universe.create_universe_api_key(description)

    @async_auto_call_manager(execute=True)
    @logging_before_and_after(logging_level=logger.info)
    async def get_universe_api_keys(self, uuid: str) -> List[Dict]:
        universe = Universe(api_client=self._api_client, uuid=uuid)
        return await universe.get_universe_api_keys()

    @async_auto_call_manager(execute=True)
    @logging_before_and_after(logging_level=logger.info)
    async def get_universe_workspaces(self, uuid: str) -> List[Dict]:
        universe = Universe(api_client=self._api_client, uuid=uuid)
        return [b.cascade_to_dict() for b in await universe.get_businesses()]

    @async_auto_call_manager(execute=True)
    @logging_before_and_after(logging_level=logger.info)
    async def get_universe_activity_templates(self, uuid: str) -> List[Dict]:
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


