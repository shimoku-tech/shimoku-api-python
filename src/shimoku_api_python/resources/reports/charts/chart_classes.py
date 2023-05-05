from ...report import Report

import logging
logger = logging.getLogger(__name__)


class Barchart(Report):
    report_type = 'BARCHART'


class Linechart(Report):
    report_type = 'LINECHART'


class StockLineChart(Report):
    report_type = 'STOCKLINECHART'


class HTML(Report):
    report_type = 'HTML'


class IFrame(Report):
    report_type = 'IFRAME'


class ECharts(Report):
    report_type = 'ECHARTS2'


class Form(Report):
    report_type = 'FORM'


class Button(Report):
    report_type = 'BUTTON'


class AnnotatedEChart(Report):
    report_type = 'ANNOTATED_ECHART'
