""""""

from abc import ABC
from typing import List, Dict, Union, Optional

import datetime as dt

from shimoku_api_python.api.explorer_api import ReportExplorerApi


class ReportMetadataApi(ReportExplorerApi, ABC):
    """
    """

    def __init__(self, api_client):
        self.api_client = api_client

    def _get_report_by_var(
        self, business_id: str, app_id: str,
        var_name: str, var_value: str,
        path: Optional[str] = None,
    ) -> Union[Dict, List[Dict]]:
        """Given a business retrieve all app metadata

        :param business_id: business UUID
        :param app_id: business UUID
        :param report_name:
        """
        endpoint: str = f'business/{business_id}/app/{app_id}'
        reports: Dict = (
            self.api_client.query_element(
                endpoint=endpoint, method='GET',
            )
        )

        # Is expected to be a single item (Dict) but an App
        # could have several reports with the same name
        result: Union[Dict, List[Dict]] = {}
        for report in reports:
            if path:
                if report.get('path') != path:
                    continue
            if report.get(var_name) == var_value:
                if result:
                    if len(result) == 1:
                        result: List[Dict] = [result] + [report]
                    else:
                        result: List[Dict] = result + [report]
                else:
                    result: Dict = report
        return result

    def has_report_data(
        self, business_id: str, app_id: str, report_id: str
    ) -> bool:
        """"""
        data: List[str] = self.get_report_data(
            business_id=business_id,
            app_id=app_id,
            report_id=report_id,
        )
        if data:
            return True
        else:
            return False

    def get_target_report_any_data(
        self, business_id: str, app_id: str, report_id: str
    ) -> List[str]:
        """Retrieve a subset of the chartData"""
        raise NotImplementedError

    def get_report_last_update(
        self, business_id: str, app_id: str, report_id: str,
    ) -> dt.datetime:
        """"""
        report: Dict = self.get_report(
            business_id=business_id,
            app_id=app_id,
            report_id=report_id,
        )
        # TODO check it returns dt.date
        return report['updatedAt']

    def get_report_data_fields(
        self, business_id: str, app_id: str, report_id: str,
    ) -> Dict:
        """
        """
        report: Dict = self.get_report(
            business_id=business_id,
            app_id=app_id,
            report_id=report_id,
        )
        return report['dataFields']

    def get_report_by_path(
        self, business_id: str, app_id: str,
        path: str,
    ) -> Union[Dict, List[Dict]]:
        """
        :param business_id: business UUID
        :param app_id: business UUID
        :param path:
        """
        return (
            self._get_report_by_var(
                business_id=business_id,
                app_id=app_id,
                var_name='path',
                var_value=path,
            )
        )

    def get_report_by_title(
        self, business_id: str, app_id: str,
        title: str, path: Optional[str] = None,
    ) -> Union[Dict, List[Dict]]:
        """
        :param business_id: business UUID
        :param app_id: business UUID
        :param title:
        :param path:
        """
        return (
            self._get_report_by_var(
                business_id=business_id,
                app_id=app_id,
                path=path,
                var_name='title',
                var_value=title,
            )
        )

    def get_report_by_external_id(
        self, business_id: str, app_id: str,
        external_id: str, path: Optional[str] = None,
    ) -> Union[Dict, List[Dict]]:
        """
        :param business_id: business UUID
        :param app_id: business UUID
        :param external_id:
        :param path:
        """
        return (
            self._get_report_by_var(
                business_id=business_id,
                app_id=app_id,
                path=path,
                var_name='codeETLId',
                var_value=external_id,
            )
        )

    def get_report_by_grid_position(
        self, business_id: str, app_id: str,
        row: int, column: int, path: Optional[str] = None,
    ) -> Union[Dict, List[Dict]]:
        """
        :param business_id: business UUID
        :param app_id: business UUID
        :param row:
        :param column:
        :param path:
        """
        grid: str = f'{row}, {column}'
        return (
            self._get_report_by_var(
                business_id=business_id,
                app_id=app_id,
                path=path,
                var_name='grid',
                var_value=grid,
            )
        )

    def get_report_by_chart_type(
        self, business_id: str, app_id: str,
        chart_type: str, path: Optional[str] = None,
    ) -> Union[Dict, List[Dict]]:
        """Given a business retrieve all app metadata

        :param business_id: business UUID
        :param app_id: business UUID
        :param chart_type:
        :param path:
        """
        return (
            self._get_report_by_var(
                business_id=business_id,
                app_id=app_id,
                path=path,
                var_name='reportType',
                var_value=chart_type,
            )
        )

    def update_report_title(
        self, business_id: str, app_id: str, report_id: str,
        title: str,
    ) -> Dict:
        """"""
        report_data = {'title': title}
        return (
            self.update_report(
                business_id=business_id,
                app_id=app_id,
                report_id=report_id,
                report_data=report_data,
            )
        )

    def update_report_external_id(
        self, business_id: str, app_id: str, report_id: str,
        new_external_id: str,
    ) -> Dict:
        report_data = {'externalId': new_external_id}
        return (
            self.update_report(
                business_id=business_id,
                app_id=app_id,
                report_id=report_id,
                report_data=report_data,
            )
        )

    def update_report_grid_position(
        self, business_id: str, app_id: str, report_id: str,
        row: int, column: int,
    ) -> Dict:
        """"""
        report_data = {'grid': f'{row}, {column}'}
        return (
            self.update_report(
                business_id=business_id,
                app_id=app_id,
                report_id=report_id,
                report_data=report_data,
            )
        )

    def update_report_chart_type(
        self, business_id: str, app_id: str, report_id: str,
        report_type: str,
    ) -> Dict:
        """Update report.reportType
        """
        report_data = {'reportType': report_type}
        return (
            self.update_report(
                business_id=business_id,
                app_id=app_id,
                report_id=report_id,
                report_data=report_data,
            )
        )

    def update_report_description(
        self, business_id: str, app_id: str, report_id: str,
        description: str,
    ) -> Dict:
        """"""
        report_data = {'description': description}
        return (
            self.update_report(
                business_id=business_id,
                app_id=app_id,
                report_id=report_id,
                report_data=report_data,
            )
        )

    def update_report_smart_filter(
        self, business_id: str, app_id: str, report_id: str,
        smart_filter: Dict,
    ) -> Dict:
        """"""
        report_data = {'smartFilter': smart_filter}
        return (
            self.update_report(
                business_id=business_id,
                app_id=app_id,
                report_id=report_id,
                report_data=report_data,
            )
        )

    def change_report_grid_position(
        self, business_id: str, app_id: str, grid: str,
        report_id: Optional[str] = None,
        external_id: Optional[str] = None,
        reorganize_grid: bool = False
    ) -> None:
        """Update report.grid

        If reorganize_grid is False means that we will not
        move the other reports downside if this report gets in a position
        where other reports already exists or it has reports below.
        Otherwise it will move all the stack of reports downside to create room
        for this new position of this report
        """
        if report_id:
            pass
        if external_id:
            report: Dict = self.get_report(
                business_id=business_id,
                app_id=app_id,
                external_id=external_id
            )
            report_id: str = report['id']
        else:
            raise ValueError('Either report_id or extenral_id must be provided')

        if reorganize_grid:
            report = self.get_report(report_id)
            path_name: str = report.get('path')

            if not path_name:
                raise NotImplementedError

            report_ids: List[str] = (
                self.get_app_path_all_reports(
                    business_id=business_id,
                    app_id=app_id,
                    path_name=path_name,
                )
            )

            for report_id in report_ids:
                report = self.get_report(report_id)
                if int(report['grid'][0]) < grid:
                    continue
                else:
                    # IMPORTANT
                    # This is recursive, watch out!
                    new_grid_row: int = int(report['grid'][0]) + 1
                    new_grid_position: str = (
                        f"{new_grid_row},{report['grid'].split(',')[1]}"
                    )
                    self.change_report_grid_position(
                        business_id=business_id,
                        app_id=app_id,
                        report_id=report_id,
                        grid=new_grid_position, reorganize_grid=False,
                    )

        report_data: Dict = {'grid': grid}
        self.update_report(
            report_id=report_id,
            report_data=report_data,
        )
