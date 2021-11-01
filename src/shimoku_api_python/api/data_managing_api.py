""""""

from typing import List, Dict, Optional, Union

from pandas import DataFrame


# TODO to add data resistance will be required to check df integrity, etc


class DataManagingApi(object):
    """
    """

    def __init__(self, api_client):
        self.api_client = api_client

    def get_target_report_any_data(self, report_id: str) -> List[str]:
        """"""
        table_name: str = f'ReportEntry-{self.table_name_suffix}'
        filter_expression = 'reportId = :reportId'
        filter_values = {':reportId': {'S': report_id}}
        scan_filter = {
            'filter_expression': filter_expression,
            'filter_values': filter_values,
        }

        report_entry: List[str] = (
            self.get_any_item(
                table_name=table_name,
                filters=scan_filter,
            )
        )
        return report_entry

# TODO
    def has_path_data(self, app_id: str, path_name: str) -> bool:
        """"""
        reports: List[str] = self.get_target_app_all_reports(app_id)
        for report_id in reports:
            result: bool = self.has_report_report_entries(report_id)
            if result:
                return True
        return False

    def has_report_data(self, report_id) -> bool:
        """"""
        data = self.get_target_report_any_report_entry(report_id)
        if data:
            return True
        return False

# TODO allow report_data it to be also a json!! '[{...}, {...}]'
    def add_report_data(
        self, report_data: pd.DataFrame, report_id: str,
    ) -> None:
        """Having a dataframe of Report
        add all of them to Report.ChartData

        It is an aggregation, meaning we preserve all previous
        Report.ChartData and just concatenate the new ones
        """
        table_name: str = f'Report-{self.table_name_suffix}'

        report: Dict = self.get_target_report(report_id)
        chart_data: Dict = report['chartData']
        new_data: Dict = report_df.to_dict(orient='records')
        chart_data.update(new_data)

        # filter_expression = 'id = :report_id'
        # filter_values = {':report_id': {'S': report_id}}
        constraints: Dict = {
            'id': {'S': report_id},
        }

        update_expression: str = f'chartData = :chartData'
        attribute_vals: Dict = {
            ':chartData': chart_data,
        }

        self.update_item(
            table_name=table_name, constraints=constraints,
            update_expression=update_expression,
            attribute_vals=attribute_vals,
            action="set",
        )

# TODO
# TODO allow it to be also a json!! '[{...}, {...}]'
    def append_data(self):
        pass

    # TODO allow report_data to be also a json!! '[{...}, {...}]'
    def update_report_chart_data(
        self, report_data: pd.DataFrame, report_id: str,
    ) -> None:
        """Update report.chartData

        report_df is actually a string
        """
        table_name: str = f'Report-{self.table_name_suffix}'
        # filter_expression = 'id = :report_id'
        # filter_values = {':report_id': {'S': report_id}}
        constraints: Dict = {
            'id': {'S': report_id},
        }

        update_expression: str = f'chartData = :chartData'
        attribute_vals: Dict = {
            ':chartData': report_df.to_dict(orient='records'),
        }

        self.update_item(
            table_name=table_name, constraints=constraints,
            update_expression=update_expression,
            attribute_vals=attribute_vals,
            action="set",
        )

    def post_report_data(
        self, df: pd.DataFrame,
        report_id: str, owner_id: str,
    ):
        """Having a dataframe of Report Entries
        post all of them (row by row) to Dynamo

        First we need to create in the dataframe the abstract columns
        Second we store as a dict the initial dataframe
        Third we store in another dict the sub-dataframe of abstract columns and metadata
        Finally we merge both in a single list of dicts that post massively to Dynamo

        IMPORTANT
        --------------------
        Note it can also be used to add new report entries if used directly
        """
        table_name: str = f'ReportEntry-{self.table_name_suffix}'

        # Save the initial columns that are
        # all the fields that will get into `data`
        # column in `reportEntry` table
        data_columns: List[str] = [
            col
            for col in df.columns
            if col != 'description'
        ]

        # Note now is in UTC
        now = dt.datetime.utcnow().isoformat()
        df['owner'] = owner_id
        df['reportId'] = report_id
        df['createdAt'] = now
        df['updatedAt'] = now
        df['__typename'] = 'ReportEntry'
        # Set hashes for id
        df['id'] = [str(uuid.uuid4()) for _ in range(len(df.index))]

        # Retrieve reportEntry abstract str and numeric fields
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

        # query_conditions = Key('reportId').eq(report_id)
        # post all entries to Dynamo
        self.put_many_items(
            table_name=table_name, items=entries,
        )

    def add_fixture_data(self):
        raise NotImplementedError
