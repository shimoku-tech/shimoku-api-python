""""""

from abc import ABC
from typing import List, Dict, Optional

from shimoku_api_python.api.explorer_api import PathExplorerApi


class PathMetadataApi(PathExplorerApi, ABC):
    """
    """

    def __init__(self, api_client):
        self.api_client = api_client

    def check_if_path_exists(
        self, business_id: str, app_id: str, path_name: str
    ) -> bool:
        reports: List[Dict] = (
            self.get_path_reports(
                business_id=business_id,
                app_id=app_id,
                path_name=path_name,
            )
        )
        if reports:
            return True
        else:
            return False

    def get_path_position(
        self, business_id: str, app_id: str, path_name: str
    ) -> Optional[int]:
        reports: List[Dict] = (
            self.get_path_reports(
                business_id=business_id,
                app_id=app_id,
                path_name=path_name,
            )
        )
        orders: List[int] = [report.get('order') for report in reports]

        if orders:
            return min(orders)
        else:
            return

    def get_target_grid_row_position_reports(
        self, business_id: str, app_id: str, path_name: str,
        row_position: int,
    ) -> List[str]:
        """Given a grid row retrieve all report ids
        that belongs to that row position

        :param business_id:
        :param app_id: app UUID
        :param path_name: path name
        :param row_position: grid row position. Example: "3, 1" --> 3
        """
        target_report_ids: List[str] = list()
        report_ids: List[str] = (
            self.get_app_path_all_reports(
                business_id=business_id,
                app_id=app_id,
                path_name=path_name,
            )
        )

        for report_id in report_ids:
            report: Dict = self.get_report(report_id)
            if report.get('path') == path_name:
                if report.get('grid'):
                    clean_row_position = int(report['grid'].split(',')[0])
                    if clean_row_position == row_position:
                        report_ids.append(report['id'])

        return target_report_ids

    def get_target_grid_position_reports(
        self, business_id: str, app_id: str, path_name: str,
        grid_position: str,
    ) -> List[str]:
        """Given a grid retrieve all report ids
        that belongs to that grid position

        :param business_id:
        :param app_id: app UUID
        :param path_name: path name
        :param grid_position: grid row position. Example: "3, 1"
        """
        assert ',' in grid_position

        try:
            row_position: int = int(grid_position.strip().split(',')[0])
            column_position: int = int(grid_position.strip().split(',')[1])
        except ValueError:
            raise ValueError(
                'grid_position must have the shape "X, Y" '
                'where X and Y must be integers'
            )

        report_ids: List[str] = (
            self.get_target_grid_row_position_reports(
                business_id=business_id,
                app_id=app_id,
                path_name=path_name,
                row_position=row_position,
            )
        )

        target_report_ids: List[str] = []
        for report_id in report_ids:
            report: Dict = self.get_report(report_id)
            if report.get('grid'):
                report_column_position: int = (
                    int(report.get('grid').strip().split(',')[1])
                )
                if report_column_position == column_position:
                    target_report_ids.append(report['id'])

        return target_report_ids

    def change_path_name(
        self, business_id: str, app_id: str,
        old_path_name: str, new_path_name: str,
    ) -> None:
        """Update path name
        """
        reports: List[Dict] = (
            self.get_app_path_all_reports(
                business_id=business_id,
                app_id=app_id,
                path_name=old_path_name,
            )
        )

        for report in reports:
            if report.get('path') == old_path_name:
                report_data = {'path': new_path_name}
                self.update_report(
                    report_id=report['id'],
                    report_data=report_data
                )

    # TODO this can be done?
    def change_path_position(
        self, business_id: str, app_id: str, new_position: int,
    ) -> None:
        """Update path name
        """
        raise NotImplementedError

    # TODO this updates the grid of every report in a path for it to work well
    def fix_path_reports_grid(
        self, business_id: str, app_id: str, path_name: str,
    ):
        raise NotImplementedError

