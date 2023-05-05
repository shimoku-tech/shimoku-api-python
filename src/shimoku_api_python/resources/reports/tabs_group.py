from typing import List, TYPE_CHECKING
from ..report import Report

import logging
from ...execution_logger import logging_before_and_after
logger = logging.getLogger(__name__)

if TYPE_CHECKING:
    pass


class TabsGroup(Report):
    """ Tabs group report class """

    report_type = 'TABS'

    default_properties = dict(
        tabs=dict(),
        groupName=None,
        sticky=False,
        variant='enclosedSolidRounded',
    )

    @logging_before_and_after(logger.debug)
    def add_report(self, tab: str, report: Report):
        """ Add report to the tabs group without saving it to the server
        :param tab: tab name
        :param report: report to add
        """

        if tab not in self['properties']['tabs']:
            self['properties']['tabs'][tab] = {'order': len(self['properties']['tabs']), 'reportIds': []}

        if report['id'] in self['properties']['tabs'][tab]['reportIds']:
            logger.warning(f"Report {report['id']} already in tab {tab}")

        self['properties']['tabs'][tab]['reportIds'].append(report['id'])

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

