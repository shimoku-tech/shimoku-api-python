""""""

from abc import ABC
from typing import List, Dict

import datetime as dt

from shimoku_api_python.api.explorer_api import ReportExplorerApi


class ReportMetadataApi(ReportExplorerApi, ABC):
    """
    """

    def __init__(self, api_client):
        self.api_client = api_client

    def has_report_data(self, report_id: str) -> bool:
        """"""
        data: List[str] = self.get_report_data(report_id=report_id)
        if data:
            return True
        else:
            return False

    def get_target_report_any_data(self, report_id: str) -> List[str]:
        """Retrieve a subset of the chartData"""
        raise NotImplementedError

    def get_report_last_update(self, report_id: str) -> dt.datetime:
        """"""
        report: Dict = self.get_report(report_id)
        # TODO check it returns dt.date
        return report['updatedAt']

    def get_report_data_fields(self, report_id: str) -> Dict:
        """
        """
        report: Dict = self.get_report(report_id)
        # TODO check it returns Dict
        return report['dataFields']

    def get_report_fields(self, report_id: str):
        """"""
        raise NotImplementedError

    # TODO some data resistence here to avoid it to get broken
    def update_report_fields(
        self, report_id: str, data_fields: str,
    ) -> None:
        """"""
        report_data = {'dataFields': data_fields}
        self.update_report(
            report_id=report_id,
            report_data=report_data,
        )

    def update_report_description(
        self, report_id: str, description: str,
    ) -> None:
        """"""
        report_data = {'description': description}
        self.update_report(
            report_id=report_id,
            report_data=report_data,
        )

    def update_report_chart_type(self, report_id: str, report_type: str) -> None:
        """Update report.reportType
        """
        report_data = {'reportType': report_type}
        self.update_report(
            report_id=report_id,
            report_data=report_data,
        )

    def update_report_external_id(self, report_id: str, new_external_id: str):
        report_data = {'externalId': new_external_id}
        self.update_report(
            report_id=report_id,
            report_data=report_data,
        )

# TODO get_report_by_external_id(self, external_id: str) -> str
