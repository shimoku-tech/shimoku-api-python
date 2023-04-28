from typing import Optional, List

from ..base_resource import Resource
from .business import Business
from ..client import ApiClient

import logging
from ..execution_logger import logging_before_and_after
logger = logging.getLogger(__name__)


class Universe(Resource):
    resource_type = 'universe'

    @logging_before_and_after(logger.debug)
    def __init__(self, api_client: ApiClient, uuid: str):

        super().__init__(api_client=api_client, uuid=uuid, children=[Business])

    # Business methods
    @logging_before_and_after(logger.debug)
    async def create_business(self, name: str, theme: Optional[dict] = None) -> Business:
        return await self._base_resource.create_child(Business, alias=name, theme=theme if theme else {})

    @logging_before_and_after(logger.debug)
    async def update_business(self, uuid: Optional[str] = None, name: Optional[str] = None, **params):
        if 'new_name' in params:
            params['new_alias'] = params.pop('new_name')
        return await self._base_resource.update_child(Business, uuid=uuid, alias=name, **params)

    @logging_before_and_after(logger.debug)
    async def get_business(self, uuid: Optional[str] = None, name: Optional[str] = None) -> Optional[Business]:
        return await self._base_resource.get_child(Business, uuid, name)

    @logging_before_and_after(logger.debug)
    async def get_businesses(self) -> List[Business]:
        return await self._base_resource.get_children(Business)

    @logging_before_and_after(logger.debug)
    async def delete_business(self, uuid: Optional[str] = None, name: Optional[str] = None):
        return await self._base_resource.delete_child(Business, uuid, name)
