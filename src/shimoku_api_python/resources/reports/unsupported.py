from ..report import Report


class Unsupported(Report):
    """ ECharts report class """
    report_type = 'UNSUPPORTED'

    default_properties = dict(
        hash=None,
    )