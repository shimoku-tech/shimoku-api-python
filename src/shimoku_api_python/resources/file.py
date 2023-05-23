from typing import Dict, Optional, TYPE_CHECKING

from ..utils import create_normalized_name
from ..base_resource import Resource
if TYPE_CHECKING:
    from .app import App

import logging
from ..execution_logger import logging_before_and_after
logger = logging.getLogger(__name__)


class File(Resource):
    """ Report resource class """

    resource_type = 'file'
    plural = 'files'
    alias_field = 'name'

    @logging_before_and_after(logger.debug)
    def __init__(self, parent: 'App', uuid: Optional[str] = None, alias: Optional[str] = None,
                 db_resource: Optional[Dict] = None):

        params = dict(
            name=alias,
            fileName=create_normalized_name(alias) if alias else None,
            url='',
            contentType='',
        )

        super().__init__(parent=parent, uuid=uuid, db_resource=db_resource, params=params,
                         check_params_before_creation=['name'])

    @logging_before_and_after(logger.debug)
    async def delete(self):
        """ Delete the report """
        return await self._base_resource.delete()
