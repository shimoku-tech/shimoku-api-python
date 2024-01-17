from typing import List, Dict, Optional
from ..resources.app import App
from ..resources.report import Report

from ..async_execution_pool import ExecutionPoolContext, async_auto_call_manager

import logging
from ..execution_logger import logging_before_and_after
logger = logging.getLogger(__name__)


class ReportMetadataApi:
    """
    """

    @logging_before_and_after(logging_level=logger.debug)
    def __init__(self, app: Optional['App'], execution_pool_context: ExecutionPoolContext):
        self._app = app
        self.epc = execution_pool_context

    @async_auto_call_manager(execute=True)
    @logging_before_and_after(logging_level=logger.info)
    async def get_components_in_sub_path(self, path: str) -> List[Dict]:
        """
        :param path: path to the components
        :return: list of components
        """
        return [report.cascade_to_dict() for report in (await self._app.get_reports()) if report['path'] == path]

    @async_auto_call_manager(execute=True)
    @logging_before_and_after(logging_level=logger.info)
    async def get_component(self, uuid: str) -> Dict:
        """
        :param uuid: uuid of the component
        :return: component
        """
        return (await self._app.get_report(uuid=uuid)).cascade_to_dict()

    @async_auto_call_manager(execute=True)
    @logging_before_and_after(logging_level=logger.info)
    async def delete_component(self, uuid: str):
        """
        :param uuid: uuid of the component
        """
        await self._app.delete_report(uuid=uuid)

    @async_auto_call_manager(execute=True)
    @logging_before_and_after(logging_level=logger.info)
    async def get_component_data_set_links(self, uuid: str) -> List[Dict]:
        """
        :param uuid: uuid of the component
        :return: list of data set links
        """
        report: Report = await self._app.get_report(uuid=uuid)
        return [rds.cascade_to_dict() for rds in (await report.get_report_data_sets())]
