from shimoku.utils import create_function_name
from shimoku.code_gen.business_code_gen.apps_code_gen.reports_code_gen. \
        report_types_code_gen.code_gen_from_other import delete_default_properties
from shimoku.code_gen.business_code_gen.apps_code_gen.reports_code_gen. \
        report_types_code_gen.code_gen_from_tabs import code_gen_tabs_and_other
from typing import TYPE_CHECKING
from shimoku.code_gen.utils_code_gen import code_gen_from_value
from shimoku.api.resources.reports.modal import Modal
if TYPE_CHECKING:
    from shimoku.code_gen.business_code_gen.apps_code_gen.code_gen_from_apps import AppCodeGen


async def code_gen_from_modal(self: 'AppCodeGen', tree: dict) -> list[str]:
    """ Generate code for a modal.
    :param tree: tree of reports
    :return: list of code lines
    """
    # code_lines = (await code_gen_tabs_functions(tree['tab_groups']))
    code_lines = []
    modal: Modal = tree['modal']
    properties = delete_default_properties(modal['properties'], Modal.default_properties)
    properties['modal_name'] = tree['name']
    del properties['hash']
    if 'reportIds' in properties:
        del properties['reportIds']
    if 'open' in properties:
        if properties['open']:
            properties['open_by_default'] = True
        del properties['open']
    code_lines.extend([
        'shimoku_client.plt.set_modal(',
        *[f'    {k}={code_gen_from_value(v)},' for k, v in properties.items()],
        ')',
    ])
    code_lines.extend(await code_gen_tabs_and_other(self, tree))
    code_lines.extend(['', 'shimoku_client.plt.pop_out_of_modal()'])
    return code_lines


async def code_gen_modals_functions(self: 'AppCodeGen', path: str) -> list[str]:
    """ Generate code for modals.
    :param path: path to the modals
    :return: list of code lines
    """
    code_lines = []
    for modal in self._code_gen_tree.tree[path]['modals']:
        modal_code_lines = await code_gen_from_modal(self, modal)
        code_lines.extend([
            '',
            f'def modal_{create_function_name(modal["name"])}'
            f'(shimoku_client: Client):',
            *['    ' + line for line in modal_code_lines]
        ])
    return code_lines
