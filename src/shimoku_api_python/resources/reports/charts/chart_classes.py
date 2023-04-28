from ...report import Report

import logging
logger = logging.getLogger(__name__)


class HTML(Report):
    report_type = 'HTML'


class Form(Report):
    report_type = 'FORM'


class Button(Report):
    report_type = 'BUTTON'


class AnnotatedEChart(Report):
    report_type = 'ANNOTATED_ECHART'
