from ...report import Report


class EChart(Report):
    """ECharts report class"""

    report_type = "ECHARTS2"

    default_properties = dict(
        hash=None,
        option={},
    )
