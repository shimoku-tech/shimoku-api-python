from typing import Optional

import logging
from shimoku.execution_logger import ClassWithLogging
from shimoku.api.resources.app import App
from shimoku.api.resources.report import Report

logger = logging.getLogger(__name__)


class ComponentsLayer(ClassWithLogging):
    """
    This class is used to interact with the API at the component level.
    """

    _module_logger = logger
    _use_info_logging = True

    def __init__(self, app: Optional[App]):
        self._app = app

    async def get_components_in_sub_path(self, path: str) -> list[dict]:
        """
        :param path: path to the components
        :return: list of components
        """
        return [
            report.cascade_to_dict()
            for report in (await self._app.get_reports())
            if report["path"] == path
        ]

    async def get_component(self, uuid: str) -> dict:
        """
        :param uuid: uuid of the component
        :return: component
        """
        return (await self._app.get_report(uuid=uuid)).cascade_to_dict()

    async def delete_component(self, uuid: str):
        """
        :param uuid: uuid of the component
        """
        await self._app.delete_report(uuid=uuid)

    async def get_component_data_set_links(self, uuid: str) -> list[dict]:
        """
        :param uuid: uuid of the component
        :return: list of data set links
        """
        report: Report = await self._app.get_report(uuid=uuid)
        return [rds.cascade_to_dict() for rds in (await report.get_report_data_sets())]
