from typing import List, Dict, Optional, Type, Tuple, Union, TYPE_CHECKING
from copy import deepcopy

import pandas as pd

from ..base_resource import Resource, ResourceCache
from ..utils import create_normalized_name
from .activity import Activity
from .role import Role, create_role, get_role, get_roles, delete_role
from .report import Report
from .data_set import DataSet, Mapping

if TYPE_CHECKING:
    from .business import Business

import logging
from ..execution_logger import logging_before_and_after, log_error
logger = logging.getLogger(__name__)


class App(Resource):
    """ App resource class """

    resource_type = 'app'
    alias_field = 'name'
    plural = 'apps'

    @logging_before_and_after(logger.debug)
    def __init__(self, parent: 'Business', uuid: Optional[str] = None, alias: Optional[str] = None,
                 db_resource: Optional[Dict] = None):

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

        super().__init__(parent=parent, uuid=uuid, db_resource=db_resource,
                         children=[Role, Activity, Report, DataSet],
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
    def mock_create_report(self, report_class: Type[Report], r_hash: str, **params) -> Report:
        """ Creates a child of a given report class but doesn't add it to the cache.
        :param report_class: The class of the report to create.
        :param r_hash: The hash of the report to create.
        :param params: The parameters of the report to create.
        :return: The created resource.
        """
        report = report_class(parent=self)
        params = deepcopy(params)

        properties = params.pop('properties') if 'properties' in params else {}
        properties['hash'] = r_hash

        report.set_properties(**properties)
        report.set_params(**params)
        return report

    @logging_before_and_after(logger.debug)
    async def create_report(self, report_class: Type[Report], r_hash: str, **params) -> Report:
        """ Creates a child of a given report class.
        :param report_class: The class of the report to create.
        :param r_hash: The hash of the report to create.
        :param params: The parameters of the report to create.
        :return: The created resource.
        """
        report_cache: ResourceCache = self._base_resource.children[Report]
        return await report_cache.add(self.mock_create_report(report_class, r_hash, **params), alias=r_hash)

    @logging_before_and_after(logger.debug)
    async def get_report(self, uuid: Optional[str] = None, r_hash: Optional[str] = None) -> Optional[Report]:
        """ Gets a report.
        :param uuid: The UUID of the report to get.
        :param r_hash: The hash of the report to get.
        :return: The resource.
        """
        return await self._base_resource.get_child(Report, uuid, r_hash)

    @logging_before_and_after(logger.debug)
    async def get_reports(self) -> List[Report]:
        """ Gets all the reports of the app."""
        return await self._base_resource.get_children(Report)

    @logging_before_and_after(logger.debug)
    async def update_report(self, uuid: Optional[str] = None, r_hash: Optional[str] = None, **params):
        """ Updates a report.
        :param uuid: The UUID of the report to update.
        :param r_hash: The hash of the report to update.
        :param params: The parameters of the report to update.
        """
        report = await self.get_report(uuid, r_hash)
        params = deepcopy(params)
        if 'properties' in params:
            if 'hash' in params['properties']:
                log_error(logger, 'Cannot update the hash of a report.', ValueError)
            report.set_properties(**params.pop('properties'))

        report.set_params(**params)
        await report.update()

    @logging_before_and_after(logger.debug)
    async def delete_report(self, uuid: Optional[str] = None):
        """ Deletes a report.
        :param uuid: The UUID of the report to delete.
        """
        return await self._base_resource.delete_child(Report, uuid)

    # DataSet methods
    @logging_before_and_after(logger.debug)
    async def create_dataset(self) -> DataSet:
        """ Creates a dataset.
        :return: The created dataset.
        """
        return await self._base_resource.create_child(DataSet)

    @logging_before_and_after(logger.debug)
    async def get_dataset(self, uuid: Optional[str] = None) -> Optional[DataSet]:
        """ Gets a dataset.
        :param uuid: The UUID of the dataset to get.
        :return: The dataset.
        """
        return await self._base_resource.get_child(DataSet, uuid)

    @logging_before_and_after(logger.debug)
    async def get_datasets(self) -> List[DataSet]:
        """ Gets all the datasets of the app."""
        return await self._base_resource.get_children(DataSet)

    @logging_before_and_after(logger.debug)
    async def delete_dataset(self, uuid: Optional[str] = None):
        """ Deletes a dataset.
        :param uuid: The UUID of the dataset to delete.
        """
        return await self._base_resource.delete_child(DataSet, uuid)

    @logging_before_and_after(logger.debug)
    async def append_data_to_dataset(self, data: Union[pd.DataFrame, Dict], uuid: Optional[str] = None,
                                     sort: Optional[Dict] = None) -> Tuple[Mapping, DataSet, Dict]:
        """ Appends data to a dataset. If the dataset doesn't exist, it is created.
        :param uuid: The UUID of the dataset to update.
        :param data: The data to update the dataset with.
        :param sort: The sort to apply to the data.
        :return: The dataset.
        """
        data_set = await self.get_dataset(uuid) if uuid else await self.create_dataset()
        mapping, res_sort = await data_set.create_data_points(
            data_points=data.to_dict(orient='records') if isinstance(data, pd.DataFrame) else data,
            sort=sort)
        return mapping, data_set, res_sort

    # Role methods
    get_role = get_role
    get_roles = get_roles
    create_role = create_role
    delete_role = delete_role
