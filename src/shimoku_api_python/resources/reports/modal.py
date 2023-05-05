from typing import TYPE_CHECKING
from ..report import Report

import logging
from ...execution_logger import logging_before_and_after
logger = logging.getLogger(__name__)

if TYPE_CHECKING:
    pass


class Modal(Report):
    """ Modal report class """

    report_type = 'MODAL'

    default_properties = dict(
        name=None,
        open=False,
        reportIds=[],
        width=60,
        height=50,
    )

    @logging_before_and_after(logger.debug)
    def add_report(self, report: Report):
        """ Add report to the modal without saving it to the server
        :param report: report to add
        """

        if report['id'] in self['properties']['reportIds']:
            logger.warning(f"Report {report['id']} already in modal")

        self['properties']['reportIds'].append(report['id'])

    @logging_before_and_after(logger.debug)
    def remove_report(self, report: Report):
        """ Remove report from the modal without saving it to the server
        :param report: report to remove
        """

        if report['id'] not in self['properties']['reportIds']:
            logger.warning(f"Report {report['id']} not in modal")
            return

        self['properties']['reportIds'].remove(report['id'])

