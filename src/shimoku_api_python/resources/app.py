from typing import List, Dict, Optional, Type, Tuple, Union, TYPE_CHECKING
from copy import deepcopy

import aiohttp
import pandas as pd
import asyncio

from ..base_resource import Resource, ResourceCache
from ..utils import create_normalized_name
from ..exceptions import MenuPathError, FileError
from .activity import Activity
from .role import Role, create_role, get_role, get_roles, delete_role
from .report import Report
from .file import File
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
                         children=[Role, Activity, Report, DataSet, File],
                         check_params_before_creation=['name'], params=params)

        self.currently_in_use: bool = False

    @logging_before_and_after(logger.debug)
    async def delete(self):
        """ Delete the app """
        if self.currently_in_use:
            log_error(logger, f'Menu path {str(self)} is currently in use and cannot be deleted', MenuPathError)
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
        return await self._base_resource.get_child(Activity, uuid, name)

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
    async def get_paths_in_order(self) -> List[str]:
        """ Gets all the paths of the app. They are stored in the reports. """
        reports = await self.get_reports()
        path_orders = [(report['path'], report['pathOrder']) for report in reports if report['pathOrder'] is not None]
        path_orders.sort(key=lambda x: x[1])
        result = []
        for path_order in path_orders:
            if path_order[0] not in result:
                result.append(path_order[0])
        return result

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
        report: Optional[Report] = await self.get_report(uuid, r_hash)
        if not report:
            logger.warning(f'Report {r_hash if r_hash else uuid} not found')
            return
        params = deepcopy(params)
        if 'properties' in params:
            if 'hash' in params['properties']:
                log_error(logger, 'Cannot update the hash of a component.', ValueError)
            report.set_properties(**params.pop('properties'))

        report.set_params(**params)
        await report.update()

    @logging_before_and_after(logger.debug)
    async def delete_report(self, uuid: Optional[str] = None, r_hash: Optional[str] = None):
        """ Deletes a report.
        :param uuid: The UUID of the report to delete.
        :param r_hash: The hash of the report to delete.
        """
        return await self._base_resource.delete_child(Report, uuid, r_hash)

    # DataSet methods
    @logging_before_and_after(logger.debug)
    async def get_data_set(self, uuid: Optional[str] = None, name: Optional[str] = None, create_if_not_exists=True
                           ) -> Optional[DataSet]:
        """ Gets a dataset.
        :param uuid: The UUID of the dataset to get.
        :param name: The alias of the dataset to get.
        :param create_if_not_exists: If True, creates the dataset if it doesn't exist.
        :return: The dataset.
        """
        return await self._base_resource.get_child(DataSet, uuid, name, create_if_not_exists=create_if_not_exists)

    @logging_before_and_after(logger.debug)
    async def get_data_sets(self) -> List[DataSet]:
        """ Gets all the datasets of the app."""
        return await self._base_resource.get_children(DataSet)

    @logging_before_and_after(logger.debug)
    async def delete_data_set(self, uuid: Optional[str] = None, name: Optional[str] = None):
        """ Deletes a dataset.
        :param uuid: The UUID of the dataset to delete.
        :param name: The alias of the dataset to delete.
        """
        return await self._base_resource.delete_child(DataSet, uuid, name)

    @logging_before_and_after(logger.debug)
    async def append_data_to_data_set(
        self, data: Union[pd.DataFrame, List[Dict]],
        uuid: Optional[str] = None, name: Optional[str] = None,
        sort: Optional[Dict] = None, dump_whole: bool = False,
        column_types: Optional[dict] = None
    ) -> Tuple[Mapping, DataSet, Dict]:
        """ Appends data to a dataset. If the dataset doesn't exist, it is created.
        :param uuid: The UUID of the dataset to update.
        :param name: The alias of the dataset to update.
        :param data: The data to update the dataset with.
        :param sort: The sort to apply to the data.
        :param dump_whole: Whether to dump the whole data.
        :param column_types: The types of the columns.
        :return: The dataset.
        """
        data = data.to_dict(orient='records') if isinstance(data, pd.DataFrame) else data
        data_set: DataSet = await self.get_data_set(uuid, name)
        mapping, res_sort = await data_set.create_data_points(
            data_points=data, sort=sort, dump_whole=dump_whole, column_types=column_types
        )
        return mapping, data_set, res_sort

    @logging_before_and_after(logger.debug)
    async def force_delete_data_set(self, uuid: Optional[str] = None, name: Optional[str] = None) -> bool:
        """ Deletes a dataset.
        :param uuid: The UUID of the dataset to delete.
        :param name: The alias of the dataset to delete.
        :return: Whether the dataset was deleted.
        """
        data_set = await self.get_data_set(uuid, name, create_if_not_exists=False)
        if not data_set:
            return False
        reports = await self.get_reports()
        report_data_sets_lists = await asyncio.gather(*[report.get_report_data_sets() for report in reports])
        delete_tasks = []
        for i, report_data_sets in enumerate(report_data_sets_lists):
            await asyncio.gather(*[reports[i].delete_report_dataset(rds['id'])
                                   for rds in report_data_sets if rds['dataSetId'] == data_set['id']])

        await asyncio.gather(*delete_tasks)
        await self.delete_data_set(uuid, name)
        return True

    @logging_before_and_after(logger.debug)
    async def delete_unused_data_sets(self, log: bool = False, data_set_ids: Optional[List[str]] = None):
        """ Deletes all the unused datasets of the app.
        :param log: Whether to log the deletion.
        :param data_set_ids: The ids of the datasets to delete.
        """
        all_reports = await self.get_reports()
        all_rds = await asyncio.gather(*[report.get_report_data_sets() for report in all_reports])
        all_datasets_in_use = [rds['dataSetId'] for _rds_list in all_rds for rds in _rds_list]
        all_datasets = await self.get_data_sets()
        dataset_ids_to_delete = [ds['id'] for ds in all_datasets
                                 if ds['id'] not in all_datasets_in_use
                                 and (ds['id'] in data_set_ids or data_set_ids is None)]
        await asyncio.gather(*[self._base_resource.delete_child(DataSet, ds_id) for ds_id in dataset_ids_to_delete])
        if log:
            logger.info(f'Deleted {len(dataset_ids_to_delete)} unused datasets from the menu path {str(self)}')

    # File methods
    @logging_before_and_after(logger.debug)
    async def create_file(self, name: str, file_object: bytes) -> File:
        """ Creates a file.
        :param name: The file to create.
        :param file_object: The file object.
        :return: The created file.
        """
        name = await self._base_resource.create_child(File, alias=name, contentType='text/csv')

        async with aiohttp.ClientSession() as session:
            logger.info(f'Uploading file {str(name)}')
            async with session.put(name['url'], data=file_object, headers={'Content-Type': 'text/csv'}) as resp:
                if resp.status < 200 or resp.status >= 300:
                    log_error(logger, f'Could not create file {name}, status code: {resp.status}', FileError)

        return name

    @logging_before_and_after(logger.debug)
    async def delete_file(self, uuid: Optional[str] = None, name: Optional[str] = None):
        """ Deletes a file.
        :param uuid: The UUID of the file to delete.
        :param name: The name of the file to delete.
        """
        return await self._base_resource.delete_child(File, uuid, name)

    @logging_before_and_after(logger.debug)
    async def get_file(self, uuid: Optional[str] = None, name: Optional[str] = None) -> Optional[File]:
        """ Gets a file.
        :param uuid: The UUID of the file to get.
        :param name: The alias of the file to get.
        :return: The file.
        """
        return await self._base_resource.get_child(File, uuid, name)

    @logging_before_and_after(logger.debug)
    async def get_files(self) -> List[File]:
        """ Gets all the files of the app.
        :return: The files.
        """
        return await self._base_resource.get_children(File)

    @logging_before_and_after(logger.debug)
    async def get_file_object(self, uuid: Optional[str] = None, name: Optional[str] = None) -> Optional[bytes]:
        """ Gets a file object.
        :param uuid: The UUID of the file to get.
        :param name: The alias of the file to get.
        :return: The file object.
        """
        file = await self.get_file(uuid, name)
        await file.get()

        if not file:
            logger.warning(f'Could not get file {name if name else uuid}')
            return None

        async with aiohttp.ClientSession() as session:
            logger.info(f'Downloading file {str(file)}')
            async with session.request('GET', file['url']) as resp:
                if resp.status < 200 or resp.status >= 300:
                    log_error(logger, f'Could not get file {file}, status code: {resp.status}', FileError)
                return await resp.read()

    # Role methods
    get_role = get_role
    get_roles = get_roles
    create_role = create_role
    delete_role = delete_role
