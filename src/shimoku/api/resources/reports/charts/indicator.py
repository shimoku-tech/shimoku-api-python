from ...report import Report


class Indicator(Report):
    report_type = "INDICATOR"

    possible_values = dict(
        colors=["success", "warning", "error", "neutral", "caution"],
        align=["left", "center", "right"],
        variant=["default", "outlined", "contained", "topColor"],
    )

    default_properties = dict(
        **Report.default_properties,
        title=None,
        value=None,
        description=None,
        targetPath=None,
        color="neutral",
        align="right",
        variant="default",
        info=None,
        icon=None,
        bigIcon=None,
        hideIcons=False,
        backgroundImage=None,
    )
