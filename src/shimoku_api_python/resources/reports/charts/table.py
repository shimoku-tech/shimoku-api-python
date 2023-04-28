from ...report import Report

import logging
logger = logging.getLogger(__name__)


class Table(Report):
    report_type = 'TABLE'
