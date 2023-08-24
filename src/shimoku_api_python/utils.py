import collections.abc
import json
import json5
import logging
from typing import Tuple, Dict, List, Optional, Union

import numpy as np
import pandas as pd
from pandas import DataFrame

from shimoku_api_python.resources.data_set import convert_input_data_to_db_items
from shimoku_api_python.execution_logger import logging_before_and_after, log_error

logger = logging.getLogger(__name__)


def create_normalized_name(name: str) -> str:
    """Having a name create a normalizedName

    Example
    ----------------------
    # "name": "   Test Borrar_grafico    "
    # "normalizedName": "test-borrar-grafico"
    """
    if any([c not in 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789._- '
            for c in name.encode('ascii', 'ignore').decode()]):
        log_error(logger,
                  f'You can only use letters, numbers, spaces, "-" and "_" in your name | '
                  f'you introduced {name}',
                  ValueError
                  )
    # remove empty spaces at the beginning and end
    name: str = name.strip()
    # replace "_" for www protocol it is not good
    name = name.replace('_', '-')

    return '-'.join(name.split(' ')).lower()


def clean_menu_path(menu_path: str) -> Tuple[str, str]:
    """
    Break the menu path in the apptype or app normalizedName
    and the path normalizedName if any
    :param menu_path: the menu path
    """
    # remove empty spaces
    menu_path: str = menu_path.strip()
    # replace "_" for www protocol it is not good
    menu_path = menu_path.replace('_', '-')

    try:
        assert len(menu_path.split('/')) <= 2  # we allow only one level of path
    except AssertionError:
        raise ValueError(
            f'We only allow one subpath in your request | '
            f'you introduced {menu_path} it should be maximum '
            f'{"/".join(menu_path.split("/")[:1])}'
        )

    # Split AppType or App Normalized Name
    normalized_name: str = menu_path.split('/')[0]
    name: str = (
        ' '.join(normalized_name.split('-'))
    )

    try:
        path_normalized_name: str = menu_path.split('/')[1]
        path_name: str = (
            ' '.join(path_normalized_name.split('-'))
        )
    except IndexError:
        path_name = None

    return name, path_name


@logging_before_and_after(logging_level=logger.debug)
def calculate_percentages_from_list(numbers, round_digits_min):
    """Calculate the proportion of each number in a list
    :param numbers: list of numbers
    :param round_digits_min: minimum number of digits to round
    :return: list of percentages
    """

    def max_precision():
        max_p = 0
        for n in numbers:
            str_n = str(n)
            if '.' in str_n:
                n_precision = len(str_n.split('.')[1])
                max_p = n_precision if n_precision > max_p else max_p
        return max(max_p, round_digits_min)

    if isinstance(numbers, list):
        numbers = np.array(numbers)

    perc = np.round(100 * numbers / np.sum(numbers), max_precision())
    round_max = 99.9
    while np.sum(perc) > 99.99:
        perc = np.round(round_max * numbers / np.sum(numbers), max_precision())
        round_max -= 0.1
    return perc


# From https://stackoverflow.com/questions/3232943/update-value-of-a-nested-dictionary-of-varying-depth
def deep_update(source, overrides) -> Dict:
    """
    Update a nested dictionary or similar mapping.
    Modify ``source`` in place.
    """
    for key, value in overrides.items():
        if isinstance(value, collections.abc.Mapping) and value:
            returned = deep_update(source.get(key, {}), value)
            source[key] = returned
        else:
            source[key] = overrides[key]
    return source


def convert_data_and_get_series_name(data: pd.DataFrame, field: str) -> Tuple[pd.DataFrame, str]:
    """ Convert data to a format that can be used by the API and get the series name of a field.
    :param data: data to convert
    :param field: field to get the series name
    :return: converted data and the converted series name
    """
    converted_data = pd.DataFrame(convert_input_data_to_db_items(data.to_dict(orient='records')))

    converted_data_columns = converted_data.columns.to_list()
    data_columns = data.columns.to_list()
    series_name = converted_data_columns[data_columns.index(field)]

    return converted_data, series_name


@logging_before_and_after(logging_level=logger.debug)
def get_uuids_from_dict(_dict: dict) -> List[str]:
    """ Get all uuids from a dictionary. They follow the pattern '#{'id'}'. """
    uuids = []
    for k, v in _dict.items():
        if isinstance(v, dict):
            uuids.extend(get_uuids_from_dict(v))
        elif isinstance(v, list):
            uuids.extend(get_uuids_from_list(v))
        elif isinstance(v, str) and v.startswith('#{') and v.endswith('}'):
            uuids.append(v[2:-1])
    return uuids


@logging_before_and_after(logging_level=logger.debug)
def get_uuids_from_list(_list: list) -> List[str]:
    """ Get all uuids from a list. They follow the pattern '#{'id'}'. """
    uuids = []
    for v in _list:
        if isinstance(v, dict):
            uuids.extend(get_uuids_from_dict(v))
        elif isinstance(v, list):
            uuids.extend(get_uuids_from_list(v))
        elif isinstance(v, str) and v.startswith('#{') and v.endswith('}'):
            uuids.append(v[2:-1])
    return uuids


@logging_before_and_after(logging_level=logger.debug)
def get_data_references_from_dict(_dict: dict, previous_keys: Optional[List[Union[str, int]]] = None) -> \
        List[List[str]]:
    """ Get all data references from a dictionary. They follow the pattern '#set_data#'. """
    if previous_keys is None:
        previous_keys = []
    entries = []
    for k, v in _dict.items():
        if isinstance(v, dict):
            entries.extend(get_data_references_from_dict(v, previous_keys=previous_keys + [k]))
        elif isinstance(v, list):
            entries.extend(get_data_references_from_list(v, previous_keys=previous_keys + [k]))
        elif v == '#set_data#':
            entries.append(previous_keys + [k])
    return entries


@logging_before_and_after(logging_level=logger.debug)
def get_data_references_from_list(_list: list, previous_keys: Optional[List[Union[int, str]]] = None
                                  ) -> List[List[str]]:
    """ Get all data references from a list. They follow the pattern '#set_data#'. """
    if previous_keys is None:
        previous_keys = []
    entries = []
    for i, v in enumerate(_list):
        if isinstance(v, dict):
            entries.extend(get_data_references_from_dict(v, previous_keys=previous_keys + [i]))
        elif isinstance(v, list):
            entries.extend(get_data_references_from_list(v, previous_keys=previous_keys + [i]))
        elif v == '#set_data#':
            entries.append(previous_keys + [i])
    return entries


@logging_before_and_after(logging_level=logger.debug)
def validate_data_is_pandarable(data: Union[str, DataFrame, List[Dict], Dict]) -> DataFrame:
    """"""
    if isinstance(data, DataFrame):
        df_ = data.copy()
    elif isinstance(data, list):
        try:
            df_ = DataFrame(data)
        except Exception:
            raise ValueError(
                'The data you passed is a list that must be '
                'able to be converted into a pandas dataframe'
            )
    elif isinstance(data, dict):
        try:
            df_ = DataFrame(data)
        except Exception:
            try:
                df_ = DataFrame(data, index=[0])
            except Exception:
                raise ValueError(
                    'The data you passed is a dict that must be '
                    'able to be converted into a pandas dataframe'
                )
    elif isinstance(data, str):
        try:
            d: List[Dict] = json.loads(data)
            df_ = DataFrame(d)
        except Exception:
            raise ValueError(
                'The data you passed is a json that must be '
                'able to be converted into a pandas dataframe'
            )
    else:
        raise ValueError(
            'Input data must be a pandas dataframe, '
            'a json or a list of dictionaries'
        )
    return df_


@logging_before_and_after(logging_level=logger.debug)
def validate_table_data(
        self, data: Union[str, DataFrame, List[Dict], Dict], elements: List[str],
):
    """"""
    df_: DataFrame = self._validate_data_is_pandarable(data)

    cols = df_.columns
    try:
        assert all([element in cols for element in elements])
    except AssertionError:
        raise ValueError(
            'Some column names you are specifying '
            'are not in the input dataframe'
        )

    try:
        len_df_: int = len(df_)
        assert all([
            len_df_ == len(df_[~df_[element].isna()])
            for element in elements
        ])
    except AssertionError:
        raise ValueError(
            f'Some of the variables {elements} have none values'
        )


@logging_before_and_after(logging_level=logger.debug)
def validate_tree_data(
        self, data: Union[str, List[Dict]], vals: List[str],
):
    """To validate Tree and Treemap data"""
    if isinstance(data, list):
        pass
    elif isinstance(data, dict):
        pass
    elif isinstance(data, str):
        data = json.loads(data)
    else:
        raise ValueError('data must be either a list, dict or a json')

    try:
        assert sorted(data.keys()) == sorted(vals)
    except AssertionError:
        raise ValueError('data keys must be "name", "value" and "children"')


@logging_before_and_after(logging_level=logger.debug)
def validate_input_form_data(self, data: Dict):
    try:
        assert type(data) == dict
    except AssertionError:
        raise ValueError('data must be a dict')

    try:
        assert 'fields' in data
    except AssertionError:
        raise ValueError('"fields" is not a key in the input data')

    try:
        assert type(data['fields']) == list
    except AssertionError:
        raise ValueError('fields must be a list')

    try:
        assert all(['fields' in field_ for field_ in data['fields']])
    except AssertionError:
        raise ValueError('"fields" are not keys in the input data')

    try:
        assert all([
            'fieldName' in field__ and 'mapping' in field__
            for field_ in data['fields']
            for field__ in field_['fields']
        ])
    except AssertionError:
        raise ValueError('"fieldName" and "mapping" are not keys in the input data')


@logging_before_and_after(logging_level=logger.debug)
def is_report_data_empty(report_data: Union[List[Dict], str, DataFrame, Dict, List]) -> bool:
    if isinstance(report_data, DataFrame):
        if report_data.empty:
            return True
        else:
            return False
    elif isinstance(report_data, list) or isinstance(report_data, dict):
        if report_data:
            return False
        else:
            return True
    elif isinstance(report_data, str):
        report_data_: List[Dict] = json.loads(report_data)
        if report_data_:
            return False
        else:
            return True
    else:
        raise ValueError(
            f'Data must be a Dictionary, JSON or pandas DataFrame '
            f'Provided: {type(report_data)}'
        )


@logging_before_and_after(logging_level=logger.debug)
def add_sorting_to_df(df: DataFrame, sort: Optional[Dict] = None) -> Tuple[DataFrame, Dict]:
    """ Add sorting to the data frame. If no sorting is provided the a column named 'sort_values' is added.
    :param df: the data frame
    :param sort: the sorting
    :return: the data frame with sorting and the sorting
    """
    if 'sort_values' not in df.columns:
        df['sort_values'] = range(len(df))
    sort = {'field': 'sort_values', 'direction': 'asc'} if not sort else sort
    df = df[[col for col in df.columns.tolist() if col != 'sort_values'] + ['sort_values']]
    return df, sort


@logging_before_and_after(logging_level=logger.debug)
def interpret_color(color_def: Union[List, str, int]) -> Union[str, Dict]:
    def rbg_to_hex(r: int, g: int, b: int) -> str:
        def clamp(x: int) -> int:
            return max(0, min(x, 255))

        # from https://stackoverflow.com/questions/3380726/converting-an-rgb-color-tuple-to-a-hexidecimal-string
        return "#{0:02x}{1:02x}{2:02x}".format(clamp(r), clamp(g), clamp(b))

    # from https://xkcd.com/color/rgb/
    color_defs = {
        "purple": "#7e1e9c",
        "red": "#e50000",
        "green": "#15b01a",
        "blue": "#0343df",
        "pink": "#ff81c0",
        "brown": "#653700",
        "orange": "#f97306",
        "yellow": "#ffff14",
        "gray": "#929591",
        "violet": "#9a0eea",
        "cyan": "#00ffff",
        "success": "var(--color-success)",
        "success-light": "var(--color-success-light)",
        "warning": "var(--color-warning)",
        "warning-light": "var(--color-warning-light)",
        "error": "var(--color-error)",
        "error-light": "var(--color-error-light)",
        "status-error": "var(--color-status-error)",
        "white": "var(--color-white)",
        "black": "var(--color-black)",
        "base-icon": "var(--color-base-icon)",
        "background": "var(--background-default)",
        "background-paper": "var(--background-paper)",
        "primary": "var(--color-primary)",
        "primary-light": "var(--color-primary-light)",
        "primary-dark": "var(--color-primary-dark)",
        "main": "var(--chart-C1)",
        "secondary": "var(--color-secondary)",
        "secondary-light": "var(--color-secondary-light)",
        "secondary-dark": "var(--color-secondary-dark)",
        "active": "var(--chart-C2)",
        "caution": "var(--chart-C3)",

    }

    if isinstance(color_def, int):
        return f'var(--chart-C{abs(color_def)})'
    elif isinstance(color_def, list):
        color_def = rbg_to_hex(color_def[0], color_def[1], color_def[2])
    elif color_def in color_defs:
        color_def = color_defs[color_def]

    return color_def


@logging_before_and_after(logging_level=logger.debug)
def transform_dict_js_to_py(options_str: str):
    """https://discuss.dizzycoding.com/how-to-convert-raw-javascript-object-to-python-dictionary/"""
    options_str = options_str.replace('\n', '')
    options_str = options_str.replace(';', '')
    return json5.loads(options_str)


@logging_before_and_after(logging_level=logger.debug)
def retrieve_data_from_options(options: Dict) -> Union[Dict, List]:
    """Retrieve data from eCharts options

    Example
    -----------
    input options = {'title': {'text': 'Stacked Area Chart'},
         'tooltip': {'trigger': 'axis',
          'axisPointer': {'type': 'cross', 'label': {'backgroundColor': '#6a7985'}}},
         'legend': {'data': ['Email',
           'Union Ads',
           'Video Ads',
           'Direct',
           'Search Engine']},
         'toolbox': {'feature': {'saveAsImage': {}}},
         'grid': {'left': '3%', 'right': '4%', 'bottom': '3%', 'containLabel': True},
         'xAxis': [{'type': 'category',
           'boundaryGap': False,
           'data': ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']}],
         'yAxis': [{'type': 'value'}],
         'series': [{'name': 'Email',
           'type': 'line',
           'stack': 'Total',
           'areaStyle': {},
           'emphasis': {'focus': 'series'},
           'data': [120, 132, 101, 134, 90, 230, 210]},
          {'name': 'Union Ads',
           'type': 'line',
           'stack': 'Total',
           'areaStyle': {},
           'emphasis': {'focus': 'series'},
           'data': [220, 182, 191, 234, 290, 330, 310]},
          {'name': 'Video Ads',
           'type': 'line',
           'stack': 'Total',
           'areaStyle': {},
           'emphasis': {'focus': 'series'},
           'data': [150, 232, 201, 154, 190, 330, 410]},
          {'name': 'Direct',
           'type': 'line',
           'stack': 'Total',
           'areaStyle': {},
           'emphasis': {'focus': 'series'},
           'data': [320, 332, 301, 334, 390, 330, 320]},
          {'name': 'Search Engine',
           'type': 'line',
           'stack': 'Total',
           'label': {'show': True, 'position': 'top'},
           'areaStyle': {},
           'emphasis': {'focus': 'series'},
           'data': [820, 932, 901, 934, 1290, 1330, 1320]}]
        }

    output
        [{'Mon': 120,
          'Tue': 132,
          'Wed': 101,
          'Thu': 134,
          'Fri': 90,
          'Sat': 230,
          'Sun': 210},
         {'Mon': 220,
          'Tue': 182,
          'Wed': 191,
          'Thu': 234,
          'Fri': 290,
          'Sat': 330,
          'Sun': 310},
         {'Mon': 150,
          'Tue': 232,
          'Wed': 201,
          'Thu': 154,
          'Fri': 190,
          'Sat': 330,
          'Sun': 410},
         {'Mon': 320,
          'Tue': 332,
          'Wed': 301,
          'Thu': 334,
          'Fri': 390,
          'Sat': 330,
          'Sun': 320},
         {'Mon': 820,
          'Tue': 932,
          'Wed': 901,
          'Thu': 934,
          'Fri': 1290,
          'Sat': 1330,
          'Sun': 1320
        }
    ]
    """
    rows = []
    data = []
    cols = []
    if 'xAxis' in options:
        if type(options['xAxis']) == list:
            if len(options['xAxis']) == 1:
                if 'data' in options['xAxis'][0]:
                    rows = options['xAxis'][0]['data']
        elif type(options['xAxis']) == dict:
            if 'data' in options['xAxis']:
                rows = options['xAxis']['data']
            elif type(options['xAxis']) == dict:
                if 'data' in options['yAxis']:
                    rows = options['yAxis']['data']
        else:
            raise ValueError('xAxis has multiple values only 1 allowed')
    elif 'radar' in options:
        if 'indicator' in options['radar']:
            rows = [element['name'] for element in options['radar']['indicator']]
        elif type(options['radar']) == dict:
            raise NotImplementedError('Multi-radar not implemented')

    if 'data' in options:
        data = options['data']
    if 'series' in options:
        if 'data' in options['series']:
            pass
        else:
            for serie in options['series']:
                if 'data' in serie:
                    if serie.get('type') in ['pie', 'gauge']:
                        for datum in serie['data']:
                            data.append(datum)
                    elif serie.get('type') == 'radar':
                        for datum in serie['data']:
                            data.append(datum['value'])
                            cols.append(datum['name'])
                        break
                    else:
                        data.append(serie['data'])

                if 'name' in serie:
                    cols.append(serie['name'])
                elif 'type' in serie:
                    cols.append(serie['type'])
    else:
        return {}

    df = DataFrame(data)
    if not rows and not cols:
        return df.reset_index().to_dict(orient='records')
    if not rows:
        return df.to_dict(orient='records')

    if rows:
        df.columns = rows
    df_ = df.T
    df_.columns = cols
    return df_.reset_index().to_dict(orient='records')


@logging_before_and_after(logging_level=logger.debug)
def validate_input_form_data(data: Dict):
    try:
        assert type(data) == dict
    except AssertionError:
        raise ValueError('data must be a dict')

    try:
        assert 'fields' in data
    except AssertionError:
        raise ValueError('"fields" is not a key in the input data')

    try:
        assert type(data['fields']) == list
    except AssertionError:
        raise ValueError('fields must be a list')

    try:
        assert all(['fields' in field_ for field_ in data['fields']])
    except AssertionError:
        raise ValueError('"fields" are not keys in the input data')

    try:
        assert all([
            'fieldName' in field__ and 'mapping' in field__
            for field_ in data['fields']
            for field__ in field_['fields']
        ])
    except AssertionError:
        raise ValueError('"fieldName" and "mapping" are not keys in the input data')
