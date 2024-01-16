from typing import Optional, List, Tuple

from ..base_resource import Resource
from .business import Business
from .activity_template import ActivityTemplate
from ..client import ApiClient

import logging
from ..execution_logger import logging_before_and_after, log_error

logger = logging.getLogger(__name__)


class Universe(Resource):
    resource_type = 'universe'

    @logging_before_and_after(logger.debug)
    def __init__(self, api_client: ApiClient, uuid: str):

        super().__init__(api_client=api_client, uuid=uuid, children=[Business, ActivityTemplate])

    @logging_before_and_after(logger.debug)
    async def create_universe_api_key(self, description: str):
        endpoint = self._base_resource.base_url + f'universe/{self._base_resource.id}/apiKey'

        params = dict(
            userType='ADMIN',
            enabled=True,
            description=description
        )

        return await self._base_resource.api_client.query_element(
            method='POST', endpoint=endpoint,
            **{'body_params': params}
        )

    @logging_before_and_after(logger.debug)
    async def get_universe_api_keys(self):
        endpoint = self._base_resource.base_url + f'universe/{self._base_resource.id}/apiKeys'

        return (await self._base_resource.api_client.query_element(
            method='GET', endpoint=endpoint,
        ))['items']

    # Business methods
    @logging_before_and_after(logger.debug)
    async def create_business(self, name: str, theme: Optional[dict] = None) -> Business:
        if self._base_resource.api_client.playground:
            log_error(logger, 'Cannot create business in local environment', RuntimeError)
        return await self._base_resource.create_child(Business, alias=name, theme=theme if theme else {})

    @logging_before_and_after(logger.debug)
    async def update_business(self, uuid: Optional[str] = None, name: Optional[str] = None, **params):
        if params.get('new_name') is not None:
            params['name'] = params.pop('new_name')
            params['new_alias'] = True
        if self._base_resource.api_client.playground:
            uuid, name = 'local', None
        return await self._base_resource.update_child(Business, uuid=uuid, alias=name, **params)

    @logging_before_and_after(logger.debug)
    async def get_business(self, uuid: Optional[str] = None, name: Optional[str] = None) -> Optional[Business]:
        if self._base_resource.api_client.playground:
            uuid, name = 'local', None
        return await self._base_resource.get_child(Business, uuid, name)

    @logging_before_and_after(logger.debug)
    async def get_businesses(self) -> List[Business]:
        return await self._base_resource.get_children(Business)

    @logging_before_and_after(logger.debug)
    async def delete_business(self, uuid: Optional[str] = None, name: Optional[str] = None):
        if self._base_resource.api_client.playground:
            log_error(logger, 'Cannot delete local business', RuntimeError)
        return await self._base_resource.delete_child(Business, uuid, name)

    # Activity template methods
    @logging_before_and_after(logger.debug)
    async def get_activity_template(
            self, uuid: Optional[str] = None, name_version: Optional[Tuple[str, str]] = None
    ) -> Optional[ActivityTemplate]:
        return await self._base_resource.get_child(ActivityTemplate, uuid, name_version)

    @staticmethod
    @logging_before_and_after(logging_level=logger.debug)
    def interpret_version(version: str) -> list:
        """ Interpret a version string by appending '0' to each section for sorting. """
        numbers = '0123456789'
        if not version:
            return [0, 0, 0]

        def interpret_version_section(section: str) -> list:
            """ Interpret a version section, considering non-numeric characters as earlier. """
            res_section = []
            number = ''
            for c in section:
                if c in numbers:
                    number += c
                else:
                    if number:
                        res_section.append(ord('z') + int(number))
                        number = ''
                    res_section.append(ord(c))
            if number:
                res_section.append(ord('z') + int(number))
            return res_section

        return [interpret_version_section(section + '0') for section in version.split('.')]

    @logging_before_and_after(logger.debug)
    async def get_activity_templates(self) -> List[ActivityTemplate]:
        templates = await self._base_resource.get_children(ActivityTemplate)
        return sorted(templates, key=lambda t: [t['name']] + self.interpret_version(t['version']))
