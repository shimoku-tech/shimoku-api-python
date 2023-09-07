from typing import Dict, Optional, Tuple
from abc import ABC

from ..async_execution_pool import async_auto_call_manager, ExecutionPoolContext
from ..resources.universe import Universe

import logging
from ..execution_logger import logging_before_and_after
logger = logging.getLogger(__name__)


class ActivityTemplateMetadataApi(ABC):
    """
    """
    @logging_before_and_after(logging_level=logger.debug)
    def __init__(self, universe: 'Universe', execution_pool_context: ExecutionPoolContext):
        self._universe = universe
        self.epc = execution_pool_context

    @async_auto_call_manager(execute=True)
    @logging_before_and_after(logging_level=logger.info)
    async def get_activity_template(
        self, uuid: Optional[str] = None, name_version: Optional[Tuple[str, str]] = None
    ) -> Dict:
        """Get a workspace
        :param name_version: name and version of the activity template
        :param uuid: UUID of the activity template
        """
        return (await self._universe.get_activity_template(uuid=uuid, name_version=name_version)).cascade_to_dict()
