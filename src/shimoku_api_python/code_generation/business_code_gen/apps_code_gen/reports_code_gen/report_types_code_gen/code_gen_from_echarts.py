from typing import TYPE_CHECKING, List
from copy import deepcopy
from shimoku_api_python.utils import revert_uuids_from_dict, change_data_set_name_with_report
from ...data_sets_code_gen.code_gen_from_data_sets import code_gen_read_csv_from_data_set, get_linked_data_set_info
from shimoku_api_python.code_generation.utils_code_gen import code_gen_from_dict, code_gen_from_list
if TYPE_CHECKING:
    from ...code_gen_from_apps import AppCodeGen
    from shimoku_api_python.resources.report import Report

import logging
from shimoku_api_python.execution_logger import log_error

logger = logging.getLogger(__name__)


def get_fields_from_mapping(rev_columns, mappings, data_is_custom):
    if data_is_custom:
        return ['data']
    fields = []
    for _, mapping in mappings:
        if isinstance(mapping, dict):
            entry = {}
            for k, v in mapping.items():
                entry[k] = rev_columns[v] if v in rev_columns else v
            fields.append(entry)
        elif isinstance(mapping, list):
            entry = []
            for v in mapping:
                entry.append(rev_columns[v] if v in rev_columns else v)
            fields.append(entry)
        elif mapping in rev_columns:
            fields.append(rev_columns[mapping])
        else:
            fields.append(mapping)
    return fields


async def code_gen_data_arg(self: 'AppCodeGen', report, data_set_id, data_set, data_is_custom):
    data_arg_code_lines = ['[{}],']

    if data_set_id in self._code_gen_tree.shared_data_sets:
        data_arg_code_lines = [f'    "{data_set["name"]}",']
        if data_is_custom:
            data_arg_code_lines += ['    data_is_not_df=True,']
    elif data_is_custom:
        val = self._code_gen_tree.custom_data_sets_with_data[data_set_id]
        data_arg_code_lines = code_gen_from_dict(val, 4) \
            if isinstance(val, dict) else code_gen_from_list(val, 4)
        data_arg_code_lines += ['    data_is_not_df=True,']
    elif data_set is not None:
        data_arg_code_lines = [
            '    '+(await code_gen_read_csv_from_data_set(
                data_set, change_data_set_name_with_report(data_set, report)
            ))
        ]
        if data_arg_code_lines[0] is None:
            return ['pass']
        data_arg_code_lines[0] += ','

    return data_arg_code_lines


async def code_gen_from_echarts(
        self: 'AppCodeGen', report: 'Report', properties: dict
) -> List[str]:
    """ Generate code for an echarts report.
    :param report: report to generate code from
    :param report_params: parameters of the report
    :param properties: properties of the report
    :return: list of code lines
    """
    echart_options = deepcopy(properties['option'])
    rds_ids_in_order = revert_uuids_from_dict(echart_options)
    referenced_data_sets, mappings = await get_linked_data_set_info(self, report, rds_ids_in_order)
    if len(referenced_data_sets) > 1:
        log_error(logger,
                  'Only one data set is supported for the current implementation of the echarts component.',
                  RuntimeError)

    data_set_id, data_set = list(referenced_data_sets.items())[0] if len(referenced_data_sets) > 0 else (None, None)
    rev_columns = {}
    if data_set_id is not None and data_set['columns']:
        rev_columns = {v: k for k, v in data_set['columns'].items()}

    data_is_custom = data_set_id in self._code_gen_tree.custom_data_sets_with_data
    fields = code_gen_from_list(get_fields_from_mapping(rev_columns, mappings, data_is_custom), 4)
    data_arg = await code_gen_data_arg(self, report, data_set_id, data_set, data_is_custom)

    options_code = code_gen_from_dict(echart_options, 4)

    return [
        'shimoku_client.plt.free_echarts(',
        *self.code_gen_report_params(report.cascade_to_dict()),
        f'    data={data_arg[0]}',
        *data_arg[1:],
        f'    fields={fields[0][4:]}',
        *fields[1:],
        f'    options={options_code[0][4:]}',
        *options_code[1:],
        ')'
    ]
