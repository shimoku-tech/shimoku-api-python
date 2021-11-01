""""""
from abc import ABC
from typing import List, Dict

from shimoku_api_python.api.explorer_api import AppExplorerApi


class AppMetadataApi(AppExplorerApi, ABC):
    """
    """

    def __init__(self, api_client):
        self.api_client = api_client

    def get_target_grid_row_position_reports(
        self, app_id: str, path_name: str, row_position: int,
    ) -> List[str]:
        """Given a grid row retrieve all report ids
        that belongs to that row position

        :param app_id: app UUID
        :param path_name: path name
        :param row_position: grid row position. Example: "3, 1" --> 3
        """
        target_report_ids: List[str] = list()
        report_ids: List[str] = (
            self.get_app_path_all_reports(
                app_id=app_id, path_name=path_name,
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
        self, app_id: str, path_name: str, grid_position: str,
    ) -> List[str]:
        """Given a grid retrieve all report ids
        that belongs to that grid position

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
                app_id=app_id, path_name=path_name,
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

    def change_app_name(
        self, app_id: str, new_app_name: str,
    ) -> None:
        """Update path name
        """
        app_data = {'name': new_app_name}
        self.update_app(
            app_id=app_id,
            app_data=app_data,
        )

    def change_hide_title(self, app_id: str, hide_title: bool = True) -> None:
        """Hide / show app title

        See https://trello.com/c/8e11jso4/ for further info
        """
        app_data = {'hideTitle': hide_title}
        self.update_app(
            app_id=app_id,
            app_data=app_data,
        )

    def change_path_name(
        self, app_id: str, old_path_name: str, new_path_name: str,
    ) -> None:
        """Update path name
        """
        report_ids: List[str] = (
            self.get_app_path_all_reports(app_id=app_id, path_name=old_path_name)
        )

        for report_id in report_ids:
            report: Dict = self.get_report(report_id)
            if report.get('path') == old_path_name:
                report_data = {'path': new_path_name}
                self.update_report(
                    report_id=report['id'],
                    report_data=report_data
                )

    # TODO sigue siendo una gran duda para mi como gestionaremos los AppType!!
    def get_app_apptype(self, app_id: str) -> Dict:
        """Given an app retrieve its `AppType`
        :param app_id: app UUID
        """
        raise NotImplemented

    # TODO this can be done?
    def change_path_position(
        self, app_id: str, old_path_name: str, new_path_name: str,
    ) -> None:
        """Update path name
        """
        raise NotImplementedError

    def change_report_grid_position(
        self, app_id: str, report_id: str,
        grid: str, reorganize_grid: bool = False
    ) -> None:
        """Update report.grid

        If reorganize_grid is False means that we will not
        move the other reports downside if this report gets in a position
        where other reports already exists or it has reports below.
        Otherwise it will move all the stack of reports downside to create room
        for this new position of this report
        """
        if reorganize_grid:
            report = self.get_report(report_id)
            path_name: str = report.get('path')

            if not path_name:
                raise NotImplementedError

            report_ids: List[str] = (
                self.get_app_path_all_reports(
                    app_id=app_id, path_name=path_name,
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
                        app_id=app_id, report_id=report_id,
                        grid=new_grid_position, reorganize_grid=False,
                    )

        report_data: Dict = {'grid': grid}
        self.update_report(
            report_id=report_id,
            report_data=report_data,
        )

    # TODO this updates the grid of every report in a path for it to work well
    def fix_path_reports_grid(self, app_id: str, path: str):
        raise NotImplementedError
