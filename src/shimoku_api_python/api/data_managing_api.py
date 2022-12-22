""""""
import json
from typing import List, Dict, Optional, Union, Set
from itertools import chain

import datetime as dt
import pandas as pd
from pandas import DataFrame

from .explorer_api import (
    GetExplorerAPI, DeleteExplorerApi, CreateExplorerAPI,
    DatasetExplorerApi, ReportDatasetExplorerApi,
)
from .report_metadata_api import ReportMetadataApi


class DataExplorerApi:
    get_report = ReportMetadataApi.get_report
    _get_report_with_data = GetExplorerAPI._get_report_with_data
    get_report_data = ReportMetadataApi.get_report_data
    _update_report = ReportMetadataApi.update_report
    _get_report_datasets = ReportDatasetExplorerApi.get_report_datasets

    _create_report_entries = CreateExplorerAPI._create_report_entries
    _create_data_points = DatasetExplorerApi.create_data_points
    _create_dataset = DatasetExplorerApi.create_dataset
    _create_reportdataset = ReportDatasetExplorerApi.create_reportdataset

    _delete_report_entries = DeleteExplorerApi.delete_report_entries


class DataValidation:

    def __init__(self, api_client):
        self.api_client = api_client

    def _validate_data_is_pandarable(
        self, data: Union[str, DataFrame, List[Dict], Dict],
    ) -> DataFrame:
        """"""
        if isinstance(data, DataFrame):
            df_ = data.copy()
        elif isinstance(data, list):
            try:
                df_ = DataFrame(data)
            except Exception:
                raise ValueError(
                    'The data you passed is a list that must be '
                    'able to be converted into a pandas dataframe'
                )
        elif isinstance(data, dict):
            try:
                df_ = DataFrame(data)
            except Exception:
                try:
                    df_ = DataFrame(data, index=[0])
                except Exception:
                    raise ValueError(
                        'The data you passed is a dict that must be '
                        'able to be converted into a pandas dataframe'
                    )
        elif isinstance(data, str):
            try:
                d: List[Dict] = json.loads(data)
                df_ = DataFrame(d)
            except Exception:
                raise ValueError(
                    'The data you passed is a json that must be '
                    'able to be converted into a pandas dataframe'
                )
        else:
            raise ValueError(
                'Input data must be a pandas dataframe, '
                'a json or a list of dictionaries'
            )
        return df_

    def _validate_table_data(
        self, data: Union[str, DataFrame, List[Dict], Dict], elements: List[str],
    ):
        """"""
        df_: DataFrame = self._validate_data_is_pandarable(data)

        cols = df_.columns
        try:
            assert all([element in cols for element in elements])
        except AssertionError:
            raise ValueError(
                'Some column names you are specifying '
                'are not in the input dataframe'
            )

        try:
            len_df_: int = len(df_)
            assert all([
                len_df_ == len(df_[~df_[element].isna()])
                for element in elements
            ])
        except AssertionError:
            raise ValueError(
                f'Some of the variables {elements} have none values'
            )

    def _validate_tree_data(
        self, data: Union[str, List[Dict]], vals: List[str],
    ):
        """To validate Tree and Treemap data"""
        if isinstance(data, list):
            pass
        elif isinstance(data, dict):
            pass
        elif isinstance(data, str):
            data = json.loads(data)
        else:
            raise ValueError('data must be either a list, dict or a json')

        try:
            assert sorted(data.keys()) == sorted(vals)
        except AssertionError:
            raise ValueError('data keys must be "name", "value" and "children"')

    def _validate_input_form_data(self, data: Dict):
        try:
            assert type(data) == dict
        except AssertionError:
            raise ValueError('data must be a dict')

        try:
            assert 'fields' in data
        except AssertionError:
            raise ValueError('"fields" is not a key in the input data')

        try:
            assert type(data['fields']) == list
        except AssertionError:
            raise ValueError('fields must be a list')

        try:
            assert all(['fields' in field_ for field_ in data['fields']])
        except AssertionError:
            raise ValueError('"fields" are not keys in the input data')

        try:
            assert all([
                'fieldName' in field__ and 'mapping' in field__
                for field_ in data['fields']
                for field__ in field_['fields']
            ])
        except AssertionError:
            raise ValueError('"fieldName" and "mapping" are not keys in the input data')

    def _is_report_data_empty(
        self, report_data: Union[List[Dict], str, DataFrame, Dict, List],
    ) -> bool:
        if isinstance(report_data, DataFrame):
            if report_data.empty:
                return True
            else:
                return False
        elif isinstance(report_data, list) or isinstance(report_data, dict):
            if report_data:
                return False
            else:
                return True
        elif isinstance(report_data, str):
            report_data_: List[Dict] = json.loads(report_data)
            if report_data_:
                return False
            else:
                return True
        else:
            raise ValueError(
                f'Data must be a Dictionary, JSON or pandas DataFrame '
                f'Provided: {type(report_data)}'
            )


class DataManagingApi(DataExplorerApi, DataValidation):
    """This is used for
    - report.chartData
    - reportEntry

    For DataSet / Data see: DataSetManagingApi()
    """

    def __init__(self, api_client):
        self.api_client = api_client

    def _transform_report_data_to_chart_data(
        self, report_data: Union[List[Dict], str, DataFrame, Dict],
    ) -> List[Dict]:
        if isinstance(report_data, DataFrame):
            chart_data: List[Dict] = report_data.to_dict(orient='records')
        elif isinstance(report_data, dict):
            df_: DataFrame = pd.DataFrame([report_data])
            chart_data: List[Dict] = df_.to_dict(orient='records')
        elif isinstance(report_data, list):
            assert isinstance(report_data[0], dict)
            chart_data: List[Dict] = report_data
        elif isinstance(report_data, str):
            chart_data: List[Dict] = json.loads(report_data)
        else:
            raise ValueError(
                f'Data must be a Dictionary, JSON or pandas DataFrame '
                f'Provided: {type(report_data)}'
            )
        return chart_data

    def _convert_input_data_to_db_items(
        self, data: Union[List[Dict], Dict], sort: Optional[Dict] = None
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
            return {'customField1': json.dumps(data)}
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
                    float_counter += 1
                    if sort and k == sort['field']:
                        d.update({k: 'orderField1'})
                        sort['field'] = 'orderField1'
                    else:
                        d.update({k: f'intField{float_counter}'})

                elif type_v == dt.date or type_v == dt.datetime or type_v == pd.Timestamp:
                    date_counter += 1
                    d.update({k: f'dateField{date_counter}'})
                elif type_v == dict:
                    d.update({k: f'customField1'})
                else:
                    raise ValueError(f'Unknown value type {v} | Type {type_v}')
            return [{d[k]: v for k, v in datum.items()} for datum in data]
        else:
            assert type(data) == list or type(data) == dict

    def _convert_dataframe_to_report_entry(
        self, df: DataFrame,
        filter_map: Optional[Dict[str, str]] = None,
        filter_fields: Optional[Dict[str, List[str]]] = None,
        search_columns: Optional[List[str]] = None,
        report_entry_chunks: bool = True,
    ) -> List[Dict]:
        """
        :param df:
        :param report_id:
        :param filter_fields: Example: {
                'stringField1': ['high', 'medium', 'low'],
                'stringField2': ['probable', 'improbable'],
            }
        :param search_columns:
        :param report_entry_chunks:
        """
        cols: List[str] = df.columns.tolist()

        if filter_fields:
            try:
                assert len(filter_fields) <= 4
            except AssertionError:
                raise ValueError(
                    f'At maximum a table may have 4 different filters | '
                    f'You provided {len(filter_fields)} | '
                    f'You provided {filter_fields}'
                )

            df_ = df.rename(columns=filter_map)
            metadata_entries: Dict = df_[list(filter_map.values())].to_dict(orient='records')
        elif search_columns:
            df_ = df.rename(columns=filter_map)
            filter_search_map: List = [
                v for k, v in filter_map.items() if k in search_columns
            ]
            metadata_entries: Dict = df_[filter_search_map].to_dict(orient='records')
        else:
            data_columns: List[str] = cols
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

# TODO pending add append_report_data to free Echarts
    def append_report_data(
        self, business_id: str, app_id: str,
        report_data: Union[List[Dict], str, DataFrame, Dict],
        report_id: Optional[str] = None,
        external_id: Optional[str] = None,
    ) -> None:
        """Having a dataframe of Report

        It is an aggregation, meaning we preserve all previous
        data and just concatenate the new ones
        """
        _ = self._validate_data_is_pandarable(report_data)

        if self._is_report_data_empty(report_data):
            return

        report: Dict = (
            self._get_report_with_data(
                business_id=business_id,
                app_id=app_id,
                report_id=report_id,
                external_id=external_id,
            )
        )

        if report.get('reportType'):  # For non-table chart
            chart_data_new: List[Dict] = (
                self._transform_report_data_to_chart_data(report_data)
            )

            chart_data: Dict = report.get('chartData')

            # Data resistance
            #  check that the column names are the
            #  same in the data we try to append
            all_keys: Set[str] = set(chain.from_iterable(chart_data))
            for d in chart_data_new:
                try:
                    assert set(sorted((d.keys()))) == all_keys
                except AssertionError:
                    KeyError(
                        f'The provided data has not the same keys'
                        f' that the data it tries to append | '
                        f'Required keys: {all_keys}'
                    )

            if chart_data:
                chart_data = chart_data + chart_data_new
            else:
                chart_data = chart_data_new

            try:
                report_data_ = {
                    'chartData': json.dumps(chart_data),
                }
            except TypeError:
                # If we have date or datetime values
                # then we need to convert them to isoformat
                for datum in chart_data:
                    for k, v in datum.items():
                        if isinstance(v, dt.date) or isinstance(v, dt.datetime):
                            datum[k] = v.isoformat()

                report_data_ = {
                    'chartData': json.dumps(chart_data),
                }

            self._update_report(
                business_id=business_id,
                app_id=app_id,
                report_id=report_id,
                report_metadata=report_data_,
            )
        else:  # Then it is a table
            item: Dict = {'reportId': report_id}

            data: List[Dict] = (
                self.convert_dataframe_to_report_entry(
                    report_id=report_id, df=report_data,
                )
            )

            # TODO we can store batches and go faster than one by one
            for datum in data:
                item.update(datum)
                self.post_report_entry(item)

    def update_report_data(
            self, business_id: str, app_id: str,
            report_data: Union[List, Dict, str, DataFrame],
            report_id: Optional[str] = None,
            external_id: Optional[str] = None,
    ) -> None:
        """Remove old add new"""
        _ = self._validate_data_is_pandarable(report_data)

        if self._is_report_data_empty(report_data):
            return

        report: Dict = (
            self.get_report(
                business_id=business_id,
                app_id=app_id,
                report_id=report_id,
                external_id=external_id,
            )
        )

        report_type: Optional[str] = report.get('reportType')
        if report_type:
            chart_data_new: List[Dict] = (
                self._transform_report_data_to_chart_data(report_data)
            )

            chart_data: Dict = report.get('chartData')
            if chart_data:
                chart_data = chart_data + chart_data_new
            else:
                chart_data = chart_data_new

            try:
                report_data_ = {
                    'chartData': json.dumps(chart_data),
                }
            except TypeError:
                # If we have date or datetime values
                # then we need to convert them to isoformat
                for datum in chart_data:
                    for k, v in datum.items():
                        if isinstance(v, dt.date) or isinstance(v, dt.datetime):
                            datum[k] = v.isoformat()

                report_data_ = {
                    'chartData': json.dumps(chart_data),
                }

            self._update_report(
                business_id=business_id,
                app_id=app_id,
                report_id=report_id,
                report_metadata=report_data_,
            )
        else:  # Then it is a table
            self._delete_report_entries(
                business_id=business_id,
                app_id=app_id,
                report_id=report_id,
            )

            self._create_report_entries(
                business_id=business_id,
                app_id=app_id,
                report_id=report_id,
                items=report_data,
            )


class DataSetManagingApi(DataExplorerApi, DataValidation):
    """
    """

    def __init__(self, api_client):
        self.api_client = api_client

# TODO
    def _convert_dataframe_to_dataset_data(
        self, df: DataFrame,
        filter_map: Optional[Dict[str, str]] = None,
        filter_fields: Optional[Dict[str, List[str]]] = None,
        search_columns: Optional[List[str]] = None,
    ) -> List[Dict]:
        """
        :param df:
        :param report_id:
        :param filter_fields: Example: {
                'stringField1': ['high', 'medium', 'low'],
                'stringField2': ['probable', 'improbable'],
            }
        :param search_columns:
        """
        cols: List[str] = df.columns.tolist()

        if filter_fields:
            try:
                assert len(filter_fields) <= 4
            except AssertionError:
                raise ValueError(
                    f'At maximum a table may have 4 different filters | '
                    f'You provided {len(filter_fields)} | '
                    f'You provided {filter_fields}'
                )

            df_ = df.rename(columns=filter_map)
            metadata_entries: Dict = df_[list(filter_map.values())].to_dict(orient='records')
        elif search_columns:
            df_ = df.rename(columns=filter_map)
            filter_search_map: List = [
                v for k, v in filter_map.items() if k in search_columns
            ]
            metadata_entries: Dict = df_[filter_search_map].to_dict(orient='records')
        else:
            data_columns: List[str] = cols
            metadata_entries: List[Dict] = []

        records: List[Dict] = df.to_dict(orient='records')
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

# TODO
    def append_dataset_data(
        self, business_id: str, app_id: str,
        report_data: Union[List[Dict], str, DataFrame, Dict],
        report_id: Optional[str] = None,
        external_id: Optional[str] = None,
    ) -> None:
        """Having a dataframe of Report

        It is an aggregation, meaning we preserve all previous
        data and just concatenate the new ones
        """
        _ = self._validate_data_is_pandarable(report_data)

        if self._is_report_data_empty(report_data):
            return

        report: Dict = (
            self._get_report_with_data(
                business_id=business_id,
                app_id=app_id,
                report_id=report_id,
                external_id=external_id,
            )
        )

        if report.get('reportType'):  # For non-table chart
            chart_data_new: List[Dict] = (
                self._transform_report_data_to_chart_data(report_data)
            )

            chart_data: Dict = report.get('chartData')

            # Data resistance
            #  check that the column names are the
            #  same in the data we try to append
            all_keys: Set[str] = set(chain.from_iterable(chart_data))
            for d in chart_data_new:
                try:
                    assert set(sorted((d.keys()))) == all_keys
                except AssertionError:
                    KeyError(
                        f'The provided data has not the same keys'
                        f' that the data it tries to append | '
                        f'Required keys: {all_keys}'
                    )

            if chart_data:
                chart_data = chart_data + chart_data_new
            else:
                chart_data = chart_data_new

            try:
                report_data_ = {
                    'chartData': json.dumps(chart_data),
                }
            except TypeError:
                # If we have date or datetime values
                # then we need to convert them to isoformat
                for datum in chart_data:
                    for k, v in datum.items():
                        if isinstance(v, dt.date) or isinstance(v, dt.datetime):
                            datum[k] = v.isoformat()

                report_data_ = {
                    'chartData': json.dumps(chart_data),
                }

            self._update_report(
                business_id=business_id,
                app_id=app_id,
                report_id=report_id,
                report_metadata=report_data_,
            )
        else:  # Then it is a table
            item: Dict = {'reportId': report_id}

            data: List[Dict] = (
                self.convert_dataframe_to_report_entry(
                    report_id=report_id, df=report_data,
                )
            )

            # TODO we can store batches and go faster than one by one
            for datum in data:
                item.update(datum)
                self.post_report_entry(item)
