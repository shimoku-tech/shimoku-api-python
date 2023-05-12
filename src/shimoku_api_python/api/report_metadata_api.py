from typing import List, Dict, Optional, TYPE_CHECKING

from ..resources.app import App

from ..async_execution_pool import async_auto_call_manager, ExecutionPoolContext

import logging
from ..execution_logger import logging_before_and_after
logger = logging.getLogger(__name__)


class ReportMetadataApi:
    """
    """

    @logging_before_and_after(logging_level=logger.debug)
    def __init__(self, app: 'App', execution_pool_context: ExecutionPoolContext):
        self._app = app
        self.epc = execution_pool_context

    @logging_before_and_after(logging_level=logger.debug)
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

    @logging_before_and_after(logging_level=logger.debug)
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

    @logging_before_and_after(logging_level=logger.debug)
    def get_reports_by_path(
        self, business_id: str, app_id: str,
        path: str,
    ) -> List[Dict]:
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

    @logging_before_and_after(logging_level=logger.debug)
    def get_reports_in_same_path(
        self, business_id: str, app_id: str, report_id: str,
    ) -> List[Dict]:
        """
        :param business_id: business UUID
        :param app_id: business UUID
        :param report_id:
        """
        report: Dict = self.get_report(
            business_id=business_id,
            app_id=app_id,
            report_id=report_id,
        )
        report_path = report.get('path')
        output_reports: List[Dict] = list()

        if report_path:
            reports: List[Dict] = self._get_app_reports(
                business_id=business_id,
                app_id=app_id
            )
            for report_ in reports:
                if report_.get('path') == report_path:
                    output_reports = output_reports + [report_]
            return output_reports
        else:
            return []

    @logging_before_and_after(logging_level=logger.debug)
    def get_reports_by_title(
        self, business_id: str, app_id: str,
        title: str, path: Optional[str] = None,
    ) -> List[Dict]:
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

    @logging_before_and_after(logging_level=logger.debug)
    def get_reports_by_external_id(
        self, business_id: str, app_id: str,
        external_id: str, path: Optional[str] = None,
    ) -> List[Dict]:
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

    @logging_before_and_after(logging_level=logger.debug)
    def get_reports_by_grid_position(
        self, business_id: str, app_id: str,
        row: int, column: int, path: Optional[str] = None,
    ) -> List[Dict]:
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

    @logging_before_and_after(logging_level=logger.debug)
    def get_reports_by_chart_type(
        self, business_id: str, app_id: str,
        chart_type: str, path: Optional[str] = None,
    ) -> List[Dict]:
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

    @logging_before_and_after(logging_level=logger.debug)# TODO pending
    def get_reports_by_path_grid_and_type(
        self, business_id: str, app_id: str,
        grid: str, chart_type: str, path: str,
    ):
        """"""
        raise NotImplementedError

    @logging_before_and_after(logging_level=logger.debug)
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

    @logging_before_and_after(logging_level=logger.debug)
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

    @logging_before_and_after(logging_level=logger.debug)
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

    @logging_before_and_after(logging_level=logger.debug)
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

    @logging_before_and_after(logging_level=logger.debug)
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

    @logging_before_and_after(logging_level=logger.debug)
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

    @logging_before_and_after(logging_level=logger.debug)
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

    @logging_before_and_after(logging_level=logger.debug)
    def fetch_filter_report(
        self, business_id: str, app_id: str, report_id: str,
    ) -> Dict:
        """Having a report_id return all reports that filter that one"""
        report: Dict = self.get_report(report_id)
        reports: List[Dict] = self._get_app_reports(
            business_id=business_id,
            app_id=app_id,
        )

        filter_report_candidates: List[Dict] = [
            # TODO falta aplicar una funcion aqui abajo:
            report['dataFields']
            for report_ in reports
            if report_['reportType'].lower() == 'filter'
        ]

        for filter_report_candidate in filter_report_candidates:
            if report_id in filter_report_candidate:
                return # TODO pensarlo mejor

    @logging_before_and_after(logging_level=logger.debug)
    def get_filter_report(
        self, business_id: str, app_id: str,
        report_id: Optional[str] = None,
        report_filter_id: Optional[str] = None,
    ) -> Dict:
        if report_id:
            return self.fetch_filter_report(
                business_id=business_id,
                app_id=app_id,
                report_id=report_id,
            )
        elif report_filter_id:
            return self.get_report(
                business_id=business_id,
                app_id=app_id,
                report_id=report_id,
            )
        else:
            raise ValueError(
                'Either report_id or report_filter_id must be provided'
            )

    @logging_before_and_after(logging_level=logger.debug)
    def hide_report(self, business_id: str, app_id: str, report_id: str):
        report_metadata: Dict = {'isDisabled': True}
        self.update_report(
            business_id=business_id,
            app_id=app_id,
            report_id=report_id,
            report_metadata=report_metadata,
        )

    @logging_before_and_after(logging_level=logger.debug)
    def unhide_report(self, business_id: str, app_id: str, report_id: str):
        report_metadata: Dict = {'isDisabled': False}
        self.update_report(
            business_id=business_id,
            app_id=app_id,
            report_id=report_id,
            report_metadata=report_metadata,
        )
