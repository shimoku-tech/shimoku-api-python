from typing import List, Dict, Optional, Tuple, TYPE_CHECKING, Type

import asyncio
from copy import deepcopy

from ..base_resource import Resource
from .data_set import DataSet, Mapping
if TYPE_CHECKING:
    from .app import App

import logging
from ..execution_logger import logging_before_and_after

logger = logging.getLogger(__name__)


class Report(Resource):
    """ Report resource class """

    resource_type = 'report'
    plural = 'reports'
    alias_field = 'properties/hash'

    report_type = None
    possible_values = {}
    default_properties = {
        'hash': None,
    }

    class ReportDataSet(Resource):

        resource_type = 'reportDataSet'
        plural = 'reportDataSets'

        @logging_before_and_after(logger.debug)
        def __init__(self, parent: 'Report', uuid: Optional[str] = None, db_resource: Optional[Dict] = None):

            params = dict(
                reportId=parent['id'],
                dataSetId='',
                properties={},
            )

            super().__init__(parent=parent, uuid=uuid, db_resource=db_resource, params=params,
                             check_params_before_creation=['reportId', 'dataSetId'],
                             params_to_serialize=['properties'])

        @logging_before_and_after(logger.debug)
        async def delete(self):
            """ Delete the report dataset """
            return await self._base_resource.delete()

        @logging_before_and_after(logger.debug)
        async def update(self):
            """ Update the report dataset """
            return await self._base_resource.update()

    @logging_before_and_after(logger.debug)
    def __init__(self, parent: 'App', uuid: Optional[str] = None, db_resource: Optional[Dict] = None):

        params = dict(
            title=None,
            path=None,
            pathOrder=None,
            reportType=self.report_type,
            order=0,
            sizeColumns=12,
            sizeRows=3,
            sizePadding='0,0,0,0',
            bentobox={},
            properties=deepcopy(self.default_properties),
            dataFields={},
            chartData=[],
            # subscribed=False,
            smartFilters=[],
        )

        super().__init__(parent=parent, uuid=uuid, db_resource=db_resource, params=params,
                         children=[Report.ReportDataSet],
                         check_params_before_creation=['order'],
                         params_to_serialize=['properties', 'dataFields', 'chartData', 'bentobox', 'smartFilters'])

    @logging_before_and_after(logger.debug)
    def __ne__(self, other):
        return not self.__eq__(other)

    @logging_before_and_after(logger.debug)
    def __eq__(self, other: 'Report'):
        return super().__eq__(other)

    def __new__(cls, parent: 'App', uuid: Optional[str] = None, db_resource: Optional[Dict] = None):
        if uuid:
            return super().__new__(cls)
        if cls is Report:
            if db_resource is None:
                raise ValueError('You must provide a db_resource to create a Report instance')
            if db_resource['reportType'] == 'TABS':
                from .reports.tabs_group import TabsGroup
                return TabsGroup(parent=parent, uuid=uuid, db_resource=db_resource)
            elif db_resource['reportType'] == 'MODAL':
                from .reports.modal import Modal
                return Modal(parent=parent, uuid=uuid, db_resource=db_resource)
            elif db_resource['reportType'] == 'INDICATOR':
                from .reports.charts.indicator import Indicator
                return Indicator(parent=parent, uuid=uuid, db_resource=db_resource)
            elif db_resource['reportType'] == 'ECHARTS2':
                from .reports.charts.echart import EChart
                return EChart(parent=parent, uuid=uuid, db_resource=db_resource)
            elif db_resource['reportType'] == 'IFRAME':
                from .reports.charts.iframe import IFrame
                return IFrame(parent=parent, uuid=uuid, db_resource=db_resource)
            elif db_resource['reportType'] == 'HTML':
                from .reports.charts.html import HTML
                return HTML(parent=parent, uuid=uuid, db_resource=db_resource)
            elif db_resource['reportType'] == 'TABLE':
                from .reports.charts.table import Table
                return Table(parent=parent, uuid=uuid, db_resource=db_resource)
            elif db_resource['reportType'] == 'ANNOTATED_ECHART':
                from .reports.charts.annotated_chart import AnnotatedEChart
                return AnnotatedEChart(parent=parent, uuid=uuid, db_resource=db_resource)
            elif db_resource['reportType'] == 'BUTTON':
                from .reports.charts.button import Button
                return Button(parent=parent, uuid=uuid, db_resource=db_resource)
            elif db_resource['reportType'] == 'FORM':
                from .reports.charts.input_form import InputForm
                return InputForm(parent=parent, uuid=uuid, db_resource=db_resource)
            elif db_resource['reportType'] == 'FILTERDATASET':
                from .reports.filter_data_set import FilterDataSet
                return FilterDataSet(parent=parent, uuid=uuid, db_resource=db_resource)
            elif db_resource['reportType'] in ['INDICATORS', 'MULTIFILTER', 'ECHARTS', None]:
                from .reports.unsupported import Unsupported
                return Unsupported(parent=parent, uuid=uuid, db_resource=db_resource)
            else:
                raise ValueError(f'Unknown report type {db_resource["reportType"]}')
        else:
            return super().__new__(cls)

    @logging_before_and_after(logger.debug)
    async def delete(self):
        """ Delete the report """
        return await self._base_resource.delete()

    @logging_before_and_after(logger.debug)
    async def update(self):
        """ Update the report """
        return await self._base_resource.update()

    @logging_before_and_after(logger.debug)
    def set_properties(self, **properties):
        """ Set the properties of the report without saving it to the server ç
        :param properties: the properties to set """
        for property_name, value in properties.items():
            if property_name not in self.default_properties.keys():
                raise ValueError(f'Property {property_name} is not a possible property for {self.report_type}')
            if property_name in self.possible_values and value not in self.possible_values[property_name]:
                raise ValueError(f'Value {value} is not a possible value for property {property_name}')

        self['properties'].update(properties)
        self._base_resource.changed_params.add('properties')

    @logging_before_and_after(logger.debug)
    async def change_report_type(self, report_class: Type['Report']):
        """ change the report type of the report """
        logger.info(f'Changing component type from {self.report_type} to {report_class.report_type}')
        if self.report_type == report_class.report_type:
            return
        await self.delete_report_data_sets()
        self['reportType'] = report_class.report_type
        r_hash = self['properties'].get('hash')
        self['properties'] = deepcopy(report_class.default_properties)
        self['properties']['hash'] = r_hash
        self['dataFields'] = {}
        self['chartData'] = []
        self.__class__ = report_class

    # ReportDataSet methods
    @logging_before_and_after(logger.debug)
    async def create_report_data_set(self, mapping_data_set_sort: Tuple[Optional[Mapping], DataSet, Optional[Dict]],
                                     properties: Optional[Dict] = None) -> 'ReportDataSet':
        """ Update the report dataset
        :param mapping_data_set_sort: a tuple of mapping, data_set, sort
        :param properties: the properties to set
        :return: the updated report dataset
        """
        mapping, data_set, sort = mapping_data_set_sort
        data_set_id = data_set['id']
        properties = properties if properties is not None else {}
        properties['mapping'] = mapping
        properties['sort'] = sort
        params = dict(
            dataSetId=data_set_id,
            properties=properties,
        )
        report_data_set = await self._base_resource.create_child(self.ReportDataSet, **params)
        return report_data_set

    @logging_before_and_after(logger.debug)
    async def get_report_dataset(self, uuid: Optional[str] = None) -> 'ReportDataSet':
        """ Get a report dataset
        :param uuid: the uuid of the report dataset to get
        :return: the report dataset
        """
        return await self._base_resource.get_child(self.ReportDataSet, uuid=uuid)

    @logging_before_and_after(logger.debug)
    async def get_report_data_sets(self) -> List['ReportDataSet']:
        """ Get all the report datasets of the report """
        return await self._base_resource.get_children(self.ReportDataSet)

    @logging_before_and_after(logger.debug)
    async def delete_report_dataset(self, uuid: Optional[str] = None) -> bool:
        """ Delete a report dataset
        :param uuid: the uuid of the report dataset to delete
        :return: True if the report dataset was deleted, False otherwise
        """
        return await self._base_resource.delete_child(self.ReportDataSet, uuid=uuid)

    @logging_before_and_after(logging_level=logger.debug)
    async def delete_report_data_sets(self, log: bool = False):
        """ Delete the datasets and links that are not in use anymore.
        :param log: if True, log the actions"""
        report_data_sets = await self.get_report_data_sets()
        await asyncio.gather(*[self._base_resource.delete_child(self.ReportDataSet, uuid=rds['id'])
                               for rds in report_data_sets])
        if log:
            logger.info(f'Deleted {len(report_data_sets)} component data set links from component at {str(self)}')
