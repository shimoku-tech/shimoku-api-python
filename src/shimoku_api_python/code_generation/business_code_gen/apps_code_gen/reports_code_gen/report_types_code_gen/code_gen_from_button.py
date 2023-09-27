from typing import TYPE_CHECKING, List
from shimoku_api_python.code_generation.utils_code_gen import code_gen_from_dict
if TYPE_CHECKING:
    from ...code_gen_from_apps import AppCodeGen
    from shimoku_api_python.resources.report import Report


async def code_gen_from_button_modal(
        self: 'AppCodeGen', report: 'Report', report_params: List[str]
) -> List[str]:
    modal_id = report['properties']['events']['onClick'][0]['params']['modalId']
    modal = await self._app.get_report(modal_id)
    path = modal['path']+'_' if modal['path'] else ''
    name = modal["properties"]["hash"][len(path):]
    return [
        'shimoku_client.plt.modal_button(',
        f'    modal="{name}",',
        *report_params,
        ')'
    ]


async def code_gen_from_button_activity(
        self: 'AppCodeGen', report: 'Report', report_params: List[str]
) -> List[str]:
    activity_id = report['properties']['events']['onClick'][0]['params']['activityId']
    activity = await self._app.get_activity(activity_id)
    return [
        'shimoku_client.plt.activity_button(',
        f'    activity_name="{activity["name"]}",',
        *report_params,
        ')'
    ]


async def code_gen_from_button_generic(
        self: 'AppCodeGen', report: 'Report', report_params: List[str]
) -> List[str]:
    events_code = code_gen_from_dict(report['properties']['events'], 4)
    return [
        'shimoku_client.plt.button(',
        *report_params,
        f'    on_click_events={events_code[0][4:]}',
        *events_code[1:],
        ')'
    ]


async def code_gen_from_button(
        self: 'AppCodeGen', report: 'Report'
) -> List[str]:
    """ Generate code for a button report.
    :param report: report to generate code from
    :return: list of code lines
    """
    report_params = [
        f'    label="{report["properties"]["text"]}",',
        f'    order={report["order"]},',
    ]
    if report['sizeColumns'] != 12:
        report_params.append(f'    cols_size={report["sizeColumns"]},')
    if report['sizeRows'] != 1:
        report_params.append(f'    rows_size={report["sizeRows"]},')
    if report['sizePadding'] != '0,0,0,0':
        report_params.append(f'    padding="{report["sizePadding"]}",')
    if report['properties']['align'] != 'stretch':
        report_params.append(f'    align="{report["properties"]["align"]}",')

    if report['properties']['events']['onClick'][0]['action'] == 'openModal':
        return await code_gen_from_button_modal(self, report, report_params)
    elif report['properties']['events']['onClick'][0]['action'] == 'openActivity':
        return await code_gen_from_button_activity(self, report, report_params)
    else:
        return await code_gen_from_button_generic(self, report, report_params)
