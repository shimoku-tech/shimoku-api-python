""""""

from abc import ABC

from shimoku_api_python.api.explorer_api import UniverseExplorerApi
from shimoku_api_python.async_execution_pool import async_auto_call_manager

import logging
from shimoku_api_python.execution_logger import logging_before_and_after
logger = logging.getLogger(__name__)


class UniverseMetadataApi(UniverseExplorerApi, ABC):
    """
    """

    get_universe_businesses = async_auto_call_manager(execute=True)(UniverseExplorerApi.get_universe_businesses)
    get_universe_app_types = async_auto_call_manager(execute=True)(UniverseExplorerApi.get_universe_app_types)

    @logging_before_and_after(logging_level=logger.debug)
    def __init__(self, api_client):
        self.api_client = api_client



