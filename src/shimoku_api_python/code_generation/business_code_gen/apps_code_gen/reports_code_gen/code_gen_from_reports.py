from typing import TYPE_CHECKING, List
from shimoku_api_python.utils import create_function_name
from .report_types_code_gen.code_gen_from_tabs import code_gen_tabs_and_other

if TYPE_CHECKING:
    from ..code_gen_from_apps import AppCodeGen


async def code_gen_from_reports_tree(self: 'AppCodeGen', path: str) -> List[str]:
    code_lines = [
        # *(await code_gen_tabs_functions(all_tab_groups[path]) if path in all_tab_groups else []),
        # *(await code_gen_modals_functions(tree[path]['modals']) if path in tree else []),
    ]
    tree = self._code_gen_tree.tree
    for modal_dict in tree[path]['modals']:
        code_lines.extend([
            '',
            f'modal_{create_function_name(modal_dict["name"])}(shimoku_client)'
        ])
    # if len(tree[path]['modals']) > 0:
    #     code_lines.extend(['', 'shimoku_client.plt.pop_out_of_modal()', ''])
    code_lines.extend(['', *await code_gen_tabs_and_other(self, tree[path])])
    return code_lines
