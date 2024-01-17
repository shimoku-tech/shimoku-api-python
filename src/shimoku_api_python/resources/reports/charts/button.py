from ...report import Report

import logging
logger = logging.getLogger(__name__)


class Button(Report):
    report_type = 'BUTTON'

    default_properties = dict(
        **Report.default_properties,
        text='More Info',
        align='stretch',
        events={}
    )
