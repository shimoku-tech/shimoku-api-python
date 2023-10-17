import datetime as dt
import pandas as pd
import asyncio
from copy import deepcopy
from typing import List, Dict, Optional, Union, Tuple, TYPE_CHECKING, TypeVar
from numbers import Number


from ..base_resource import Resource
from ..exceptions import DataError

if TYPE_CHECKING:
    from .app import App

import logging
from ..execution_logger import logging_before_and_after, log_error
logger = logging.getLogger(__name__)

Mapping = TypeVar('Mapping', bound=Union[Dict, List[str], str])


@logging_before_and_after(logging_level=logger.debug)
def check_for_null_values(value, row, column):
    if value is None or pd.isna(value) or pd.isnull(value):
        log_error(
            logger,
            f'Value ({value}) in row ({row}) and column ({column}) is a null value please check for missing values',
            DataError
        )


@logging_before_and_after(logging_level=logger.debug)
def get_column_types(data_point: dict, sort: Optional[dict]) -> dict:
    """ Given a data point, return a dictionary with the column names as keys and their types as values
    :param data_point: a data point
    :param sort: a dictionary with the sort field and order
    """
    data_mapping = {}
    str_counter = 0
    float_counter = 0
    date_counter = 0
    for k, v in data_point.items():
        check_for_null_values(v, 0, k)
        if str_counter > 50:
            raise ValueError('Too many string fields')
        if float_counter > 50:
            raise ValueError('Too many int fields')
        if date_counter > 50:
            raise ValueError('Too many date fields')
        if isinstance(v, str) or isinstance(v, bool):
            str_counter += 1
            data_mapping.update({k: f'stringField{str_counter}'})
        elif isinstance(v, Number):
            if sort and k == sort['field']:
                data_mapping.update({k: 'orderField1'})
                sort['field'] = 'orderField1'
            else:
                float_counter += 1
                data_mapping.update({k: f'intField{float_counter}'})
        elif isinstance(v, (dt.date, dt.datetime, pd.Timestamp)):
            date_counter += 1
            data_mapping.update({k: f'dateField{date_counter}'})
            if sort and k == sort['field']:
                sort['field'] = f'dateField{date_counter}'
        elif isinstance(v, dict):
            data_mapping.update({k: f'customField1'})
        else:
            log_error(logger, f'Unknown value type {v} | Type {type(v)} | Key {k}', DataError)
    return data_mapping


@logging_before_and_after(logging_level=logger.debug)
def check_correct_type(value, types: Union[type, Tuple[type, ...]], row_number: int, column_name: str):
    """ Check if the value is of the correct type
    :param value: value to check
    :param types: type or tuple of types to check
    :param row_number: row number of the value
    :param column_name: column name of the value
    """
    if not isinstance(value, types):
        log_error(
            logger,
            f'Value ({value}) in row ({row_number}) and column ({column_name}) '
            + (f'is not of the correct type {types}' if not isinstance(types, tuple) else
               f'is not one of the correct types {types}'),
            DataError
        )


@logging_before_and_after(logging_level=logger.debug)
def change_keys(data: Union[List[Dict], Dict], mapping: Dict) -> List[Dict]:
    """ Given a data and a mapping, change the keys of the data to the values of the mapping
    :param data: data to change the keys
    :param mapping: mapping of the keys to change
    """
    changed_keys_data = []
    for i, datum in enumerate(data):
        changed_keys_datum = {}
        for k, v in datum.items():
            check_for_null_values(v, i, k)
            k_mapping = mapping[k]
            if k_mapping.startswith('stringField'):
                check_correct_type(v, (str, bool), i, k)
                v = str(v)
            elif k_mapping.startswith('intField') or k_mapping.startswith('orderField'):
                check_correct_type(v, Number, i, k)
                v = float(v)
            elif k_mapping.startswith('dateField'):
                check_correct_type(v, (dt.date, dt.datetime, pd.Timestamp), i, k)
                v = pd.to_datetime(v).isoformat() + 'Z'
            changed_keys_datum[k_mapping] = v
        changed_keys_data.append(changed_keys_datum)
    return changed_keys_data


@logging_before_and_after(logging_level=logger.debug)
def convert_input_data_to_db_items(
    data: Union[List[Dict], Dict],
    sort: Optional[Dict] = None, dump_whole: bool = False,
    column_types: Optional[Dict] = None
) -> Union[List[Dict], Dict]:
    """Given an input data, for all the keys of the data convert it to
     a Shimoku body parameter for data table

      stringField1: String
      stringField2: String
      stringField3: String
      stringField4: String
      intField1: Float
      intField2: Float
      intField3: Float
      intField4: Float
      dateField1: AWSDateTime
      customField1: AWSJSON

    Example
    ------------
    input
        data = [
         {'product': 'Matcha Latte', '2015': 43.3, '2016': 85.8, '2017': 93.7},
         {'product': 'Milk Tea', '2015': 83.1, '2016': 73.4, '2017': 55.1},
         {'product': 'Cheese Cocoa', '2015': 86.4, '2016': 65.2, '2017': 82.5},
         {'product': 'Walnut Brownie', '2015': 72.4, '2016': 53.9, '2017': 39.1}
        ]

    intermediate output
        d = {
            'product': 'stringField1',
            '2015': 'intField1',
            '2016': 'intField2',
            '2017': 'intField3'
        }

    output
        [
            {'stringField1': 'Matcha Latte',
             'intField1': 43.3,
             'intField2': 85.8,
             'intField3': 93.7
             },
            {'stringField1': 'Milk Tea',
             'intField1': 83.1,
             'intField2': 73.4,
             'intField3': 55.1
             },
            {'stringField1': 'Cheese Cocoa',
             'intField1': 86.4,
             'intField2': 65.2,
             'intField3': 82.5
             },
            {'stringField1': 'Walnut Brownie',
             'intField1': 72.4,
             'intField2': 53.9,
             'intField3': 39.1
             }
        ]
    """
    if dump_whole:
        return {'customField1': data}
    elif isinstance(data, list):
        column_mapping = get_column_types(data[0], sort) if column_types is None else column_types
        return change_keys(data, column_mapping)
    else:
        log_error(logger, f'Unknown data type {type(data)}', DataError)


class DataSet(Resource):
    """
    DataSet resource class
    """

    resource_type = 'dataSet'
    alias_field = 'name'
    plural = 'dataSets'

    class DataPoint(Resource):

        resource_type = 'data'
        plural = 'datas'

        @logging_before_and_after(logging_level=logger.debug)
        def __init__(self, parent: 'DataSet', uuid: Optional[str] = None, db_resource: Optional[Dict] = None):

            params = dict(
                dataSetId=parent['id'],
                orderField1=None,
                description=None,
                customField1={},
            )
            for i in range(1, 6):
                params.update({f'dateField{i}': None})
            for i in range(1, 9):
                params.update({f'stringField{i}': None})
                params.update({f'intField{i}': None})

            super().__init__(parent=parent, db_resource=db_resource, uuid=uuid, params=params,
                             params_to_serialize=['customField1'])

        @logging_before_and_after(logging_level=logger.debug)
        async def delete(self):
            """ Delete the data point """
            return await self._base_resource.delete()

        @logging_before_and_after(logging_level=logger.debug)
        async def update(self):
            """ Update the data point """
            return await self._base_resource.update()

    @logging_before_and_after(logging_level=logger.debug)
    def __init__(self, parent: 'App', uuid: Optional[str] = None, alias: Optional[str] = None,
                 db_resource: Optional[Dict] = None):

        params = dict(
            name=alias,
        )
        super().__init__(parent=parent, uuid=uuid, db_resource=db_resource, children=[self.DataPoint],
                         check_params_before_creation=['name'], params=params)

    @logging_before_and_after(logging_level=logger.debug)
    def delete(self):
        """ Delete the data point """
        return self._base_resource.delete()

    # DataPoint methods
    @logging_before_and_after(logging_level=logger.debug)
    async def create_data_points(
        self, data_points: Union[List[Dict], Dict], sort: Optional[Dict] = None,
        dump_whole: bool = False, column_types: Optional[dict] = None
    ) -> Tuple[Mapping, Dict]:
        """ Create data points for a report
        :param data_points: data points to be created
        :param sort: sort parameter
        :param dump_whole: whether to dump the whole data into a single field
        :param column_types: precomputed column types
        :return: mapping
        """
        copy_sort = deepcopy(sort) if sort else None
        converted_data_points = convert_input_data_to_db_items(
            data_points, copy_sort, dump_whole=dump_whole, column_types=column_types
        )
        if isinstance(converted_data_points, Dict):
            converted_data_points = [converted_data_points]
        await self._base_resource.create_children_batch(self.DataPoint, converted_data_points, unit=' data points')
        keys = [k for k in converted_data_points[0].keys() if not copy_sort or copy_sort['field'] != k]
        return keys, copy_sort

    @logging_before_and_after(logging_level=logger.debug)
    async def delete_data_points(self):
        """ Delete data points """
        data_points = await self._base_resource.get_children(self.DataPoint)
        if data_points:
            await asyncio.gather(*[self._base_resource.delete_child(self.DataPoint, uuid=dp['id'])
                                   for dp in data_points])

    @logging_before_and_after(logging_level=logger.debug)
    async def get_data_points(self, limit: Optional[int] = None):
        """ Get data points """
        self.clear()
        return await self._base_resource.get_children(self.DataPoint, limit=limit)

    @logging_before_and_after(logging_level=logger.debug)
    async def get_one_data_point(self) -> Optional['DataSet.DataPoint']:
        """ Get one data point """
        data_points = await self._base_resource.get_children(self.DataPoint, limit=1)
        return data_points[0] if data_points else None
