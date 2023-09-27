from typing import TYPE_CHECKING, List
if TYPE_CHECKING:
    from ...code_gen_from_apps import AppCodeGen
    from shimoku_api_python.resources.report import Report


async def code_gen_from_filter(
        self: 'AppCodeGen', report: 'Report'
) -> List[str]:
    """ Generate code for a filter report.
    :param report: report to generate code from
    :return: list of code lines
    """
    filter_def = report['properties']['filter'][0]
    mapping = report['properties']['mapping'][0]
    field_name = filter_def['field']
    data_set = await self._app.get_data_set(mapping['id'])
    field = field_name if data_set['columns'] else mapping[field_name]
    report_params = [
        f'    order={report["order"]},',
        f'    data="{data_set["name"]}",',
        f'    field="{field}",',
    ]
    if report['sizeColumns'] != 4:
        report_params.append(f'    cols_size={report["sizeColumns"]},')
    if report['sizeRows'] != 1:
        report_params.append(f'    rows_size={report["sizeRows"]},')
    if report['sizePadding'] != '0,0,0,0':
        report_params.append(f'    padding="{report["sizePadding"]}",')
    if filter_def['inputType'] == 'CATEGORICAL_MULTI':
        report_params.append(f'    multi_select=True,')
    return [
        'shimoku_client.plt.filter(',
        *report_params,
        ')'
    ]
