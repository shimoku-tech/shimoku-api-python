import json

import datetime as dt
import pandas as pd
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
    data: Union[List[Dict], Dict], sort: Optional[Dict] = None
) -> Union[List[Dict], Dict]:
    """Given an input data, for all the keys of the data convert it to
     a Shimoku body parameter for Data table

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
    if type(data) == dict:
        return {'customField1': data}
    elif type(data) == list:
        d = {}
        str_counter = 0
        float_counter = 0
        date_counter = 0
        for k, v in data[0].items():
            type_v = type(v)
            if type_v == str:
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
    plural = 'dataSets'

    class DataPoint(Resource):

        resource_type = 'data'
        plural = 'datas'

        @logging_before_and_after(logging_level=logger.debug)
        def __init__(self, parent: 'DataSet', uuid: Optional[str] = None, db_resource: Optional[Dict] = None):

            params = dict(
                reportId=parent['id'],
            )

            super().__init__(parent=parent, db_resource=db_resource, uuid=uuid, params=params,
                             check_params_before_creation=['reportId'],
                             params_to_serialize=['properties'])

        @logging_before_and_after(logging_level=logger.debug)
        async def delete(self):
            """ Delete the report entry """
            return await self._base_resource.delete()

        @logging_before_and_after(logging_level=logger.debug)
        async def update(self):
            """ Update the report entry """
            return await self._base_resource.update()

    @logging_before_and_after(logging_level=logger.debug)
    def __init__(self, parent: 'App', uuid: Optional[str] = None, db_resource: Optional[Dict] = None):

        super().__init__(parent=parent, uuid=uuid, db_resource=db_resource, children=[self.DataPoint])

    @logging_before_and_after(logging_level=logger.debug)
    def delete(self):
        """ Delete the report entry """
        return self._base_resource.delete()

    # DataPoint methods
    @logging_before_and_after(logging_level=logger.debug)
    async def create_data_points(self, data_points: Union[List[Dict], Dict], sort: Optional[Dict] = None
                                 ) -> Tuple[Mapping, Dict]:
        """ Create data points for a report
        :param data_points: data points to be created
        :param sort: sort parameter
        :return: mapping
        """
        copy_sort = deepcopy(sort) if sort else None
        converted_data_points = convert_input_data_to_db_items(data_points, copy_sort)
        if isinstance(converted_data_points, Dict):
            converted_data_points = [converted_data_points]
        await self._base_resource.create_children_batch(self.DataPoint, converted_data_points, unit=' data points')
        keys = [k for k in converted_data_points[0].keys() if not copy_sort or copy_sort['field'] != k]
        return keys, copy_sort
