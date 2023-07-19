from ..report import Report
from ..data_set import DataSet, convert_input_data_to_db_items
import pandas as pd
import logging
from ...execution_logger import logging_before_and_after
logger = logging.getLogger(__name__)


class FilterDataSet(Report):
    """ Filter data set report class """

    report_type = 'FILTERDATASET'

    default_properties = dict(
        hash=None,
        filter=[],
        mapping=[],
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @logging_before_and_after(logger.debug)
    async def link_to_data_set(self, data_set: DataSet, data: pd.DataFrame, field_name: str):
        """ Link the filter data set to a data set
        :param data_set: data set to link to
        :param field_name: field name to link to
        :param data: data to link to
        """
        data_columns = data.columns.to_list()
        converted_data = pd.DataFrame(convert_input_data_to_db_items(data.to_dict(orient='records')))
        converted_data_columns = converted_data.columns.to_list()

        series_name = converted_data_columns[data_columns.index(field_name)]
        if series_name.startswith('date'):
            input_type = "DATERANGE"
        else:
            raise NotImplementedError(f"Field type {series_name} is not supported")

        self['properties']['filter'] = [{
            'operations': ['contains'],
            'field': field_name,
            'inputType': input_type,

        }, {
            'operations': ['contains'],
            'field': field_name,
            'inputType': input_type,

        }]

        self['properties']['mapping'] = [{
            field_name: series_name,
            'id': data_set['id']
        }]

        await self.update()
