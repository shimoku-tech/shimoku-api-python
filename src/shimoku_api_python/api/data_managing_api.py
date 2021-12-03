""""""
import json
from typing import List, Dict, Optional, Union

from pandas import DataFrame

from .report_metadata_api import ReportMetadataApi


# TODO to add data resistance will be required to check df integrity, etc
# TODO allow dataframe but also List[Dict] of json as input


class DataExplorerApi:
    get_report = ReportMetadataApi.get_report
    update_report = ReportMetadataApi.update_report

    get_report_by_external_id = ReportMetadataApi.get_report_by_external_id


class DataManagingApi(DataExplorerApi):
    """
    """

    def __init__(self, api_client):
        self.api_client = api_client

    @staticmethod
    def _is_report_data_empty(
        report_data: Union[List[Dict], str, DataFrame],
    ) -> bool:
        if isinstance(report_data, DataFrame):
            if report_data.empty:
                return True
            else:
                return False
        elif isinstance(report_data, list):
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

    @staticmethod
    def _transform_report_data_to_chart_data(
        report_data: Union[List[Dict], str, DataFrame],
    ) -> List[Dict]:
        if isinstance(report_data, DataFrame):
            chart_data: List[Dict] = report_data.to_dict(orient='records')
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

    def convert_dataframe_to_report_entry(
        self, business_id: str, app_id: str, df: DataFrame,
        report_id: Optional[str] = None,
        external_id: Optional[str] = None,
    ) -> List[Dict]:
        if report_id:
            pass
        elif external_id:
            report_id: str = (
                self.get_report_by_external_id(
                    business_id=business_id,
                    app_id=app_id,
                    external_id=external_id,
                )
            )
        else:
            raise ValueError('Either report_id or external_id must be provided')

        # Save the initial columns that are
        # all the fields that will get into `data`
        # column in `reportEntry` table
        data_columns: List[str] = [
            col
            for col in df.columns
            if col != 'description'
        ]

        fields: Dict = self.get_report_fields(report_id=report_id)
        # Some QA
        # Validate that all the filter column names
        # are in the dataframe otherwise raise an error
        cols: List[str] = df.columns
        for real_name, abstract_name in fields.items():
            assert real_name in cols
            try:
                df[abstract_name['field']] = df[real_name]
            except AttributeError:
                continue
            except TypeError:
                continue

        # pick all columns that are not in `data`. Including `description`
        non_data_columns = [
            col
            for col in df.columns
            if col not in data_columns
        ]

        # `data` column in DynamoDB `ReportEntry`
        data_entries: List[Dict] = [
            {'data': d}
            for d in df[data_columns].to_dict(orient='records')
        ]
        # owner, reportId and abstract columns
        other_entries: List[Dict] = (
            df[non_data_columns].to_dict(orient='records')
        )

        # Generate the list of single entries with all
        # necessary information to be posted
        entries: List[Dict] = [
            {**data_entry, **other_entry}
            for data_entry, other_entry in zip(data_entries, other_entries)
        ]

        return entries

    # TODO pending data resistance
    def append_report_data(
        self, business_id: str, app_id: str,
        report_data: Union[List[Dict], str, DataFrame],
        report_id: Optional[str] = None,
        external_id: Optional[str] = None,
    ) -> None:
        """Having a dataframe of Report

        It is an aggregation, meaning we preserve all previous
        data and just concatenate the new ones
        """
        if self._is_report_data_empty(report_data):
            return

        if report_id:
            report: Dict = (
                self.get_report(
                    business_id=business_id,
                    app_id=app_id,
                    report_id=report_id
                )
            )
        elif external_id:
            report: Dict = (
                self.get_report_by_external_id(
                    business_id=business_id,
                    app_id=app_id,
                    external_id=external_id,
                )
            )
            report_id: str = report['id']
        else:
            raise ValueError('Either report_id or external_id must be provided')

        if report.get('reportType'):
            chart_data_new: List[Dict] = (
                self._transform_report_data_to_chart_data(report_data)
            )

            chart_data: Dict = report['chartData']
            chart_data.update(chart_data_new)

            report_data_ = {'chartData': chart_data}
            self.update_report(
                report_id=report_id,
                report_data=report_data_,
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
        report_data: Union[Dict, str, DataFrame],
        report_id: Optional[str] = None,
        external_id: Optional[str] = None,
    ) -> None:
        """Remove old add new"""
        if self._is_report_data_empty(report_data):
            return

        if report_id:
            report: Dict = (
                self.get_report(
                    business_id=business_id,
                    app_id=app_id,
                    report_id=report_id
                )
            )
        elif external_id:
            report: Dict = (
                self.get_report_by_external_id(
                    business_id=business_id,
                    app_id=app_id,
                    external_id=external_id,
                )
            )
            report_id: str = report['id']
        else:
            raise ValueError('Either report_id or external_id must be provided')

        if report.get('reportType'):
            chart_data: List[Dict] = (
                self._transform_report_data_to_chart_data(report_data)
            )

            report_data_ = {'chartData': chart_data}
            self.update_report(
                business_id=business_id,
                app_id=app_id,
                report_id=report_id,
                report_data=report_data_,
            )
        else:  # Then it is a table
            # TODO method pending to be created
            self.delete_report_data(
                business_id=business_id,
                app_id=app_id,
                report_id=report_id,
            )

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
