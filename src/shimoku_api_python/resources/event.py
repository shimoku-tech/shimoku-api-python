from typing import Optional, TYPE_CHECKING

from ..base_resource import Resource
if TYPE_CHECKING:
    from .business import Business

import logging
from ..execution_logger import logging_before_and_after
logger = logging.getLogger(__name__)


class Event(Resource):
    """ Event resource class """

    resource_type = 'event'
    plural = 'events'

    @logging_before_and_after(logger.debug)
    def __init__(self, parent: 'Business', uuid: Optional[str] = None):

        params = dict(
            type='NO_EVENT',
            resourceId=None,
            content={},
        )

        super().__init__(
            parent=parent, uuid=uuid, params=params,
            params_to_serialize=['content']
        )
