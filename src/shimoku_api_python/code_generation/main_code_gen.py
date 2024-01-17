from typing import Optional, List

import tqdm
import subprocess
import os

from shimoku_api_python.resources.business import Business
from shimoku_api_python.code_generation.business_code_gen.code_gen_from_business import BusinessCodeGen
from shimoku_api_python.code_generation.file_generator import CodeGenFileHandler

from shimoku_api_python.utils import create_function_name

from shimoku_api_python.async_execution_pool import ExecutionPoolContext

import logging
from shimoku_api_python.execution_logger import logging_before_and_after
logger = logging.getLogger(__name__)


@logging_before_and_after(logging_level=logger.debug)
async def generate_code(
        business_object: Business,
        business_id: str,
        access_token: str,
        universe_id: str,
        environment: str,
        output_path: str,
        epc: ExecutionPoolContext,
        menu_paths: Optional[list[str]] = None,
        use_black_formatter: bool = False,
        pbar: Optional[tqdm.tqdm] = None
):
    """ Main code generation function.
    :param business_object: business object to generate code for
    :param business_id: business id to use
    :param access_token: access token to use
    :param universe_id: universe id to use
    :param environment: environment to use
    :param output_path: output path to use
    :param epc: execution pool context to use
    :param menu_paths: list of menu paths to generate code for
    :param use_black_formatter: whether to use black formatter
    :param pbar: progress bar to use
    """
    await BusinessCodeGen(business_object, output_path, epc).generate_code(business_id, menu_paths, pbar=pbar)
    business_name = create_function_name(business_object['name'])

    main_code_lines: List[str] = [
        'shimoku_client = shimoku.Client(',
    ]
    if access_token != 'local':
        main_code_lines.extend([
            f'    access_token="{access_token}",',
            f'    universe_id="{universe_id}",'
        ])
    main_code_lines.extend([
        f'    environment="{environment}",',
        f'    async_execution=True,',
        '    verbosity="INFO"',
        ')',
        '',
        f'workspace_{business_name}(shimoku_client)',
        '',
        'shimoku_client.run()'
    ])
    CodeGenFileHandler(output_path).generate_script_file(
        f'execute_workspace_{business_name}',
        [
            'import shimoku_api_python as shimoku',
            f'from {business_name}.workspace_{business_name} import workspace_{business_name}',
            '',
            '',
            'def main():',
            *[f'    {line}' for line in main_code_lines],
            '',
            '',
            'if __name__ == "__main__":',
            '    main()'
            ''
        ]
    )

    if use_black_formatter:
        # apply black formatting
        subprocess.run(["black", "-l", "80", os.path.join(output_path)])

    if pbar:
        pbar.update(1)
