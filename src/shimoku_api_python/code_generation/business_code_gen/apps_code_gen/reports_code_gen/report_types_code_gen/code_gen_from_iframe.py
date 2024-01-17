from typing import TYPE_CHECKING, List
if TYPE_CHECKING:
    from ...code_gen_from_apps import AppCodeGen
    from shimoku_api_python.resources.report import Report


async def code_gen_from_iframe(
        self: 'AppCodeGen', report: 'Report'
) -> List[str]:
    """ Generate code for an iframe report.
    :param report: report to generate code from
    :return: list of code lines
    """
    code_lines = [
        'shimoku_client.plt.iframe(',
        f'    order={report["order"]},',
        f'    url="{report["dataFields"]["url"]}",',
    ]
    if report['dataFields']['height'] != 640:
        code_lines.append(f'    height={report["dataFields"]["height"]},')
    if report['sizeColumns'] != 12:
        code_lines.append(f'    cols_size={report["sizeColumns"]},')
    if report['sizePadding'] != '0,0,0,0':
        code_lines.append(f'    padding="{report["sizePadding"]}",')
    code_lines.append(')')
    return code_lines
