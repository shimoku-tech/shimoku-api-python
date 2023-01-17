""""""

from abc import ABC

from shimoku_api_python.api.explorer_api import UniverseExplorerApi

import logging
from shimoku_api_python.execution_logger import logging_before_and_after
logger = logging.getLogger(__name__)


class UniverseMetadataApi(UniverseExplorerApi, ABC):
    """
    """

    @logging_before_and_after(logging_level=logger.debug)
    def __init__(self, api_client):
        self.api_client = api_client
