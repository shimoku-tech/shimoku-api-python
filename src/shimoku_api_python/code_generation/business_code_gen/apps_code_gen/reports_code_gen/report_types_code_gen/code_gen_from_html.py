from typing import TYPE_CHECKING, List
if TYPE_CHECKING:
    from ...code_gen_from_apps import AppCodeGen
    from shimoku_api_python.resources.report import Report


def code_gen_from_html_string(html_string: str):
    """ Generate code for an html string.
    :param html_string: html string to generate code from
    :return: list of code lines
    """
    code_lines = []
    current_line = ""
    for c in html_string:
        if c in ['\n', '\r']:
            code_lines.append(current_line)
            current_line = ""
        elif c == '<':
            code_lines.append(current_line)
            current_line = '<'
        elif c == ';' and len(current_line) > 60:
            code_lines.append(current_line + ';')
            current_line = ""
        else:
            current_line += c
    if current_line:
        code_lines.append(current_line)

    return [f'"{line}"' for line in code_lines if line]


async def code_gen_from_html(
        self: 'AppCodeGen', report: 'Report'
) -> List[str]:
    """ Generate code for an html report.
    :param report: report to generate code from
    :return: list of code lines
    """

    html = report['chartData'][0]["value"].replace("'", "\\'").replace('"', '\\"')
    html_lines = ['    ' + line for line in code_gen_from_html_string(html)]
    if not html_lines:
        return ['pass']
    html_lines[-1] += ','
    code_lines = [
        'shimoku_client.plt.html(',
        f'    order={report["order"]},',
    ]
    if report['sizeColumns'] != 12:
        code_lines.append(f'    cols_size={report["sizeColumns"]},')
    if report['sizeRows']:
        code_lines.append(f'    rows_size={report["sizeRows"]},')
    if report['sizePadding'] != '0,0,0,0':
        code_lines.append(f'    padding="{report["sizePadding"]}",')

    code_lines.extend([f'    html={html_lines[0][4:]}', *html_lines[1:], ')'])

    return code_lines
