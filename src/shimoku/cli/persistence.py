from shimoku.cli import CLIParser, CLIFuncParam
from shimoku.cli.cloud.cascade_get_resources import InitOptions, ResourceGetter
from typing import Optional
from shimoku.code_gen.main_code_gen import generate_code as gen_code
from shimoku.execution_logger import log_error
from shimoku.utils import create_function_name
from shimoku import Business
import tqdm
import tempfile
import shutil
import subprocess

import logging

logger = logging.getLogger(__name__)


def add_persistence_parser(parser: Optional[CLIParser] = None):
    """
    Function to add the playground parser to a parser
    :param parser: Parser to add the playground parser to
    """

    params = {
        "name": "persist",
        "description": "Commands to persist the contents of the current database",
    }

    if parser:
        persistence_parser = parser.add_command(**params)
    else:
        persistence_parser = CLIParser(**params)

    module_functions = [generate_code, commit, pull]

    common_args = [
        CLIFuncParam(
            name="local-port",
            arg_type=int,
            arg_help="Local port to use",
            mandatory=False,
        ),
        CLIFuncParam(
            name="environment",
            arg_type=str,
            arg_help="Environment to use",
            mandatory=False,
        ),
        CLIFuncParam(
            name="access-token",
            arg_type=str,
            arg_help="Access token to use",
            mandatory=False,
        ),
        CLIFuncParam(
            name="universe-id",
            arg_type=str,
            arg_help="Universe ID to use",
            mandatory=False,
        ),
        CLIFuncParam(
            name="workspace-id",
            arg_type=str,
            arg_help="Workspace ID to use",
            mandatory=False,
        ),
    ]

    for func in module_functions:
        persistence_parser.decor_add_command(common_args=common_args)(func)

    return persistence_parser


async def generate_code(
    output_path: Optional[str],
    menu_paths: Optional[list[str]],
    hide_progress_bar: bool = CLIFuncParam(
        default=False, action="store_true", mandatory=False
    ),
    use_black_formatter: bool = CLIFuncParam(
        default=False, action="store_true", mandatory=False
    ),
    **kwargs,
):
    """
    Generate code for a set workspace.
    :param menu_paths: List of menu paths to generate code from, leave empty to generate code for all menu paths.
    :param use_black_formatter: Use black formatter to format the generated code.
    :param output_path: Output path for the generated code.
    :param hide_progress_bar: Show progress bar while generating code.
    """
    resource_getter = ResourceGetter(InitOptions(**kwargs))
    business_object = await resource_getter.get_business()

    if not output_path:
        output_path = "generated_code"
    pbar = None
    if not hide_progress_bar:
        pbar = tqdm.tqdm(
            total=sum(
                [
                    len(await app.get_reports())
                    for app in await business_object.get_apps()
                ]
            )
            + 1
        )
    await gen_code(
        business_object=business_object,
        output_path=output_path,
        menu_paths=menu_paths,
        use_black_formatter=use_black_formatter,
        pbar=pbar,
    )
    if pbar:
        pbar.close()


async def commit(
    target_workspace: str = CLIFuncParam(prompt=True),
    target_access_token: str = CLIFuncParam(prompt=True),
    target_universe_id: str = CLIFuncParam(prompt=True),
    target_environment: str = CLIFuncParam(default="production", mandatory=False),
    hide_progress_bar: bool = CLIFuncParam(
        default=False, action="store_true", mandatory=False
    ),
    **kwargs,
):
    """
    Commit contents to another workspace.
    :param target_workspace: Workspace id or name to commit to.
    :param target_access_token: Access token with access to the target workspace.
    :param target_universe_id: Universe id of the target workspace.
    :param target_environment: Environment of the target workspace.
    :param hide_progress_bar: Show progress bar while generating code.
    """
    resource_getter = ResourceGetter(InitOptions(**kwargs))
    business_object = await resource_getter.get_business()
    try:
        target_resource_getter = ResourceGetter(
            InitOptions(
                universe_id=target_universe_id,
                access_token=target_access_token,
                environment=target_environment,
                workspace=target_workspace,
            )
        )
        target_business_object = await target_resource_getter.get_business()
    except Exception as e:
        log_error(logger, f"Could not access target workspace: {e}", RuntimeError)
        raise e  # IDE complains if this is not here, because it thinks that log_error is not raising an exception

    temp_dir = tempfile.mkdtemp()
    pbar = None
    if not hide_progress_bar:
        pbar = tqdm.tqdm(
            total=sum(
                [
                    len(await app.get_reports())
                    for app in await business_object.get_apps()
                ]
            )
            + 1
        )
    await gen_code(
        business_object=business_object,
        business_id=target_business_object["id"],
        access_token=target_access_token,
        universe_id=target_universe_id,
        environment=target_environment,
        output_path=temp_dir,
        menu_paths=None,
        use_black_formatter=False,
        pbar=pbar,
    )
    if pbar:
        pbar.close()
    process = subprocess.run(
        [
            "python",
            f'{temp_dir}/execute_workspace_{create_function_name(business_object["name"])}.py',
        ],
        check=True,
    )
    if process.returncode != 0:
        log_error(logger, "Error while executing the generated code.", RuntimeError)
    shutil.rmtree(temp_dir)


async def pull(
    origin_workspace: str = CLIFuncParam(prompt=True),
    origin_access_token: str = CLIFuncParam(prompt=True),
    origin_universe_id: str = CLIFuncParam(prompt=True),
    origin_environment: str = CLIFuncParam(default="production", mandatory=False),
    hide_progress_bar: bool = CLIFuncParam(
        default=False, action="store_true", mandatory=False
    ),
    **kwargs,
):
    """
    Pull contents from another workspace.
    :param origin_workspace: Workspace id or name to pull from.
    :param origin_access_token: Access token with access to the origin workspace.
    :param origin_universe_id: Universe id of the origin workspace.
    :param origin_environment: Environment of the origin workspace.
    :param hide_progress_bar: Show progress bar while retrieving the necessary data.
    """
    resource_getter = ResourceGetter(InitOptions(**kwargs))
    business_object: Business = await resource_getter.get_business()
    try:
        origin_resource_getter = ResourceGetter(
            InitOptions(
                universe_id=origin_universe_id,
                access_token=origin_access_token,
                environment=origin_environment,
                workspace=origin_workspace,
            )
        )
        origin_business_object = await origin_resource_getter.get_business()
    except Exception as e:
        log_error(logger, f"Could not access origin workspace: {e}", RuntimeError)
        raise e  # IDE complains if this is not here, because it thinks that log_error is not raising an exception

    temp_dir = tempfile.mkdtemp()
    pbar = None
    if not hide_progress_bar:
        pbar = tqdm.tqdm(
            total=sum(
                [
                    len(await app.get_reports())
                    for app in await origin_business_object.get_apps()
                ]
            )
            + 1
        )
    await gen_code(
        business_object=origin_business_object,
        business_id=business_object["id"],
        access_token=business_object.api_client.access_token,
        universe_id=business_object.parent["id"],
        environment=business_object.api_client.environment,
        output_path=temp_dir,
        menu_paths=None,
        use_black_formatter=False,
        pbar=pbar,
    )
    if pbar:
        pbar.close()
    process = subprocess.run(
        [
            "python",
            f'{temp_dir}/execute_workspace_{create_function_name(origin_business_object["name"])}.py',
        ],
        check=True,
    )
    if process.returncode != 0:
        log_error(logger, "Error while executing the generated code.", RuntimeError)
    shutil.rmtree(temp_dir)
