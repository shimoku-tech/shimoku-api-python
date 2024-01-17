from shimoku_api_python.resources.report import Report

import logging
logger = logging.getLogger(__name__)


class HTML(Report):
    report_type = 'HTML'
