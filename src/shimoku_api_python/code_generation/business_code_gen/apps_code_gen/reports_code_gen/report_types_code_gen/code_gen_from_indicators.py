from typing import TYPE_CHECKING, List
from shimoku_api_python.resources.report import Report
from shimoku_api_python.code_generation.utils_code_gen import code_gen_from_dict
if TYPE_CHECKING:
    from ...code_gen_from_apps import AppCodeGen


async def code_gen_from_indicator(
        self: 'AppCodeGen', report: Report, properties: dict
) -> List[str]:
    """ Generate code for an indicator report.
    :param report: report to generate code from
    :param properties: properties of the report
    :return: list of code lines
    """
    report_dict = report.cascade_to_dict()
    if self._actual_bentobox:
        report_dict['sizeColumns'] += 1
    report_params = self.code_gen_report_params(report_dict)
    properties_code_lines = code_gen_from_dict(properties, 4)
    return [
        'shimoku_client.plt.indicator(',
        *report_params,
        f'    data={properties_code_lines[0][4:]}',
        *properties_code_lines[1:],
        ')'
    ]
