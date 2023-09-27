from typing import List
from ..report import Report

import asyncio
import logging
from ...execution_logger import logging_before_and_after
logger = logging.getLogger(__name__)


class TabsGroup(Report):
    """ Tabs group report class """

    report_type = 'TABS'

    default_properties = dict(
        **Report.default_properties,
        tabs=dict(),
        sticky=False,
        variant='enclosedSolidRounded',
    )

    def __init__(self, *args, **kwargs):
        self.dirty = False
        super().__init__(*args, **kwargs)

    @logging_before_and_after(logger.debug)
    async def update(self, *args, **kwargs) -> bool:
        """ Update the tabs group on the server
        :return: True if the tabs group was updated, False otherwise
        """
        if not self.dirty:
            return False
        self.dirty = False
        await super().update()
        return True

    @logging_before_and_after(logger.debug)
    async def delete(self):
        """ Delete the tabs group from the server and all its children """
        delete_tasks = []
        for tab_dict in self['properties']['tabs'].values():
            for rd_id in tab_dict['reportIds']:
                delete_tasks.append(self._base_resource.parent.delete_component(rd_id))
        await asyncio.gather(*delete_tasks)
        await super().delete()

    @logging_before_and_after(logger.debug)
    def add_tab(self, tab: str):
        """ Add tab to the tabs group without saving it to the server
        :param tab: tab name
        """
        if tab in self['properties']['tabs']:
            return
        self['properties']['tabs'][tab] = {'order': len(self['properties']['tabs']), 'reportIds': []}
        self.dirty = True

    @logging_before_and_after(logger.debug)
    def add_report(self, tab: str, report: Report):
        """ Add report to the tabs group without saving it to the server
        :param tab: tab name
        :param report: report to add
        """
        self.add_tab(tab)

        if report['id'] in self['properties']['tabs'][tab]['reportIds']:
            logger.warning(f"Report {report['id']} already in tab {tab}")
            return

        self['properties']['tabs'][tab]['reportIds'].append(report['id'])
        self.dirty = True

    @logging_before_and_after(logger.debug)
    def remove_report(self, tab: str, report: Report):
        """ Remove report from the tabs group without saving it to the server
        :param tab: tab name
        :param report: report to remove
        """

        if tab not in self['properties']['tabs']:
            logger.warning(f"Tab {tab} not found")
            return

        if report['id'] not in self['properties']['tabs'][tab]['reportIds']:
            logger.warning(f"Report {report['id']} not in tab {tab}")
            return

        self['properties']['tabs'][tab]['reportIds'].remove(report['id'])
        self.dirty = True

    @logging_before_and_after(logger.debug)
    def change_tabs_order(self, tabs: List[str]):
        """ Change tabs order without saving it to the server
        :param tabs: list of tabs in the new order
        """
        all_tabs = list(self['properties']['tabs'].keys())

        for i, tab in enumerate(tabs):
            if tab not in self['properties']['tabs']:
                logger.warning(f"Tab {tab} not found")
                continue
            all_tabs.remove(tab)
            self['properties']['tabs'][tab]['order'] = i

        for i, tab in enumerate(all_tabs):
            self['properties']['tabs'][tab]['order'] = i + len(tabs)
        self.dirty = True

    @logging_before_and_after(logger.debug)
    def has_report(self, report: Report):
        """ Check if report is in the tabs group
        :param report: report to check
        """
        for tab in self['properties']['tabs'].values():
            if report['id'] in tab['reportIds']:
                return True
        return False

    @logging_before_and_after(logger.debug)
    def clear_content(self):
        """ Remove all reports from the tabs group without saving it to the server """
        self['properties']['tabs'] = dict()
        self.dirty = True

