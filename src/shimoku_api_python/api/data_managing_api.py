""""""
import json
from typing import List, Dict, Optional, Union, Set
from itertools import chain

import datetime as dt
import pandas as pd
from pandas import DataFrame

from .explorer_api import GetExplorerAPI, DeleteExplorerApi, CreateExplorerAPI
from .report_metadata_api import ReportMetadataApi


class DataExplorerApi:
    get_report = ReportMetadataApi.get_report
    _get_report_with_data = GetExplorerAPI._get_report_with_data
    get_report_data = ReportMetadataApi.get_report_data
    _update_report = ReportMetadataApi.update_report

    _create_report_entries = CreateExplorerAPI._create_report_entries
    _delete_report_entries = DeleteExplorerApi.delete_report_entries

    _get_report_by_external_id = ReportMetadataApi.get_reports_by_external_id


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


class DataManagingApi(DataExplorerApi, DataValidation):
    """
    """

    def __init__(self, api_client):
        self.api_client = api_client

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

    def _transform_report_data_to_chart_data(
        self, report_data: Union[List[Dict], str, DataFrame, Dict],
    ) -> List[Dict]:
        if isinstance(report_data, DataFrame):
            chart_data: List[Dict] = report_data.to_dict(orient='records')
        elif isinstance(report_data, dict):
            df_: DataFrame = pd.DataFrame(report_data)
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

    def _convert_dataframe_to_report_entry(
        self, df: DataFrame,
        filter_map: Optional[Dict[str, str]] = None,
        filter_fields: Optional[Dict[str, List[str]]] = None,
        sort_table_by_col: Optional[Dict[str, List[str]]] = None,
    ) -> List[Dict]:
        """
        :param df:
        :param report_id:
        :param filter_fields: Example: {
                'stringField1': ['high', 'medium', 'low'],
                'stringField2': ['probable', 'improbable'],
            }
        :param sort_table_by_col: Example : {
            'date': 'asc'
        }
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

        if report.get('reportType'):
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
