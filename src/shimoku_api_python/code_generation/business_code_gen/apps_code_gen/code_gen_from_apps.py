import tqdm

from copy import copy
from typing import Optional, List, Dict

from shimoku_api_python.resources.app import App
from shimoku_api_python.async_execution_pool import ExecutionPoolContext
from shimoku_api_python.utils import create_function_name

from ...tree_generation import CodeGenTree
from ...file_generator import CodeGenFileHandler
from .data_sets_code_gen.code_gen_from_data_sets import code_gen_from_shared_data_sets
from .reports_code_gen.code_gen_from_reports import code_gen_from_reports_tree
from .reports_code_gen.report_types_code_gen.code_gen_from_tabs import code_gen_tabs_functions
from .reports_code_gen.report_types_code_gen.code_gen_from_modal import code_gen_modals_functions


import logging
from shimoku_api_python.execution_logger import logging_before_and_after

logger = logging.getLogger(__name__)


class AppCodeGen:
    """ Class for generating code from a menu path. """

    def __init__(self, app: App, output_path: str, epc: ExecutionPoolContext, pbar: Optional[tqdm.tqdm] = None):
        self.epc = epc
        self._app = app
        self.app_f_name = 'menu_path_' + create_function_name(app['name'])
        self._output_path = (f'{output_path}/'
                             f'{self.app_f_name}')
        self._actual_bentobox: Optional[Dict] = None
        self._imports_code_lines = [
            'import os',
            'import shimoku_api_python as shimoku'
        ]
        self._file_generator: CodeGenFileHandler = CodeGenFileHandler(self._output_path)
        self._code_gen_tree: CodeGenTree = CodeGenTree(app, self._file_generator, pbar=pbar)

    @staticmethod
    def code_gen_report_params(report: Dict) -> List[str]:
        """ Generate code for the parameters of a report.
        :param report: report to generate code from
        :return: list of code lines
        """
        report_params_to_get = {
            'order': 'order', 'title': 'title',
            'sizeColumns': 'cols_size', 'sizeRows': 'rows_size',
            'sizePadding': 'padding',
        }
        return [f'    {report_params_to_get[k]}='
                + (f'"{(report[k])}",'if isinstance(report[k], str) else f'{report[k]},')
                for k in report if k in report_params_to_get]

    @logging_before_and_after(logger.debug)
    async def generate_code(self):
        """ Use the resources in the API to generate code_lines for the SDK. Create a file in
        the specified path with the generated code_lines.
        """
        await self._code_gen_tree.generate_tree()
        if self._code_gen_tree.needs_pandas:
            self._imports_code_lines.extend(['import pandas as pd'])

        code_lines: List[str] = []
        function_calls_code_lines: List[str] = []

        shared_data_sets_code_lines = await code_gen_from_shared_data_sets(self)
        scripts_imports = copy(self._imports_code_lines)
        for path in self._code_gen_tree.tree:
            function_code_lines = await code_gen_from_reports_tree(self, path)
            path_name = 'sub_path_' + create_function_name(path) if path else 'no_path'
            script_code_lines = [
                *scripts_imports,
                '',
                '',
                'data_folder_path = os.path.dirname(os.path.abspath(__file__)) + "/data"',
                *await code_gen_tabs_functions(self, path),
                *await code_gen_modals_functions(self, path),
                '',
                '',
                f'def {path_name}(shimoku_client: shimoku.Client):',
                *['    ' + line for line in function_code_lines],
                '',
            ]
            self._file_generator.generate_script_file(path_name, script_code_lines)
            self._imports_code_lines.append(
                f'from .{path_name} import {path_name}'
            )
            function_calls_code_lines.extend([
                '',
                f'shimoku_client.set_menu_path("{self._app["name"]}"' + (f', "{path}")' if path is not None else ')'),
                f'{path_name}(shimoku_client)'
            ])

        main_code_lines = [
            f'shimoku_client.set_menu_path("{self._app["name"]}")',
            'shimoku_client.plt.clear_menu_path()',
            *shared_data_sets_code_lines,
            *function_calls_code_lines,
        ]

        code_lines.extend([
            *self._imports_code_lines,
            '',
            '',
            'data_folder_path = os.path.dirname(os.path.abspath(__file__)) + "/data"',
            '',
            '',
            f'def {self.app_f_name}(shimoku_client: shimoku.Client):',
            *['    ' + line for line in main_code_lines],
            ''
        ])

        self._file_generator.generate_script_file('app', code_lines)
        # Create an __init__.py file for the imports to work
        self._file_generator.generate_script_file('__init__', [''])
