from ...report import Report


class AnnotatedEChart(Report):
    report_type = 'ANNOTATED_ECHART'

    default_properties = dict(
        **Report.default_properties,
        option={},
        slider={},
    )

