from shimoku_api_python.resources.report import Report

import logging
logger = logging.getLogger(__name__)


class InputForm(Report):
    report_type = 'FORM'

    default_properties = dict(
        **Report.default_properties,
        events={},
    )
