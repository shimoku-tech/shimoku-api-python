from ...report import Report


class Button(Report):
    report_type = "BUTTON"

    default_properties = dict(
        **Report.default_properties, text="More Info", align="stretch", events={}
    )
