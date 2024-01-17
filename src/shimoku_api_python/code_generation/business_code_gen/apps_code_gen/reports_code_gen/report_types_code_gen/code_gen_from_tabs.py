from shimoku_api_python.resources.reports.tabs_group import TabsGroup
from shimoku_api_python.utils import create_function_name
from .code_gen_from_other import code_gen_from_other_reports, delete_default_properties
from shimoku_api_python.code_generation.utils_code_gen import code_gen_from_value
from typing import TYPE_CHECKING, List
if TYPE_CHECKING:
    from ...code_gen_from_apps import AppCodeGen


async def code_gen_tabs_and_other(
        self: 'AppCodeGen', tree: dict
) -> List[str]:
    """ Generate code for tabs and other components.
    :param tree: tree of reports
    :return: list of code lines
    """
    code_lines: List[str] = []
    reports_ordered = sorted(tree['other'] + tree['tab_groups'], key=lambda x: x['order'])
    for i, report in enumerate(reports_ordered):
        report_obj = report if not isinstance(report, dict) else report['tabs_group']
        if len(report_obj['bentobox']):
            if (self._actual_bentobox is None or
                    self._actual_bentobox['bentoboxId'] != report_obj['bentobox']['bentoboxId']):
                self._actual_bentobox = report_obj['bentobox']

                cols_size = self._actual_bentobox['bentoboxSizeColumns']
                rows_size = self._actual_bentobox['bentoboxSizeRows']
                code_lines.extend([
                    '',
                    f'shimoku_client.plt.set_bentobox(cols_size={cols_size}, rows_size={rows_size})'
                ])
        elif self._actual_bentobox is not None:
            self._actual_bentobox = None
            code_lines.append('shimoku_client.plt.pop_out_of_bentobox()')

        if isinstance(report, dict):
            code_lines.extend([
                '',
                f'tabs_group_{create_function_name(report["name"])}(shimoku_client)']
            )
        else:
            code_lines.extend(
                await code_gen_from_other_reports(self, report)
            )

        if i == len(reports_ordered) - 1 and self._actual_bentobox is not None:
            self._actual_bentobox = None
            code_lines.append('shimoku_client.plt.pop_out_of_bentobox()')

    return code_lines


async def code_gen_from_tabs_group(
        self: 'AppCodeGen', tree: dict, is_last: bool = False
) -> List[str]:
    """ Generate code for a tabs group.
    :param tree: tree of reports
    :param is_last: whether the tabs group is the last one
    :return: list of code lines
    """
    code_lines = []
    tabs_group: TabsGroup = tree['tabs_group']
    tabs_index = (tree['name'], list(tree['tabs'].keys())[0])
    parent_tabs_index = tree['parent_tabs_index']
    properties = delete_default_properties(tabs_group['properties'], TabsGroup.default_properties)
    del properties['hash']
    if 'tabs' in properties:
        del properties['tabs']
    if 'variant' in properties:
        properties['just_labels'] = True
        del properties['variant']

    for tab in tree['tabs']:
        code_lines.extend(['', f'def tab_{create_function_name(tabs_index[0])}_{create_function_name(tab)}():'])
        # tab_code = await code_gen_tabs_functions(tree['tabs'][tab]['tab_groups'])
        tab_code = await code_gen_tabs_and_other(self, tree['tabs'][tab])
        code_lines.extend([f'    {line}' for line in tab_code])

    code_lines.extend([
        '',
        'shimoku_client.plt.set_tabs_index(',
        f'    tabs_index=("{tabs_index[0]}", "{tabs_index[1]}"), order={tabs_group["order"]}, ',
    ])
    if tabs_group['sizeColumns']:
        code_lines.append(f'    cols_size={tabs_group["sizeColumns"]},')
    if tabs_group['sizeRows']:
        code_lines.append(f'    rows_size={tabs_group["sizeRows"]},')
    if tabs_group['sizePadding']:
        code_lines.append(f'    padding="{tabs_group["sizePadding"]}",')
    if parent_tabs_index:
        code_lines.extend([f'    parent_tabs_index={parent_tabs_index},'])
    code_lines.extend([f'    {k}={code_gen_from_value(v)},' for k, v in properties.items()])
    code_lines.extend([')'])

    for tab in tree['tabs']:
        code_lines.extend(['', f'shimoku_client.plt.change_current_tab("{tab}")'])
        code_lines.extend([f'tab_{create_function_name(tabs_index[0])}_{create_function_name(tab)}()'])

    if parent_tabs_index:
        if not is_last:
            code_lines.extend([
                '',
                f'shimoku_client.plt.set_tabs_index(("{parent_tabs_index[0]}", "{parent_tabs_index[1]}"))'
            ])
    else:
        code_lines.extend(['', 'shimoku_client.plt.pop_out_of_tabs_group()'])

    return code_lines


async def code_gen_tabs_functions(self, path: str) -> List[str]:
    """ Generate code for tabs groups functions.
    :return: list of code lines
    """
    code_lines = []
    if path not in self._code_gen_tree.all_tab_groups:
        return code_lines
    for tabs_group in self._code_gen_tree.all_tab_groups[path]:
        tab_code_lines = await code_gen_from_tabs_group(self, tabs_group)
        code_lines.extend([
            '',
            f'def tabs_group_{create_function_name(tabs_group["name"])}'
            f'(shimoku_client: shimoku.Client):',
            *['    ' + line for line in tab_code_lines]
        ])
    return code_lines
