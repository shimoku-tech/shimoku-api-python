from typing import TYPE_CHECKING, List
import asyncio
from copy import deepcopy
from shimoku_api_python.utils import change_data_set_name_with_report, revert_uuids_from_dict
from ...data_sets_code_gen.code_gen_from_data_sets import code_gen_read_csv_from_data_set, get_linked_data_set_info
from shimoku_api_python.code_generation.utils_code_gen import code_gen_from_list

if TYPE_CHECKING:
    from ...code_gen_from_apps import AppCodeGen
    from shimoku_api_python.resources.report import Report


# Todo needs to have the correct names for the columns
async def code_gen_from_annotated_echart(
        self: 'AppCodeGen', report: 'Report', properties: dict
) -> List[str]:
    """ Generate code for an echarts report.
    :param report: report to generate code from
    :param report_params: parameters of the report
    :param properties: properties of the report
    :return: list of code lines """
    echart_options = deepcopy(properties['option'])
    rds_ids_in_order = revert_uuids_from_dict(echart_options)
    data_set_ids, _ = await get_linked_data_set_info(self, report, rds_ids_in_order)
    data_sets = await asyncio.gather(*[self._app.get_data_set(ds_id) for ds_id in data_set_ids])
    if data_sets[0]['columns']:
        rev_data_set_columns = [{v: k for k, v in data_set['columns'].items()} for data_set in data_sets]
    else:
        rev_data_set_columns = [{"dateField1": "dateField1", "intField1": "intField1"} for _ in data_sets]
    data_set_names = [change_data_set_name_with_report(data_set, report) for data_set in data_sets]
    data_args = await asyncio.gather(*[code_gen_read_csv_from_data_set(data_set, name)
                                       for data_set, name in zip(data_sets, data_set_names)])
    data_args = [data_arg for data_arg in data_args if data_arg is not None]
    slider_properties = properties.get('slider') or {}
    marks = slider_properties.pop('marks') if 'marks' in slider_properties else None

    slider_params = []
    if slider_properties:
        slider_params.append(f'    slider_config={slider_properties},')
    if marks:
        slider_params.append(f'    slider_marks={[(mark["label"], mark["value"]) for mark in marks]},')
    y_code_lines = code_gen_from_list([rev_data_set_columns[i]["intField1"] for i in range(len(data_args))], 4)
    return [
        'shimoku_client.plt.annotated_chart(',
        f'    data=[{", ".join(data_args)}],',
        f'    x="{rev_data_set_columns[0]["dateField1"]}",',
        f'    y={y_code_lines[0][4:]}',
        *y_code_lines[1:],
        *slider_params,
        *self.code_gen_report_params(report.cascade_to_dict()),
        ')'
    ]
