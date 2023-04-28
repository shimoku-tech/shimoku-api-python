from typing import List, Dict, Optional, Callable, Union, TYPE_CHECKING
from shimoku_api_python.base_resource import Resource

if TYPE_CHECKING:
    from shimoku_api_python.base_resource import Business, Dashboard
    from shimoku_api_python.api.app_metadata_api import App

import logging
from shimoku_api_python.execution_logger import logging_before_and_after, log_error
logger = logging.getLogger(__name__)


class Role(Resource):

    resource_type = 'role'
    alias_field = 'role'
    plural = 'roles'

    def __init__(self, parent: Union['Business', 'Dashboard', 'App'], uuid: Optional[str] = None,
                 alias: Optional[str] = None):
        super().__init__(parent=parent, uuid=uuid, check_params_before_creation=['role'])

        self._base_resource.params = {
            'permission': 'READ',
            'resource': 'BUSINESS_INFO',
            'target': 'GROUP',
            'role': alias,
        }

    async def delete(self):
        return await self._base_resource.delete()

    async def update(self):
        return await self._base_resource.update()

    def set_params(self, permission: Optional[str] = None, resource: Optional[str] = None,
                   target: Optional[str] = None, role: Optional[str] = None):

        if permission:
            valid_permissions = ['READ', 'WRITE']
            if permission and permission not in valid_permissions:
                log_error(logger, f'{permission} is not a valid value for permission, '
                                  f'the valid values are: {valid_permissions}', ValueError)
            self._base_resource.params['permission'] = permission
        if resource:
            valid_resources = ['DATA', 'DATA_EXECUTION', 'USER_MANAGEMENT', 'BUSINESS_INFO']
            if resource not in valid_resources:
                log_error(logger, f'{resource} is not a valid value for resource, '
                                  f'the valid values are: {valid_resources}', ValueError)
            self._base_resource.params['resource'] = resource
        if target:
            valid_targets = ['GROUP', 'USER']
            if target and target not in valid_targets:
                log_error(logger, f'{target} is not a valid value for target, '
                                  f'the valid values are: {valid_targets}', ValueError)
            self._base_resource.params['target'] = target
        if role:
            self._base_resource.params['role'] = role
