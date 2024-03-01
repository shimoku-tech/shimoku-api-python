from ..report import Report
from enum import Enum


class FilterDataSet(Report):
    """Filter data set report class"""

    report_type = "FILTERDATASET"

    default_properties = dict(
        **Report.default_properties,
        filter=[],
        mapping=[],
    )

    class InputType(Enum):
        DATERANGE = "DATERANGE"
        NUMERIC = "NUMERIC"
        CATEGORICAL_SINGLE = "CATEGORICAL_SINGLE"
        CATEGORICAL_MULTI = "CATEGORICAL_MULTI"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
