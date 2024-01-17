from typing import TYPE_CHECKING, List
from shimoku_api_python.code_generation.utils_code_gen import code_gen_from_list
if TYPE_CHECKING:
    from ...code_gen_from_apps import AppCodeGen
    from shimoku_api_python.resources.report import Report


async def code_gen_from_form(
        self: 'AppCodeGen', report: 'Report', properties: dict
) -> List[str]:
    """ Generate code for a form report.
    :param report: report to generate code from
    :param properties: properties of the report
    :return: list of code lines
    """
    rds = (await report.get_report_data_sets())[0]
    rds_properties = rds['properties']
    form_groups = {group['title']: group['fields'] for group in rds_properties['fields']}
    input_form_params = []
    if rds_properties['fields'][0].get('nextFormGroup'):
        input_form_params.append(f'    dynamic_sequential_show=True,')
    if rds_properties.get('variant') == 'autoSend':
        input_form_params.append(f'    auto_send=True,')

    events_on_submit = []
    if 'events' not in properties:
        properties['events'] = {'onSubmit': []}
    for event in properties['events']['onSubmit']:
        if event['action'] == 'openModal':
            input_form_params.append(
                f'    modal="{(await self._app.get_report(event["params"]["modalId"]))["properties"]["hash"]}",'
            )
        elif event['action'] == 'openActivity':
            input_form_params.append(
                f'    activity_name="{(await self._app.get_activity(event["params"]["activityId"]))["name"]}",'
            )
        else:
            events_on_submit.append(event)
    if events_on_submit:
        code_gen_on_submit_events = code_gen_from_list(events_on_submit, 4)
        input_form_params.append(f'    on_submit_events={code_gen_on_submit_events[0][4:]}')
        input_form_params.extend(code_gen_on_submit_events[1:])

    report_params = [
        f'    order={report["order"]},',
    ]
    if report['sizeColumns'] != 12:
        report_params.append(f'    cols_size={report["sizeColumns"]},')
    if report['sizeRows'] != 1:
        report_params.append(f'    rows_size={report["sizeRows"]},')
    if report['sizePadding'] != '0,0,0,0':
        report_params.append(f'    padding="{report["sizePadding"]}",')
    return [
        'shimoku_client.plt.generate_input_form_groups(',
        f'    form_groups={form_groups},',
        *report_params,
        *input_form_params,
        ')'
    ]