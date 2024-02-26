from typing import Optional, List

import tqdm
import subprocess
import os

from shimoku import Business
from shimoku.code_gen.business_code_gen.code_gen_from_business import BusinessCodeGen
from shimoku.code_gen.file_generator import CodeGenFileHandler

from shimoku.utils import create_function_name


async def generate_code(
    business_object: Business,
    business_id: str = "local",
    access_token: Optional[str] = None,
    universe_id: str = "local",
    environment: str = "production",
    output_path: str = "generated_code",
    menu_paths: Optional[list[str]] = None,
    use_black_formatter: bool = False,
    pbar: Optional[tqdm.tqdm] = None,
):
    """Main code generation function.
    :param business_object: business object to generate code for
    :param business_id: business id to use
    :param access_token: access token to use
    :param universe_id: universe id to use
    :param environment: environment to use
    :param output_path: output path to use
    :param menu_paths: list of menu paths to generate code for
    :param use_black_formatter: whether to use black formatter
    :param pbar: progress bar to use
    """
    await BusinessCodeGen(business_object, output_path).generate_code(
        business_id, menu_paths, pbar=pbar
    )
    business_name = create_function_name(business_object["name"])

    main_code_lines: List[str] = [
        "shimoku_client = Client(",
    ]
    if universe_id != "local":
        main_code_lines.extend(
            [f'    access_token="{access_token}",', f'    universe_id="{universe_id}",']
        )
    main_code_lines.extend(
        [
            f'    environment="{environment}",',
            "    async_execution=True,",
            '    verbosity="INFO"',
            ")",
            "",
            f"workspace_{business_name}(shimoku_client)",
            "",
            "shimoku_client.run()",
        ]
    )
    CodeGenFileHandler(output_path).generate_script_file(
        f"execute_workspace_{business_name}",
        [
            "from shimoku import Client",
            f"from {business_name}.workspace_{business_name} import workspace_{business_name}",
            "",
            "",
            "def main():",
            *[f"    {line}" for line in main_code_lines],
            "",
            "",
            'if __name__ == "__main__":',
            "    main()",
            "",
        ],
    )

    if use_black_formatter:
        # apply black formatting
        subprocess.run(["black", "-l", "80", os.path.join(output_path)])

    if pbar:
        pbar.update(1)
