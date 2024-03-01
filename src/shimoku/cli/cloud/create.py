import asyncio
from typing import Optional

from shimoku.api.resources.role import VALID_PERMISSIONS, VALID_RESOURCES, VALID_TARGETS

from shimoku.cli import CLIParser, CLIFuncParam
from shimoku.cli.cloud.cascade_get_resources import (
    InitOptions,
    ResourceGetter,
    Universe,
)
from shimoku.cli.utils import choose_from_menu, input_list, input_dict


def add_create_parser(parser: Optional[CLIParser] = None):
    """
    Function to add the create parser to a parser
    :param parser: Parser to add the create parser to
    :return: Create parser
    """
    params = {"name": "create", "description": "Commands to create resources"}
    if parser:
        create_parser = parser.add_command(**params)
    else:
        create_parser = CLIParser(**params)

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
        action,
        universe_api_key,
        workspace,
        menu_path,
        board,
        board_menu_path_link,
        file,
        ai_input_file,
        role,
    ]

    for func in module_functions:
        create_parser.decor_add_command(common_args=common_args)(func)

    return create_parser


async def action(
    name: str = CLIFuncParam(prompt=True),
    description: str = CLIFuncParam(prompt=True),
    path_to_code: str = CLIFuncParam(prompt=True, is_path=True),
    universe_api_key: Optional[str] = CLIFuncParam(mandatory=False),
    overwrite: bool = CLIFuncParam(default=False, action="store_true", mandatory=False),
    **kwargs,
):
    """Create an action
    :param name: Name of the action
    :param description: Description of the action
    :param path_to_code: Path to the code
    :param universe_api_key: UUID of the universe api key to use
    :param overwrite: Flag to overwrite the action if it already exists
    """
    actions_layer = await ResourceGetter(InitOptions(**kwargs)).get_actions_layer()
    await actions_layer.create_action(
        name=name,
        description=description,
        path_to_code=path_to_code,
        universe_api_key=universe_api_key,
        overwrite=overwrite,
    )


async def universe_api_key(description: str = CLIFuncParam(prompt=True), **kwargs):
    """Create a universe api key
    :param description: Description of the universe api key
    """
    universe: Universe = await ResourceGetter(InitOptions(**kwargs)).get_universe()
    await universe.create_universe_api_key(description=description)


async def workspace(
    name: str = CLIFuncParam(prompt=True),
    dont_create_default_roles: bool = CLIFuncParam(
        default=False, action="store_true", mandatory=False
    ),
    theme: dict = CLIFuncParam(default=None, mandatory=False),
    **kwargs,
):
    """Create a workspace
    :param name: Workspace name to create
    :param dont_create_default_roles: Flag to not create default roles
    :param theme: Theme to use
    """
    businesses_layer = await ResourceGetter(
        InitOptions(**kwargs)
    ).get_businesses_layer()
    await businesses_layer.create_workspace(
        name=name, create_default_roles=not dont_create_default_roles, theme=theme
    )


async def menu_path(
    workspace_id: Optional[str], name: str = CLIFuncParam(prompt=True), **kwargs
):
    """Create a menu path in the workspace
    :param workspace_id: UUID of the workspace to use
    :param name: Menu path name to create
    :param order: Order of the menu path
    """
    resource_getter = ResourceGetter(InitOptions(workspace_id=workspace_id, **kwargs))
    apps_layer = await resource_getter.get_apps_layer()
    await apps_layer.get_menu_path(name=name)


async def board(
    workspace_id: Optional[str],
    order: Optional[int],
    name: str = CLIFuncParam(prompt=True),
    public: bool = CLIFuncParam(default=False, action="store_true", mandatory=False),
    not_enabled: bool = CLIFuncParam(
        default=False, action="store_true", mandatory=False
    ),
    group_menu_paths: bool = CLIFuncParam(
        default=False, action="store_true", mandatory=False
    ),
    **kwargs,
):
    """Create a board in the workspace
    :param workspace_id: UUID of the workspace to use
    :param name: Board name to create
    :param order: Order of the board
    :param public: Flag to set the board as public
    :param not_enabled: Flag to set the board as not enabled
    :param group_menu_paths: Flag to ask for menu paths to group
    """
    resource_getter = ResourceGetter(InitOptions(workspace_id=workspace_id, **kwargs))
    dashboards_layer = await resource_getter.get_dashboards_layer()
    dashboard = await dashboards_layer.create_board(
        name=name, order=order, is_public=public, is_disabled=not_enabled
    )
    if group_menu_paths:
        app_names = []
        business = await resource_getter.get_business()
        app_objs = await business.get_apps()
        options = [app["name"] for app in app_objs] + [""]
        print("Select the menu paths to group in the board (empty to stop):")
        while True:
            chosen_app = choose_from_menu(options)
            if not chosen_app:
                break
            options.remove(chosen_app)
            app_names.append(chosen_app)

        await dashboards_layer.group_menu_paths(
            uuid=dashboard["id"], menu_path_names=app_names
        )


async def board_menu_path_link(
    workspace_id: Optional[str],
    board: str = CLIFuncParam(prompt=True),
    menu_path: str = CLIFuncParam(prompt=True),
    **kwargs,
):
    """Create a board menu path link
    :param workspace_id: UUID of the workspace to use
    :param board: Board id or name to link
    :param menu_path: Menu path to link
    """
    resource_getter = ResourceGetter(
        InitOptions(
            board=board, menu_path=menu_path, workspace_id=workspace_id, **kwargs
        )
    )
    dashboards_layer = await resource_getter.get_dashboards_layer()
    dashboard, app = await asyncio.gather(
        resource_getter.get_dashboard(), resource_getter.get_app()
    )
    await dashboards_layer.add_menu_path_in_board(
        menu_path_id=app["id"], uuid=dashboard["id"]
    )


def get_file_data(path_to_file: str) -> Optional[bytes]:
    """Get the data of the file
    :param path_to_file: Path to the file
    """
    try:
        with open(path_to_file, "rb") as file_:
            return file_.read()
    except FileNotFoundError:
        print(f"File {path_to_file} not found")


async def file(
    workspace_id: Optional[str],
    menu_path: str = CLIFuncParam(prompt=True),
    name: str = CLIFuncParam(prompt=True),
    path_to_file: str = CLIFuncParam(prompt=True, is_path=True),
    ask_for_tags: bool = CLIFuncParam(
        default=False, action="store_true", mandatory=False
    ),
    ask_for_metadata: bool = CLIFuncParam(
        default=False, action="store_true", mandatory=False
    ),
    **kwargs,
):
    """Create a file in the menu path
    :param workspace_id: UUID of the workspace to use
    :param menu_path: Menu path id or name to use
    :param name: File name to create
    :param path_to_file: Path to the file to upload
    :param ask_for_tags: Flag to ask for tags
    :param ask_for_metadata: Flag to ask for metadata
    """
    tags, metadata = None, None
    file_content = get_file_data(path_to_file)
    if file_content is None:
        return
    resource_getter = ResourceGetter(
        InitOptions(menu_path=menu_path, workspace_id=workspace_id, **kwargs)
    )
    files_layer = await resource_getter.get_files_layer()
    if ask_for_tags:
        tags = input_list()
    if ask_for_metadata:
        metadata = input_dict()
    await files_layer.post_object(
        file_name=name, obj=file_content, tags=tags, metadata=metadata
    )


async def ai_input_file(
    workspace_id: Optional[str],
    menu_path: str = CLIFuncParam(prompt=True),
    name: str = CLIFuncParam(prompt=True),
    path_to_file: str = CLIFuncParam(prompt=True, is_path=True),
    **kwargs,
):
    """Create an ai input file in the menu path
    :param workspace_id: UUID of the workspace to use
    :param menu_path: Menu path id or name to use
    :param name: File name to create
    :param path_to_file: Path to the file to upload
    """
    file_content = get_file_data(path_to_file)
    if file_content is None:
        return
    resource_getter = ResourceGetter(
        InitOptions(menu_path=menu_path, workspace_id=workspace_id, **kwargs)
    )
    ai_layer = await resource_getter.get_ai_layer()
    await ai_layer.create_input_files(input_files={name: file_content})


async def role(
    workspace_id: Optional[str],
    menu_path: str = CLIFuncParam(group="menu_path_or_board", mandatory=False),
    board: str = CLIFuncParam(group="menu_path_or_board", mandatory=False),
    name: str = CLIFuncParam(prompt=True),
    **kwargs,
):
    """Create a role in a specific level, leave menu path and board empty to create a workspace role
    and specify only one to create a menu path or board role respectively. Don't specify both.
    :param workspace_id: UUID of the workspace to use
    :param menu_path: Menu path id or name to use
    :param board: Board id or name to use
    :param name: Role name to create
    """
    role_resource = choose_from_menu(VALID_RESOURCES, "Choose a resource: ")
    permission = choose_from_menu(VALID_PERMISSIONS, "Choose a permission: ")
    target = choose_from_menu(VALID_TARGETS, "Choose a target: ")
    resource_getter = ResourceGetter(
        InitOptions(
            workspace_id=workspace_id, menu_path=menu_path, board=board, **kwargs
        )
    )

    if menu_path:
        layer = await resource_getter.get_apps_layer()
        resource_id = (await resource_getter.get_app())["id"]
    elif board:
        layer = await resource_getter.get_dashboards_layer()
        resource_id = (await resource_getter.get_dashboard())["id"]
    else:
        layer = await resource_getter.get_businesses_layer()
        resource_id = (await resource_getter.get_business())["id"]

    await layer.create_role(
        uuid=resource_id,
        role_name=name,
        resource=role_resource,
        permission=permission,
        target=target,
    )


if __name__ == "__main__":
    add_create_parser().parse_args()
