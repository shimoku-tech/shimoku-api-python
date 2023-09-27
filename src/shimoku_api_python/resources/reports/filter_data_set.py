from ..report import Report
import logging
from enum import Enum
logger = logging.getLogger(__name__)


class FilterDataSet(Report):
    """ Filter data set report class """

    report_type = 'FILTERDATASET'

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
