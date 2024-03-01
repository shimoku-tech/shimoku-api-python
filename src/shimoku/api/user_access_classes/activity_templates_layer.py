from typing import Optional

from shimoku.api.resources.universe import Universe

import logging
from shimoku.execution_logger import ClassWithLogging

logger = logging.getLogger(__name__)


class ActivityTemplatesLayer(ClassWithLogging):
    """
    This class is used to interact with the API at the activity template metadata level.
    """

    def __init__(self, universe: "Universe"):
        self._universe = universe

    async def get_activity_template(
        self, uuid: Optional[str] = None, name_version: Optional[tuple[str, str]] = None
    ) -> dict:
        """Get a workspace
        :param name_version: name and version of the activity template
        :param uuid: UUID of the activity template
        """
        return (
            await self._universe.get_activity_template(
                uuid=uuid, name_version=name_version
            )
        ).cascade_to_dict()
