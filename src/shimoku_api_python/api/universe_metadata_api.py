""""""

from abc import ABC

from shimoku_api_python.api.explorer_api import UniverseExplorerApi
from shimoku_api_python.async_execution_pool import async_auto_call_manager, ExecutionPoolContext

import logging
from shimoku_api_python.execution_logger import logging_before_and_after
logger = logging.getLogger(__name__)


class UniverseMetadataApi(ABC):
    """
    """
    @logging_before_and_after(logging_level=logger.debug)
    def __init__(self, api_client, execution_pool_context: ExecutionPoolContext):

        self.universe_explorer_api = UniverseExplorerApi(api_client)

        self.get_universe_businesses = async_auto_call_manager(execute=True)(self.universe_explorer_api.get_universe_businesses)
        self.get_universe_app_types = async_auto_call_manager(execute=True)(self.universe_explorer_api.get_universe_app_types)

        self.epc = execution_pool_context


