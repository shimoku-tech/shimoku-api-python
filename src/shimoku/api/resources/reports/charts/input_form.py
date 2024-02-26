from ...report import Report


class InputForm(Report):
    report_type = "FORM"

    default_properties = dict(
        **Report.default_properties,
        events={},
    )
