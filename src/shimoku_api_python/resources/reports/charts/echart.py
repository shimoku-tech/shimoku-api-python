from ...report import Report
from copy import deepcopy
from typing import Dict, Any, List, Optional, Union
from abc import ABC, abstractmethod

from shimoku_api_python.utils import ShimokuPalette, get_default_args

import logging
from shimoku_api_python.execution_logger import log_error
logger = logging.getLogger(__name__)


class EChart(Report):
    """ ECharts report class """
    report_type = 'ECHARTS2'

    default_properties = dict(
        **Report.default_properties,
        option={},
    )


default_toolbox_options = {
    'show': True,
    'orient': 'horizontal',
    'itemSize': 20,
    'itemGap': 24,
    'showTitle': True,
    'zlevel': 100,
    'bottom': 0,
    'right': '24px',
    'feature': {
        'dataView': {
            'title': 'data',
            'readOnly': False,
            'icon': 'image://https://uploads-ssl.webflow.com/619f9fe98661d321dc3beec7/6398a555461a3684b16d544e_database.svg',
            'emphasis': {
                'iconStyle': {
                    'textBackgroundColor': ShimokuPalette.CHART_C1.value,
                    'textBorderRadius': [50, 50, 50, 50],
                    'textPadding': [8, 8, 8, 8],
                    'textFill': ShimokuPalette.WHITE.value
                }
            },
        },
        'magicType': {
            'type': ['line', 'bar'],
            'title': {
                'line': 'Switch to Line Chart',
                'bar': 'Switch to Bar Chart',
            },
            'icon': {
                'line': 'image://https://uploads-ssl.webflow.com/619f9fe98661d321dc3beec7/6398a55564d52c1ba4d9884d_linechart.svg',
                'bar': 'image://https://uploads-ssl.webflow.com/619f9fe98661d321dc3beec7/6398a5553cc6580f8e0edea4_barchart.svg'
            },
            'emphasis': {
                'iconStyle': {
                    'textBackgroundColor': ShimokuPalette.CHART_C1.value,
                    'textBorderRadius': [50, 50, 50, 50],
                    'textPadding': [8, 8, 8, 8],
                    'textFill': ShimokuPalette.WHITE.value
                }
            },
        },
        'saveAsImage': {
            'show': True,
            'title': 'Save as image',
            'icon': 'image://https://uploads-ssl.webflow.com/619f9fe98661d321dc3beec7/6398a555662e1af339154c64_download.svg',
            'emphasis': {
                'iconStyle': {
                    'textBackgroundColor': ShimokuPalette.CHART_C1.value,
                    'textBorderRadius': [50, 50, 50, 50],
                    'textPadding': [8, 8, 8, 8],
                    'textFill': ShimokuPalette.WHITE.value
                }
            }
        }
    }
}


def get_common_series_options() -> Dict[str, Any]:
    return deepcopy({
        'data': '#set_data#',
        'emphasis': {'focus': 'series'},
        'smooth': True,
        'itemStyle': {'borderRadius': [9, 9, 0, 0]},
    })


def get_common_echart_options() -> Dict[str, Any]:
    # toolbox_options = deepcopy(default_toolbox_options)
    # if bottom_toolbox:
    #     del toolbox_options['top']
    #     toolbox_options['bottom'] = "0px"
    return deepcopy({
        'legend': {
            'show': True,
            'type': 'scroll',
            'icon': 'circle',
            'padding': [5, 5, 5, 5],
        },
        'tooltip': {
            'trigger': 'item',
            'axisPointer': {'type': 'cross'},
        },
        'toolbox': default_toolbox_options,
        'xAxis': [{
            'data': '#set_data#',
            'type': 'category',
            'fontFamily': 'Rubik',
            'name': "",
            'nameLocation': 'middle',
        }],
        'yAxis': [{
            'name': "",
            'nameLocation': 'middle',
            'type': 'value',
            'fontFamily': 'Rubik',
        }],
        'grid': {
            'left': '1%',
            'right': '2%',
            'bottom': 48,
            'containLabel': True
        },
        'series': [get_common_series_options()],
    })


generic_echart_function_params = dict(
    fields='fields', options='options', data='data', option_modifications='option_modifications',
    order='order', title='title', rows_size='rows_size', cols_size='cols_size', padding='padding'
)


class InvertibleOperation(ABC):
    @abstractmethod
    def __call__(self, *args, **kwargs):
        pass

    @abstractmethod
    def revert(self, *args, **kwargs):
        pass


class InvertibleDictFunction(ABC):

    def __init__(
        self, echarts_func: callable, dict_var_name: str = 'options',
        diff_dict_var_name: str = 'option_modifications'
    ):
        self.function_operations = []
        self.params = get_default_args(echarts_func)
        self.params.pop('self')
        self.params[dict_var_name] = {}
        self.params[diff_dict_var_name] = {}
        self.d = self.params[dict_var_name]
        self.diff_dict = self.params[diff_dict_var_name]
        self.dict_var_name = dict_var_name
        self.diff_dict_var_name = diff_dict_var_name
        self.aux_definition_params = deepcopy(self.params)

    class SetItems(InvertibleOperation):

        def __init__(
            self, idf: 'InvertibleDictFunction',
            items: dict, offset: Optional[list[Union[str, int]]] = None,
            final: bool = False,
        ):
            self.d = idf.d
            self.items = deepcopy(items)
            self.previous_items = {}
            self.offset = offset if offset else []
            self.final = final
            self.diff_dict = idf.diff_dict
            self(idf.aux_definition_params[idf.dict_var_name])

        def __call__(self, d: Optional[dict] = None):
            in_definition = d is not None
            d = self.d if d is None else d
            for offset_key in self.offset:
                d = d[offset_key]
            if in_definition:
                self.previous_items = deepcopy(d)
            d.update(deepcopy(self.items))

        def revert(self) -> bool:
            d = self.d
            aux_diff = deepcopy(self.diff_dict)
            for offset_key in self.offset:
                if isinstance(d, list):
                    if offset_key not in aux_diff:
                        aux_diff = [{} for _ in range(offset_key + 1)]
                    if not isinstance(offset_key, int) or offset_key >= len(d):
                        return False
                elif offset_key not in d:
                    return False
                elif offset_key not in aux_diff:
                    aux_diff[offset_key] = {}
                d = d[offset_key]
                aux_diff = aux_diff[offset_key]

            exists_diff = False
            for k in d.keys():
                if k not in self.previous_items and k not in self.items:
                    if self.final:
                        return False
                    aux_diff[k] = d[k]
                    exists_diff = True

            for k in self.items.keys():
                if d[k] != self.items[k]:
                    if self.final:
                        return False
                    aux_diff[k] = d[k]
                    exists_diff = True
                if k in self.previous_items:
                    d[k] = self.previous_items[k]
                else:
                    del d[k]
            if exists_diff:
                self.diff_dict.clear()
                self.diff_dict.update(aux_diff)
            return True

    def set_items(
        self, items: dict, offset: Optional[list[Union[str, int]]] = None, final: bool = False
    ):
        self.function_operations.append(self.SetItems(self, items, offset, final))

    class DeleteItems(InvertibleOperation):
        def __init__(
            self, idf: 'InvertibleDictFunction',
            keys: List[str], offset: Optional[list[Union[str, int]]] = None
        ):
            self.d = idf.d
            self.keys = keys
            self.previous_items = {}
            self.offset = offset if offset else []
            self(idf.aux_definition_params[idf.dict_var_name])

        def __call__(self, d: Optional[dict] = None):
            in_definition = d is not None
            d = self.d if d is None else d
            for offset_key in self.offset:
                d = d[offset_key]
            for k in self.keys:
                if in_definition and k in d:
                    self.previous_items[k] = d[k]
                del d[k]

        def revert(self) -> bool:
            d = self.d
            for offset_key in self.offset:
                if isinstance(d, list):
                    if not isinstance(offset_key, int) or offset_key >= len(d):
                        return False
                elif offset_key not in d:
                    return False
                d = d[offset_key]
            for k in self.keys:
                if k in self.previous_items:
                    d[k] = self.previous_items[k]
                else:
                    d[k] = None
            return True

    def delete_items(self, keys: List[str], offset: Optional[list[Union[str, int]]] = None):
        self.function_operations.append(self.DeleteItems(self, keys, offset=offset))

    # TODO: Fix conditional branch
    class ConditionalBranch(InvertibleOperation):

        def __init__(
                self,
                idf: 'InvertibleDictFunction',
                condition: Any,
                condition_options: List[Any],
                branches: List[Union['InvertibleDictFunction', 'InvertibleOperation']],
                else_branch: Optional[Union['InvertibleDictFunction', 'InvertibleOperation']] = None
        ):
            self.d = idf.d
            self.params = idf.params
            self.condition = condition
            self.condition_options = condition_options
            self.branches = branches
            if else_branch is not None:
                self.branches.append(else_branch)
                condition_options.append(None)

        def __call__(self):
            for condition_option, branch in zip(self.condition_options, self.branches):
                if self.params[self.condition] == condition_option:
                    branch()
                    return

        def revert(self) -> bool:
            d = self.d
            for condition_option, branch in zip(self.condition_options, self.branches):
                aux_d = deepcopy(d)
                if branch.revert(aux_d):
                    d.clear()
                    d.update(aux_d)
                    self.params[self.condition] = condition_option
                    return True
            return False

    def conditional_branch(
        self, condition: Any, condition_options: List[Any],
        branches: List[Union['InvertibleDictFunction', 'InvertibleOperation']],
        else_branch: Optional[Union['InvertibleDictFunction', 'InvertibleOperation']] = None
    ):
        self.function_operations.append(self.ConditionalBranch(
            self, condition, condition_options, branches, else_branch
        ))

    class SetFromParams(InvertibleOperation):
        def __init__(
            self, idf: 'InvertibleDictFunction',
            offset: list[Union[str, int]],
            key: str, value: Any
        ):
            self.d = idf.d
            self.offset = offset
            self.params = idf.params
            self.key = key
            self.value = value
            self(idf.aux_definition_params[idf.dict_var_name])

        def __call__(self, d: Optional[dict] = None):
            d = self.d if d is None else d
            for offset_key in self.offset:
                d = d[offset_key]
            d[self.key] = self.value

        def revert(self) -> bool:
            d = self.d
            for offset_key in self.offset:
                if offset_key not in d:
                    return False
                d = d[offset_key]
            if self.key not in d:
                return False
            self.params[self.key] = d[self.key]
            del d[self.key]
            return True

    def set_from_params(self, offset: list[Union[str, int]], key: str, value: Any):
        self.function_operations.append(self.SetFromParams(self, offset, key, value))

    class ParamsToParams(InvertibleOperation):
        def __init__(
            self, idf: 'InvertibleDictFunction',
            keys_dict: dict,
            replace: bool = False
        ):
            self.params = idf.params
            self.keys_dict = keys_dict
            self.previous_dict = deepcopy(idf.aux_definition_params)
            self.replace = replace
            self(idf.aux_definition_params)

        def __call__(self, params: Optional[dict] = None):
            if not params:
                params = self.params
            result = {new_key: params[old_key] for new_key, old_key in self.keys_dict.items()}
            if self.replace:
                params.clear()
            params.update(result)

        def revert(self) -> bool:
            result = deepcopy(self.previous_dict)
            for new_key, old_key in self.keys_dict.items():
                if new_key not in self.params:
                    return False
                result[old_key] = self.params[new_key]
            self.params.clear()
            self.params.update(result)
            return True

    def params_to_params(self, keys_dict: dict, replace: bool = False):
        self.function_operations.append(self.ParamsToParams(self, keys_dict, replace))

    class CustomOperation(InvertibleOperation):
        def __init__(
            self, idf: 'InvertibleDictFunction',
            func: callable, inverse_func: callable
        ):
            self.params = idf.params
            self.func = func
            self.inverse_func = inverse_func
            self(idf.aux_definition_params)

        def __call__(self, params: Optional[dict] = None):
            self.func(params if params else self.params)

        def revert(self) -> bool:
            return self.inverse_func(self.params)

    def custom_operation(self, func: callable, inverse_func: callable):
        self.function_operations.append(self.CustomOperation(self, func, inverse_func))

    def add_operations(self, operations: list[InvertibleOperation]):
        for operation in operations:
            self.function_operations.append(operation)

    def __call__(self, **initial_params) -> dict:
        for k, v in initial_params.items():
            if v is None:
                continue
            if k not in self.params:
                log_error(logger, f'Parameter {k} not found in', RuntimeError)
            elif k in [self.dict_var_name, self.diff_dict_var_name]:
                self.params[k].update(deepcopy(initial_params[k]))
            else:
                self.params[k] = initial_params[k]
        for operation in self.function_operations:
            operation()
        return self.params

    def revert(self, **ending_params) -> Optional[dict]:
        for k, v in ending_params.items():
            if k not in self.aux_definition_params:
                log_error(logger, f'Parameter {k} not found in the end execution params', RuntimeError)
            elif k in [self.dict_var_name, self.diff_dict_var_name]:
                self.params[k].update(deepcopy(ending_params[k]))
            else:
                self.params[k] = ending_params[k]
        for operation in reversed(self.function_operations):
            if not operation.revert():
                return None
        return self.params
