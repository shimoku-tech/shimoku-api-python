""""""

from typing import List, Dict, Optional, Union

from pandas import DataFrame

from .explorer_api import ReportExplorerApi


# TODO to add data resistance will be required to check df integrity, etc
# TODO allow dataframe but also List[Dict] of json as input


class DataManagingApi(ReportExplorerApi):
    """
    """

    def __init__(self, api_client):
        self.api_client = api_client


# TODO permitir external_report_id como input

    def convert_dataframe_to_report_entry(
        self, report_id: str, df: DataFrame
    ) -> List[Dict]:
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

    # TODO allow report_data it to be also a json!! '[{...}, {...}]'
    # TODO pending data resistance
    def append_report_data(
        self, report_id: str, report_data: DataFrame,
    ) -> None:
        """Having a dataframe of Report

        It is an aggregation, meaning we preserve all previous
        data and just concatenate the new ones
        """
        report: Dict = self.get_report(report_id)

        new_data: Dict = report_data.to_dict(orient='records')

        if report['reportType']:
            chart_data: Dict = report['chartData']
            chart_data.update(new_data)

            report_data_ = {'chartData': chart_data}
            self.update_report(
                report_id=report_id,
                report_data=report_data_,
            )
        else:  # Then it is a table
            item: Dict = {
                'owner_id': report['ownerId'],
                'reportId': report_id,
                '__typename': 'ReportEntry',
            }

            data: List[Dict] = (
                self.convert_dataframe_to_report_entry(
                    report_id=report_id, df=report_data,
                )
            )

            # TODO we can store batches and go faster than one by one
            for datum in data:
                item.update(datum)
                self.post_report_entry(item)

    # TODO allow report_data to be also a json!! '[{...}, {...}]'
    def update_report_data(
        self, report_id: str, report_data: DataFrame,
    ) -> None:
        """Remove old add new"""
        report: Dict = self.get_report(report_id)
        chart_data: Dict = report_data.to_dict(orient='records')

        if report['reportType']:
            report_data_ = {'chartData': chart_data}
            self.update_report(
                report_id=report_id,
                report_data=report_data_,
            )
        else:  # Then it is a table
            self.delete_report_data(report_id)

            item: Dict = {
                'owner_id': report['ownerId'],
                'reportId': report_id,
                '__typename': 'ReportEntry',
            }

            data: List[Dict] = (
                self.convert_dataframe_to_report_entry(
                    report_id=report_id, df=report_data,
                )
            )

            # TODO we can store batches and go faster than one by one
            for datum in data:
                item.update(datum)
                self.post_report_entry(item)

    # TODO
    def add_fixture_data(self):
        raise NotImplementedError
