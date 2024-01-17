import datetime as dt
import pandas as pd

from ...report import Report
from typing import Union, List, Dict
from shimoku_api_python.utils import interpret_color
import logging
logger = logging.getLogger(__name__)


class Table(Report):
    report_type = 'TABLE'

    default_properties = dict(
        **Report.default_properties,
        columns=[],
        rows={},
        sort={},
        pagination={},
        columnsButton=False,
        filtersButton=False,
        exportButton=False,
        search=False,
    )


def interpret_label_map(values: list[str], label_map: Union[str, List, tuple], variant: str):
    options = []
    color_def = interpret_color(label_map)
    for val in values:
        if isinstance(val, float) and int(val) - val == 0:
            val = int(val)
        if not isinstance(val, str) and not isinstance(val, int) and not isinstance(val, dt.datetime):
            val = float(val)
        label_options = {'value': val, 'backgroundColor': color_def}
        if variant == 'outlined':
            label_options['color'] = color_def
        elif color_def.startswith('#'):
            label_options['color'] = '#000000' if (int(color_def[1:3], 16) * 0.299 +
                                                   int(color_def[3:5], 16) * 0.587 +
                                                   int(color_def[5:7], 16) * 0.114) > 186 else '#ffffff'
        options.append(label_options)
    return options


def interpret_label_info(df: pd.DataFrame, col: str, labels_map, variant: str):
    options = []
    if isinstance(labels_map, Dict):
        for value, color_def in labels_map.items():
            df_values = [value]
            if isinstance(value, tuple):
                df_values = df[df[col].between(value[0], value[1])][col].unique()
            for label_value in interpret_label_map(df_values, color_def, variant):
                if label_value['value'] not in [option['value'] for option in options]:
                    options.append(label_value)

    elif isinstance(labels_map, (str, list, tuple)):
        options = interpret_label_map(df[col].unique(), labels_map, variant)

    else:
        raise ValueError("Can't interpret label information")

    return options
