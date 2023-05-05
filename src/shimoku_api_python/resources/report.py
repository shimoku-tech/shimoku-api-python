from typing import List, Dict, Optional, TYPE_CHECKING

from copy import deepcopy
import pandas as pd
import datetime as dt
import json

from ..base_resource import Resource
from .data_set import DataSet
if TYPE_CHECKING:
    from .app import App

import logging
from ..execution_logger import logging_before_and_after
logger = logging.getLogger(__name__)


@logging_before_and_after(logging_level=logger.debug)
def convert_dataframe_to_report_entry(
    df: pd.DataFrame,
    sorting_columns_map: Optional[Dict[str, str]] = None,
    report_entry_chunks: bool = True,
) -> List[Dict]:
    """
    :param df:
    :param sorting_columns_map:
    :param report_entry_chunks:
    """

    if sorting_columns_map:
        try:
            assert len(sorting_columns_map) <= 4
        except AssertionError:
            raise ValueError(
                f'At maximum a table may have 4 different sorting columns | '
                f'You provided {len(sorting_columns_map)} | '
                f'You provided {sorting_columns_map}'
            )
        df_ = df.rename(columns=sorting_columns_map)
        metadata_entries: List[Dict] = df_[list(sorting_columns_map.values())].to_dict(orient='records')
    else:
        metadata_entries: List[Dict] = []

    records: List[Dict] = df.to_dict(orient='records')

    if report_entry_chunks:
        for datum in records:
            for k, v in datum.items():
                if isinstance(v, dt.date) or isinstance(v, dt.datetime):
                    datum[k] = v.isoformat()
        data_entries = [{'data': d} for d in records]
    else:
        try:
            data_entries: List[Dict] = [
                {'data': json.dumps(d)}
                for d in records
            ]
        except TypeError:
            # If we have date or datetime values
            # then we need to convert them to isoformat
            for datum in records:
                for k, v in datum.items():
                    if isinstance(v, dt.date) or isinstance(v, dt.datetime):
                        datum[k] = v.isoformat()

            data_entries: List[Dict] = [
                {'data': json.dumps(d)}
                for d in records
            ]

    if metadata_entries:
        try:
            _ = json.dumps(metadata_entries)
        except TypeError:
            # If we have date or datetime values
            # then we need to convert them to isoformat
            for datum in metadata_entries:
                for k, v in datum.items():
                    if isinstance(v, dt.date) or isinstance(v, dt.datetime):
                        datum[k] = v.isoformat()

        # Generate the list of single entries with all
        # necessary information to be posted
        return [
            {**data_entry, **metadata_entry}
            for data_entry, metadata_entry in zip(data_entries, metadata_entries)
        ]
    else:
        return data_entries


class Report(Resource):
    """ Report resource class """

    resource_type = 'report'
    plural = 'reports'
    report_type = None

    possible_values = {}
    default_properties = {}

    class ReportEntry(Resource):

        resource_type = 'reportEntry'
        plural = 'reportEntries'

        @logging_before_and_after(logger.debug)
        def __init__(self, parent: 'Report', uuid: Optional[str] = None):

            params = dict(
                reportId=parent['id'],
            )

            super().__init__(parent=parent, uuid=uuid, params=params,
                             check_params_before_creation=['reportId'],
                             params_to_serialize=['properties'])

        @logging_before_and_after(logger.debug)
        async def delete(self):
            """ Delete the report entry """
            return await self._base_resource.delete()

        @logging_before_and_after(logger.debug)
        async def update(self):
            """ Update the report entry """
            return await self._base_resource.update()

    class ReportDataSet(Resource):

        resource_type = 'reportDataSet'
        alias_field = 'dataSetId'
        plural = 'reportDataSets'

        @logging_before_and_after(logger.debug)
        def __init__(self, parent: 'Report', uuid: Optional[str] = None, alias: Optional[int] = None):

            params = dict(
                reportId=parent['id'],
                dataSetId=alias,
                properties={},
            )

            super().__init__(parent=parent, uuid=uuid, params=params,
                             check_params_before_creation=['reportId', 'dataSetId'],
                             params_to_serialize=['properties'])

    @logging_before_and_after(logger.debug)
    def __init__(self, parent: 'App', uuid: Optional[str] = None, params_to_update: Optional[Dict] = None):

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
        params.update(params_to_update) if params_to_update else None

        super().__init__(parent=parent, uuid=uuid, params=params,
                         children=[Report.ReportDataSet, Report.ReportEntry],
                         check_params_before_creation=['order'],
                         params_to_serialize=['properties', 'dataFields', 'chartData', 'bentobox', 'smartFilters'])

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
        """ Set the properties of the report without saving it to the server """
        for property_name, value in properties.items():
            if property_name not in self.default_properties.keys():
                raise ValueError(f'Property {property_name} is not a possible property for this report')
            if property_name in self.possible_values and value not in self.possible_values[property_name]:
                raise ValueError(f'Value {value} is not a possible value for property {property_name}')

        self['properties'].update(properties)
        self._base_resource.changed_params.add('properties')

    # ReportDataSet methods
    @logging_before_and_after(logger.debug)
    async def create_report_dataset(self, data_set: DataSet, properties: Optional[Dict] = None) -> 'ReportDataSet':
        return await self._base_resource.create_child(self.ReportDataSet, dataset=data_set, properties=properties)

    @logging_before_and_after(logger.debug)
    async def update_report_dataset(self, uuid: Optional[str] = None, data_set: Optional[DataSet] = None,
                                    **params) -> 'ReportDataSet':
        if 'new_data_set' in params:
            params['new_alias'] = params.pop('new_data_set')['id']
        data_set_id = data_set['id'] if data_set else None
        return await self._base_resource.update_child(self.ReportDataSet, uuid=uuid, alias=data_set_id, **params)

    @logging_before_and_after(logger.debug)
    async def get_report_dataset(self, uuid: Optional[str] = None, data_set: Optional[DataSet] = None
                                 ) -> Optional['ReportDataSet']:
        data_set_id = data_set['id'] if data_set else None
        return await self._base_resource.get_child(self.ReportDataSet, uuid=uuid, alias=data_set_id)

    @logging_before_and_after(logger.debug)
    async def get_report_datasets(self) -> List['ReportDataSet']:
        return await self._base_resource.get_children(self.ReportDataSet)

    @logging_before_and_after(logger.debug)
    async def delete_report_dataset(self, uuid: Optional[str] = None, data_set: Optional[DataSet] = None):
        data_set_id = data_set['id'] if data_set else None
        return await self._base_resource.delete_child(self.ReportDataSet, uuid=uuid, alias=data_set_id)

    # ReportEntry methods
    @logging_before_and_after(logger.debug)
    async def create_report_entries(self, report_entries: pd.DataFrame, sorting_columns_map: Optional[Dict] = None):
        converted_report_entries = convert_dataframe_to_report_entry(report_entries, sorting_columns_map)
        return await self._base_resource.create_children_batch(self.ReportEntry,
                                                               report_entries=converted_report_entries,
                                                               batch_size=999)
