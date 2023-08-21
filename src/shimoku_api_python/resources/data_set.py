import datetime as dt
import pandas as pd
import asyncio
from copy import deepcopy
from typing import List, Dict, Optional, Union, Tuple, TYPE_CHECKING, TypeVar

from ..base_resource import Resource

if TYPE_CHECKING:
    from .app import App

import logging
from ..execution_logger import logging_before_and_after
logger = logging.getLogger(__name__)

Mapping = TypeVar('Mapping', bound=Union[Dict, List[str], str])


@logging_before_and_after(logging_level=logger.debug)
def convert_input_data_to_db_items(
    data: Union[List[Dict], Dict], sort: Optional[Dict] = None, dump_whole: bool = False
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
    elif type(data) == list:
        d = {}
        str_counter = 0
        float_counter = 0
        date_counter = 0
        # TODO: Check all data not just the first one
        for k, v in data[0].items():
            if str_counter > 50:
                raise ValueError('Too many string fields')
            if float_counter > 50:
                raise ValueError('Too many int fields')
            if date_counter > 50:
                raise ValueError('Too many date fields')
            type_v = type(v)
            if type_v == str or type_v == bool:
                str_counter += 1
                d.update({k: f'stringField{str_counter}'})
            elif type_v == float or type_v == int:
                if sort and k == sort['field']:
                    d.update({k: 'orderField1'})
                    sort['field'] = 'orderField1'
                else:
                    float_counter += 1
                    d.update({k: f'intField{float_counter}'})
            elif type_v == dt.date or type_v == dt.datetime or type_v == pd.Timestamp:
                date_counter += 1
                d.update({k: f'dateField{date_counter}'})
                if sort and k == sort['field']:
                    sort['field'] = f'dateField{date_counter}'
            elif type_v == dict:
                d.update({k: f'customField1'})
            else:
                raise ValueError(f'Unknown value type {v} | Type {type_v}')
        return [{d[k]: v if 'dateField' not in d[k] else pd.to_datetime(v).isoformat()+'Z'
                 for k, v in datum.items()} for datum in data]
    else:
        assert type(data) == list or type(data) == dict


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
    async def create_data_points(self, data_points: Union[List[Dict], Dict], sort: Optional[Dict] = None,
                                 dump_whole: bool = False) -> Tuple[Mapping, Dict]:
        """ Create data points for a report
        :param data_points: data points to be created
        :param sort: sort parameter
        :param dump_whole: whether to dump the whole data into a single field
        :return: mapping
        """
        copy_sort = deepcopy(sort) if sort else None
        converted_data_points = convert_input_data_to_db_items(data_points, copy_sort, dump_whole=dump_whole)
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
