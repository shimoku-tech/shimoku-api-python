from typing import Optional, TYPE_CHECKING

from shimoku.api.base_resource import Resource
from shimoku.utils import EventType

if TYPE_CHECKING:
    from shimoku.api.resources.business import Business

import logging

logger = logging.getLogger(__name__)


class Event(Resource):
    """Event resource class"""

    _module_logger = logger
    resource_type = "event"
    plural = "events"

    def __init__(self, parent: "Business", uuid: Optional[str] = None):
        params = dict(
            authResourceType="business",
            mainAuthResourceId=parent['id'],
            type=EventType.TEST.value,
            resourceId=None,
            content={},
        )

        super().__init__(
            parent=parent, uuid=uuid, params=params, params_to_serialize=["content"]
        )
