""""""
import json
from typing import List, Dict, Optional, Union

from pandas import DataFrame

from .explorer_api import ReportExplorerApi
from .data_managing_api import DataManagingApi


class PlotApi(ReportExplorerApi):
    """
    """

    def __init__(self, api_client):
        self.api_client = api_client
        self.business_id: str
        self.app_id: str

    def set_vars(
        self, business_id: str, app_id: str,
    ):
        """"""
        self.business_id: str = business_id
        self.app_id: str = app_id

    def bar(
        self, data: Union[str, DataFrame, List[Dict]],
        x: str, y: str,  # first layer
        path: str, row: int, column: int,  # report creation
        title: str, color: str,  # second layer
        third_layer: Dict,
    ):
        """"""
        reports = self.get_reports_in_app()

        if reports:
            order = min([report['order'] for report in reports if report['path'] == path])
        else:
            orders = max([report['order'] for report in reports])
            order: int = orders + 1

        report_metadata = {
            'path': path,
            'reportType': 'BARCHART',
            'title': 'title',
            'grid': f'{row}, {column}',
            'order': order,
        }

        report: Dict = self.create_report(
            business_id=self.business_id,
            app_id=self.app_id,
            report_metadata=report_metadata,
        )
        report_id: str = report['id']

        self.update_report_data(
            business_id=self.business_id,
            app_id=self.app_id,
            report_id=report_id,
            report_data=data,
        )

        return report

    def line(
        self, data: Union[str, DataFrame, List[Dict]],
        x: str, y: str,  # first layer
        path: str, row: int, column: int,  # report creation
        title: str, color: str,  # second layer
        third_layer: Dict,
    ):
        """"""
        reports = self.get_reports_in_app()

        if reports:
            order = min([report['order'] for report in reports if report['path'] == path])
        else:
            orders = max([report['order'] for report in reports])
            order: int = orders + 1

        report_metadata = {
            'path': path,
            'reportType': 'BARCHART',
            'title': 'title',
            'grid': f'{row}, {column}',
            'order': order,
        }

        report: Dict = self.create_report(
            business_id=self.business_id,
            app_id=self.app_id,
            report_metadata=report_metadata,
        )
        report_id: str = report['id']

        self.update_report_data(
            business_id=self.business_id,
            app_id=self.app_id,
            report_id=report_id,
            report_data=data,
        )

        return report

    def predictive_line(
        self, data: Union[str, DataFrame, List[Dict]],
        x: str, y: str,  # first layer
        path: str, row: int, column: int,  # report creation
        title: str, color: str,  # second layer
        third_layer: Dict,
    ):
        """"""
        reports = self.get_reports_in_app()

        if reports:
            order = min([report['order'] for report in reports if report['path'] == path])
        else:
            orders = max([report['order'] for report in reports])
            order: int = orders + 1

        report_metadata = {
            'path': path,
            'reportType': 'BARCHART',
            'title': 'title',
            'grid': f'{row}, {column}',
            'order': order,
        }

        report: Dict = self.create_report(
            business_id=self.business_id,
            app_id=self.app_id,
            report_metadata=report_metadata,
        )
        report_id: str = report['id']

        self.update_report_data(
            business_id=self.business_id,
            app_id=self.app_id,
            report_id=report_id,
            report_data=data,
        )

        return report

    def stockline(
        self, data: Union[str, DataFrame, List[Dict]],
        x: str, y: str,  # first layer
        path: str, row: int, column: int,  # report creation
        title: str, color: str,  # second layer
        third_layer: Dict,
    ):
        """"""
        reports = self.get_reports_in_app()

        if reports:
            order = min([report['order'] for report in reports if report['path'] == path])
        else:
            orders = max([report['order'] for report in reports])
            order: int = orders + 1

        report_metadata = {
            'path': path,
            'reportType': 'BARCHART',
            'title': 'title',
            'grid': f'{row}, {column}',
            'order': order,
        }

        report: Dict = self.create_report(
            business_id=self.business_id,
            app_id=self.app_id,
            report_metadata=report_metadata,
        )
        report_id: str = report['id']

        self.update_report_data(
            business_id=self.business_id,
            app_id=self.app_id,
            report_id=report_id,
            report_data=data,
        )

        return report

    def scatter(
        self, data: Union[str, DataFrame, List[Dict]],
        x: str, y: str,  # first layer
        path: str, row: int, column: int,  # report creation
        title: str, color: str,  # second layer
        third_layer: Dict,
    ):
        """"""
        reports = self.get_reports_in_app()

        if reports:
            order = min([report['order'] for report in reports if report['path'] == path])
        else:
            orders = max([report['order'] for report in reports])
            order: int = orders + 1

        report_metadata = {
            'path': path,
            'reportType': 'BARCHART',
            'title': 'title',
            'grid': f'{row}, {column}',
            'order': order,
        }

        report: Dict = self.create_report(
            business_id=self.business_id,
            app_id=self.app_id,
            report_metadata=report_metadata,
        )
        report_id: str = report['id']

        self.update_report_data(
            business_id=self.business_id,
            app_id=self.app_id,
            report_id=report_id,
            report_data=data,
        )

        return report

    def set_filter():
        raise NotImplementedError
