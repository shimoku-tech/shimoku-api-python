from shimoku_api_python.resources.report import Report

import logging
logger = logging.getLogger(__name__)


class IFrame(Report):
    report_type = 'IFRAME'

    default_properties = dict(
        hash=None,
    )
