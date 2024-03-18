from typing import Optional
from shimoku.actions_execution.execute_action import print_code_with_line_numbers
from shimoku.cli import CLIParser, CLIFuncParam
from shimoku.cli.cloud.cascade_get_resources import InitOptions, ResourceGetter
from shimoku.cli.utils import display_dict, save_as_file
import logging

logger = logging.getLogger(__name__)


def add_get_parser(parser: Optional[CLIParser] = None):
    """
    Function to add the get parser to a parser
    :param parser: Parser to add the get parser to
    :return: Get parser
    """
    params = {"name": "get", "description": "Commands to get resources"}
    if parser:
        get_parser = parser.add_command(**params)
    else:
        get_parser = CLIParser(**params)

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
    ]

    module_functions = [
        action_code,
        workspace,
        board,
        menu_path,
        component,
        activity,
        file,
        ai_output_file,
        role,
    ]

    for func in module_functions:
        get_parser.decor_add_command(common_args=common_args)(func)

    return get_parser


async def action_code(
    action: str = CLIFuncParam(prompt=True),
    save_to_path: str = CLIFuncParam(default=None, mandatory=False),
    **kwargs,
):
    """
    Get the code of an action
    :param action: Action name or id to get
    :param save_to_path: Path to save the code to, leave empty to print it
    """
    resource_getter = ResourceGetter(InitOptions(action=action, **kwargs))
    action_obj = await resource_getter.get_action()
    code = await action_obj.get_code()
    if save_to_path:
        with open(save_to_path, "w") as action_file:
            action_file.write(code)
        print(f"Code of the action ({action_obj['name']}) saved to {save_to_path}.")
    else:
        print(f"Code of the action ({action_obj['name']}):")
        print_code_with_line_numbers(code)


async def workspace(
    workspace_id: str = CLIFuncParam(prompt=True),
    show_theme: bool = CLIFuncParam(
        default=False, action="store_true", mandatory=False
    ),
    **kwargs,
):
    """Get a workspace
    :param workspace_id: UUID of the workspace to use
    :param show_theme: Flag to show the theme
    """
    resource_getter = ResourceGetter(InitOptions(workspace_id=workspace_id, **kwargs))
    business = await resource_getter.get_business()
    display_dict(
        business.cascade_to_dict(),
        fields=resource_getter.get_business_fields_to_show(show_theme=show_theme),
    )


async def board(
    workspace_id: Optional[str],
    board: str = CLIFuncParam(prompt=True),
    show_public_permission: bool = CLIFuncParam(
        default=False, action="store_true", mandatory=False
    ),
    show_theme: bool = CLIFuncParam(
        default=False, action="store_true", mandatory=False
    ),
    **kwargs,
):
    """Get a board
    :param workspace_id: UUID of the workspace to use
    :param board: Board name or id to get
    :param show_public_permission: Flag to show the public permission
    :param show_theme: Flag to show the theme
    """
    resource_getter = ResourceGetter(
        InitOptions(workspace_id=workspace_id, board=board, **kwargs)
    )
    dashboard = await resource_getter.get_dashboard()
    display_dict(
        dashboard.cascade_to_dict(),
        fields=resource_getter.get_dashboard_fields_to_show(
            show_public_permission=show_public_permission, show_theme=show_theme
        ),
    )


async def menu_path(
    workspace_id: Optional[str], menu_path: str = CLIFuncParam(prompt=True), **kwargs
):
    """Get a menu path
    :param workspace_id: UUID of the workspace to use
    :param menu_path: Menu path name or id to get
    """
    resource_getter = ResourceGetter(
        InitOptions(workspace_id=workspace_id, menu_path=menu_path, **kwargs)
    )
    app = await resource_getter.get_app()
    display_dict(app.cascade_to_dict(), resource_getter.get_app_fields_to_show())


async def component(
    workspace_id: Optional[str],
    menu_path: str = CLIFuncParam(mandatory=False),
    component_id: str = CLIFuncParam(prompt=True),
    **kwargs,
):
    """Get a component from a specific level, leave menu path and board empty to get a workspace component
    and specify only one to get a menu path or board component respectively. Don't specify both.
    :param workspace_id: UUID of the workspace to use
    :param menu_path: Menu path name or id to use
    :param component_id: Component name or id to get
    """
    resource_getter = ResourceGetter(
        InitOptions(
            workspace_id=workspace_id,
            menu_path=menu_path,
            component_id=component_id,
            **kwargs,
        )
    )
    report = await resource_getter.get_report()
    display_dict(report.cascade_to_dict(), resource_getter.get_report_fields_to_show())


async def activity(
    workspace_id: Optional[str],
    menu_path: str = CLIFuncParam(mandatory=False),
    activity: str = CLIFuncParam(prompt=True),
    show_template: bool = CLIFuncParam(
        default=False, action="store_true", mandatory=False
    ),
    **kwargs,
):
    """Get an activity from a specific level, leave menu path and board empty to get a workspace activity
    and specify only one to get a menu path or board activity respectively. Don't specify both.
    :param workspace_id: UUID of the workspace to use
    :param menu_path: Menu path name or id to use
    :param activity: Activity name or id to get
    :param show_template: Flag to show the template
    """
    resource_getter = ResourceGetter(
        InitOptions(
            workspace_id=workspace_id, menu_path=menu_path, activity=activity, **kwargs
        )
    )
    activity_obj = await resource_getter.get_activity()
    display_dict(
        activity_obj.cascade_to_dict(),
        resource_getter.get_activity_fields_to_show(show_template),
    )


async def file(
    workspace_id: Optional[str],
    menu_path: str = CLIFuncParam(prompt=True),
    file: str = CLIFuncParam(prompt=True),
    save_to_path: str = CLIFuncParam(default=None, mandatory=False),
    **kwargs,
):
    """Get a file object
    :param workspace_id: Workspace name or id to get
    :param menu_path: Menu path name or id to get
    :param file: File name or id to get
    :param save_to_path: Path to save the file to
    """
    resource_getter = ResourceGetter(
        InitOptions(workspace_id=workspace_id, menu_path=menu_path, file=file, **kwargs)
    )
    app = await resource_getter.get_app()
    file_obj = await resource_getter.get_file()
    if save_to_path:
        file_data = await app.get_file_object(file_obj["id"])
        save_as_file(logger, save_to_path, file_data, file_obj["name"])
        print(f"File ({file_obj['name']}) saved to {save_to_path}.")
    print(f"Metadata of the File ({file_obj['name']}):")
    display_dict(file_obj.cascade_to_dict(), ["tags", "metadata"])


async def ai_output_file(
    workspace_id: Optional[str],
    menu_path: str = CLIFuncParam(prompt=True),
    run_id: str = CLIFuncParam(prompt=True),
    file: str = CLIFuncParam(prompt=True),
    save_to_path: str = CLIFuncParam(default=None, mandatory=False),
    **kwargs,
):
    """Get an ai output file object
    :param workspace_id: Workspace name or id to get
    :param menu_path: Menu path name or id to get
    :param run_id: Run id to get the file from
    :param file: File name or id to get
    :param save_to_path: Path to save the file to
    """
    if not file:
        print("Please provide a file name or id.")
        return
    resource_getter = ResourceGetter(
        InitOptions(workspace_id=workspace_id, menu_path=menu_path, **kwargs)
    )
    ai_layer = await resource_getter.get_ai_layer()
    file_obj, metadata = await ai_layer.get_output_file_objects(
        run_id=run_id, file_name=file
    )
    if save_to_path:
        file_data = await ai_layer.get_output_file(file_obj["id"])
        save_as_file(logger, save_to_path, file_data, file_obj["name"])
        print(f"AI Output File ({metadata['name']}) saved to {save_to_path}.")
    print(f"Metadata of the File ({metadata['name']}):")
    display_dict(metadata, list(metadata.keys()))


async def role(
    workspace_id: Optional[str],
    menu_path: str = CLIFuncParam(group="menu_path_or_board", mandatory=False),
    board: str = CLIFuncParam(group="menu_path_or_board", mandatory=False),
    role: str = CLIFuncParam(prompt=True),
    **kwargs,
):
    """Get a role from a specific level, leave menu path and board empty to get a workspace role
    and specify only one to get a menu path or board role respectively. Don't specify both.
    :param workspace_id: UUID of the workspace to use
    :param menu_path: Menu path name or id to use
    :param board: Board name or id to use
    :param role: Role name or id to get
    """
    resource_getter = ResourceGetter(
        InitOptions(
            workspace_id=workspace_id,
            menu_path=menu_path,
            board=board,
            role=role,
            **kwargs,
        )
    )
    role_obj = await resource_getter.get_role_dict()
    display_dict(role_obj, fields=list(role_obj.keys()))


if __name__ == "__main__":
    add_get_parser().parse_args()
