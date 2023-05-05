from typing import List, Dict, Optional, Type, TYPE_CHECKING

from ..base_resource import Resource, ResourceCache
from ..utils import create_normalized_name
from .activity import Activity
from .role import Role, create_role, get_role, get_roles, delete_role
from .report import Report

if TYPE_CHECKING:
    from .business import Business

import logging
from ..execution_logger import logging_before_and_after
logger = logging.getLogger(__name__)


class App(Resource):
    """ App resource class """

    resource_type = 'app'
    alias_field = 'name'
    plural = 'apps'

    @logging_before_and_after(logger.debug)
    def __init__(self, parent: 'Business', uuid: Optional[str] = None, alias: Optional[str] = None):

        normalized_name: Optional[str] = None
        if alias:
            normalized_name: str = create_normalized_name(alias)

        params = dict(
            name=alias,
            order=0,
            normalizedName=normalized_name,
            hideTitle=True,
            hidePath=False,
            showBreadcrumb=False,
            showHistoryNavigation=False,
        )

        super().__init__(parent=parent, uuid=uuid, children=[Role, Activity, Report],
                         check_params_before_creation=['name'], params=params)

    @logging_before_and_after(logger.debug)
    async def delete(self):
        """ Delete the app """
        return await self._base_resource.delete()

    @logging_before_and_after(logger.debug)
    async def update(self):
        """ Update the app """
        return await self._base_resource.update()

    # Activity methods
    @logging_before_and_after(logger.debug)
    async def create_activity(self, name: str, settings: Optional[Dict[str, str]] = None) -> Activity:
        return await self._base_resource.create_child(Activity, alias=name, settings=settings)

    @logging_before_and_after(logger.debug)
    async def update_activity(self, uuid: Optional[str] = None, name: Optional[str] = None, **params) -> Activity:
        if 'new_name' in params:
            params['new_alias'] = params.pop('new_name')
        return await self._base_resource.update_child(Activity, uuid=uuid, alias=name, **params)

    @logging_before_and_after(logger.debug)
    async def get_activity(self, uuid: Optional[str] = None, name: Optional[str] = None) -> Optional[Activity]:
        result = await self._base_resource.get_child(Activity, uuid, name)
        if not result:
            logger.warning(f'Activity {name if name else uuid} not found')
        return result

    @logging_before_and_after(logger.debug)
    async def get_activities(self) -> List[Activity]:
        return await self._base_resource.get_children(Activity)

    @logging_before_and_after(logger.debug)
    async def delete_activity(self, uuid: Optional[str] = None, name: Optional[str] = None):
        return await self._base_resource.delete_child(Activity, uuid, name)

    # Report methods
    @logging_before_and_after(logger.debug)
    async def create_report(self, report_class: Type[Report], **params) -> Report:
        """ Creates a child of a given report class.
        :param report_class: The class of the report to create.
        :param params: The parameters of the report to create.
        :return: The created resource.
        """
        report_cache: ResourceCache = self._base_resource.children[Report]

        report = report_class(parent=self)
        if 'properties' in params:
            report.set_properties(**params.pop('properties'))

        report.set_params(**params)

        return await report_cache.add(report)

    @logging_before_and_after(logger.debug)
    async def get_report(self, uuid: Optional[str] = None) -> Optional[Report]:
        """ Gets a report.
        :param uuid: The UUID of the report to get.
        :return: The resource.
        """
        return await self._base_resource.get_child(Report, uuid)

    @logging_before_and_after(logger.debug)
    async def get_reports(self) -> List[Report]:
        """ Gets all the reports of the app."""
        return await self._base_resource.get_children(Report)

    @logging_before_and_after(logger.debug)
    async def update_report(self, uuid: Optional[str] = None, **params):
        """ Updates a report.
        :param uuid: The UUID of the report to update.
        :param params: The parameters of the report to update.
        """
        report = await self.get_report(uuid)

        if 'properties' in params:
            report.set_properties(**params.pop('properties'))

        report.set_params(**params)
        await report.update()

    @logging_before_and_after(logger.debug)
    async def delete_report(self, uuid: Optional[str] = None):
        """ Deletes a report.
        :param uuid: The UUID of the report to delete.
        """
        return await self._base_resource.delete_child(Report, uuid)

    # Role methods
    get_role = get_role
    get_roles = get_roles
    create_role = create_role
    delete_role = delete_role
