from typing import Optional
from shimoku.cli import CLIParser, CLIFuncParam
from shimoku.cli.cloud.cascade_get_resources import InitOptions, ResourceGetter

import asyncio

import logging

logger = logging.getLogger(__name__)


def add_delete_parser(parser: Optional[CLIParser] = None):
    """
    Function to add the delete parser to a parser
    :param parser: Parser to add the delete parser to
    :return: Delete parser
    """
    params = {"name": "delete", "description": "Commands to create resources"}
    if parser:
        delete_parser = parser.add_command(**params)
    else:
        delete_parser = CLIParser(**params)

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
        universe_api_key,
        action,
        workspace,
        workspace_contents,
        board,
        boards,
        board_menu_path_link,
        board_menu_path_links,
        menu_path,
        menu_paths,
        component,
        components,
        data_set,
        data_sets,
        file,
        files,
        ai_input_file,
        ai_model,
        role,
    ]

    for func in module_functions:
        delete_parser.decor_add_command(common_args=common_args)(func)

    return delete_parser


async def action(
    action: str = CLIFuncParam(prompt=True),
    **kwargs,
):
    """
    Delete an action
    :param action: Action id or name to delete
    """
    resource_getter = ResourceGetter(InitOptions(action=action, **kwargs))
    actions_layer = await resource_getter.get_actions_layer()
    action_obj = await resource_getter.get_action()
    if not action_obj:
        print(f"Action {action} not found")
        return
    await actions_layer.delete_action(uuid=action_obj["id"])


async def universe_api_key(uuid: str = CLIFuncParam(prompt=True), **kwargs):
    """Delete a universe api key
    :param uuid: UUID of the universe api key
    """
    resource_getter = ResourceGetter(InitOptions(**kwargs))
    universes_layer = await resource_getter.get_universes_layer()
    await universes_layer.delete_universe_api_key(
        uuid=kwargs["uuid"], api_key_uuid=uuid
    )


async def workspace(workspace_id: str = CLIFuncParam(prompt=True), **kwargs):
    """Delete the workspace
    :param workspace_id: UUID of the workspace to use
    """
    confirmation = input("Are you sure you want to delete the workspace? (y/n): ")
    if confirmation.lower() != "y" and confirmation.lower() != "yes":
        logger.info("Cancelling delete workspace")
        return
    resource_getter = ResourceGetter(InitOptions(workspace_id=workspace_id, **kwargs))
    businesses_layer = await resource_getter.get_businesses_layer()
    await businesses_layer.delete_workspace(workspace_id)


async def workspace_contents(
    workspace_id: Optional[str],
    force: bool = CLIFuncParam(default=False, action="store_true", mandatory=False),
    **kwargs,
):
    """Delete all contents in the workspace
    :param workspace_id: UUID of the workspace to use
    :param force: Flag to not ask for confirmation
    """
    if not force:
        confirmation = input(
            "Are you sure you want to delete all contents in the workspace?"
            "\nthis action will delete all files, data sets and activities in the workspace"
            "\nmake sure to not lose any sensitive data. (y/n): "
        )
        if confirmation.lower() != "y" and confirmation.lower() != "yes":
            logger.info("Cancelling delete all workspace contents")
            return
    resource_getter = ResourceGetter(InitOptions(workspace_id=workspace_id, **kwargs))
    businesses_layer = await resource_getter.get_businesses_layer()
    app_layer = await resource_getter.get_apps_layer()
    business = await resource_getter.get_business()
    await asyncio.gather(
        *[
            app_layer.delete_all_menu_path_activities(app["id"])
            for app in await business.get_apps()
        ]
    )
    await businesses_layer.delete_all_workspace_menu_paths(business["id"])
    await businesses_layer.delete_all_workspace_boards(business["id"])


async def board(
    workspace_id: Optional[str],
    board: str = CLIFuncParam(prompt=True),
    force: bool = CLIFuncParam(default=False, action="store_true", mandatory=False),
    **kwargs,
):
    """Delete the board in the workspace
    :param workspace_id: UUID of the workspace to use
    :param board: Board id or name to delete
    :param force: Flag to force delete the board
    """
    resource_getter = ResourceGetter(
        InitOptions(workspace_id=workspace_id, board=board, **kwargs)
    )
    dashboards_layer = await resource_getter.get_dashboards_layer()
    dashboard = await resource_getter.get_dashboard()
    if not dashboard:
        print(f"Board {board} not found")
        return
    if force:
        await dashboards_layer.force_delete_board(dashboard["id"])
    else:
        await dashboards_layer.delete_board(dashboard["id"])


async def boards(
    workspace_id: Optional[str],
    force: bool = CLIFuncParam(default=False, action="store_true", mandatory=False),
    **kwargs,
):
    """Delete all boards in the workspace
    :param workspace_id: UUID of the workspace to use
    :param force: Flag to force delete the boards
    """
    resource_getter = ResourceGetter(InitOptions(workspace_id=workspace_id, **kwargs))
    businesses_layer = await resource_getter.get_businesses_layer()
    business = await resource_getter.get_business()
    await businesses_layer.delete_all_workspace_boards(business["id"], force=force)


async def board_menu_path_link(
    workspace_id: Optional[str],
    board: str = CLIFuncParam(prompt=True),
    menu_path: str = CLIFuncParam(prompt=True),
    **kwargs,
):
    """Delete the board menu path link
    :param workspace_id: UUID of the workspace to use
    :param board: Board id or name to use
    :param menu_path: Menu path id or name to delete
    """
    resource_getter = ResourceGetter(
        InitOptions(
            board=board, menu_path=menu_path, workspace_id=workspace_id, **kwargs
        )
    )
    dashboards_layer = await resource_getter.get_dashboards_layer()
    dashboard = await resource_getter.get_dashboard()
    app = await resource_getter.get_app()
    if not dashboard:
        print(f"Board {board} not found")
        return
    if not app:
        print(f"Menu path {menu_path} not found")
        return
    await dashboards_layer.remove_menu_path_from_board(
        menu_path_id=app["id"], uuid=dashboard["id"]
    )


async def board_menu_path_links(
    workspace_id: Optional[str], board: str = CLIFuncParam(prompt=True), **kwargs
):
    """Delete all board menu path links
    :param workspace_id: UUID of the workspace to use
    :param board: Board id or name to use
    """
    resource_getter = ResourceGetter(
        InitOptions(board=board, workspace_id=workspace_id, **kwargs)
    )
    dashboards_layer = await resource_getter.get_dashboards_layer()
    dashboard = await resource_getter.get_dashboard()
    if not dashboard:
        print(f"Board {board} not found")
        return
    await dashboards_layer.remove_all_menu_paths_from_board(dashboard["id"])


async def menu_path(
    workspace_id: Optional[str], menu_path: str = CLIFuncParam(prompt=True), **kwargs
):
    """Delete the menu path in the workspace
    :param workspace_id: UUID of the workspace to use
    :param menu_path: Menu path id or name to delete
    """
    resource_getter = ResourceGetter(
        InitOptions(workspace_id=workspace_id, menu_path=menu_path, **kwargs)
    )
    apps_layer = await resource_getter.get_apps_layer()
    app = await resource_getter.get_app()
    if not app:
        print(f"Menu path {menu_path} not found")
        return
    await apps_layer.delete_menu_path(uuid=app["id"])


async def menu_paths(workspace_id: Optional[str], **kwargs):
    """Delete all menu paths in the workspace
    :param workspace_id: UUID of the workspace to use
    """
    resource_getter = ResourceGetter(InitOptions(workspace_id=workspace_id, **kwargs))
    businesses_layer = await resource_getter.get_businesses_layer()
    business = await resource_getter.get_business()
    await businesses_layer.delete_all_workspace_menu_paths(business["id"])


async def component(
    workspace_id: Optional[str],
    menu_path: str = CLIFuncParam(prompt=True),
    component_id: str = CLIFuncParam(prompt=True),
    **kwargs,
):
    """Delete the component from a menu path
    :param workspace_id: UUID of the workspace to use
    :param menu_path: Menu path id or name to use
    :param component_id: Component id or name to delete
    """
    resource_getter = ResourceGetter(
        InitOptions(
            workspace_id=workspace_id,
            menu_path=menu_path,
            component_id=component_id,
            **kwargs,
        )
    )
    reports_layer = await resource_getter.get_reports_layer()
    report = await resource_getter.get_report()
    if not report:
        print(f"Component {component_id} not found")
        return
    await reports_layer.delete_component(uuid=report["id"])


async def components(
    workspace_id: Optional[str],
    menu_path: str = CLIFuncParam(prompt=True),
    sub_path: str = CLIFuncParam(mandatory=False),
    **kwargs,
):
    """Delete all components from a menu path
    :param workspace_id: UUID of the workspace to use
    :param menu_path: Menu path id or name to use
    :param sub_path: Sub path to clear
    """
    resource_getter = ResourceGetter(
        InitOptions(workspace_id=workspace_id, menu_path=menu_path, **kwargs)
    )
    apps_layer = await resource_getter.get_apps_layer()
    app = await resource_getter.get_app()
    await apps_layer.delete_all_menu_path_components(uuid=app["id"], sub_path=sub_path)


async def data_set(
    workspace_id: Optional[str],
    menu_path: str = CLIFuncParam(prompt=True),
    data_set: str = CLIFuncParam(prompt=True),
    **kwargs,
):
    """Delete the data set from a menu path
    :param workspace_id: UUID of the workspace to use
    :param menu_path: Menu path id or name to use
    :param data_set: Data set id or name to delete
    """
    resource_getter = ResourceGetter(
        InitOptions(
            workspace_id=workspace_id, menu_path=menu_path, data_set=data_set, **kwargs
        )
    )
    data_sets_layer = await resource_getter.get_data_sets_layer()
    data_set_obj = await resource_getter.get_data_set()
    if not data_set_obj:
        print(f"Data set {data_set} not found")
        return
    await data_sets_layer.delete_data_set(uuid=data_set_obj["id"])


async def data_sets(
    workspace_id: Optional[str], menu_path: str = CLIFuncParam(prompt=True), **kwargs
):
    """Delete all data sets from a menu path
    :param workspace_id: UUID of the workspace to use
    :param menu_path: Menu path id or name to use
    """
    resource_getter = ResourceGetter(
        InitOptions(workspace_id=workspace_id, menu_path=menu_path, **kwargs)
    )
    apps_layer = await resource_getter.get_apps_layer()
    app = await resource_getter.get_app()
    await apps_layer.delete_all_menu_path_data_sets(uuid=app["id"])


async def activity(
    workspace_id: Optional[str],
    menu_path: str = CLIFuncParam(prompt=True),
    activity: str = CLIFuncParam(prompt=True),
    with_linked_to_templates: bool = CLIFuncParam(
        default=False, action="store_true", mandatory=False
    ),
    **kwargs,
):
    """Delete the activity from a menu path
    :param workspace_id: UUID of the workspace to use
    :param menu_path: Menu path id or name to use
    :param activity: Activity id or name to delete
    :param with_linked_to_templates: Flag to delete the activity even if it's linked to a template
    """
    resource_getter = ResourceGetter(
        InitOptions(
            workspace_id=workspace_id, menu_path=menu_path, activity=activity, **kwargs
        )
    )
    activities_layer = await resource_getter.get_activities_layer()
    activity = await resource_getter.get_activity()
    if not activity:
        print(f"Activity {activity} not found")
        return
    await activities_layer.delete_activity(
        uuid=activity["id"], with_linked_to_templates=with_linked_to_templates
    )


async def activities(
    workspace_id: Optional[str],
    menu_path: str = CLIFuncParam(prompt=True),
    with_linked_to_templates: bool = CLIFuncParam(
        default=False, action="store_true", mandatory=False
    ),
    **kwargs,
):
    """Delete all activities from a menu path
    :param workspace_id: UUID of the workspace to use
    :param menu_path: Menu path id or name to use
    :param with_linked_to_templates: Flag to delete the activities even if they were linked to templates
    """
    resource_getter = ResourceGetter(
        InitOptions(workspace_id=workspace_id, menu_path=menu_path, **kwargs)
    )
    apps_layer = await resource_getter.get_apps_layer()
    app = await resource_getter.get_app()
    await apps_layer.delete_all_menu_path_activities(
        uuid=app["id"], with_linked_to_templates=with_linked_to_templates
    )


async def file(
    workspace_id: Optional[str],
    menu_path: str = CLIFuncParam(prompt=True),
    file: str = CLIFuncParam(prompt=True),
    with_shimoku_generated: bool = CLIFuncParam(
        default=False, action="store_true", mandatory=False
    ),
    **kwargs,
):
    """Delete the file from a menu path
    :param workspace_id: UUID of the workspace to use
    :param menu_path: Menu path id or name to use
    :param file: File id or name to delete
    :param with_shimoku_generated: Flag to delete the file even if it was generated by shimoku
    """
    resource_getter = ResourceGetter(
        InitOptions(workspace_id=workspace_id, menu_path=menu_path, file=file, **kwargs)
    )
    files_layer = await resource_getter.get_files_layer()
    file = await resource_getter.get_file()
    if not file:
        print(f"File {file} not found")
        return
    print(file["id"])
    await files_layer.delete_file(
        uuid=file["id"], with_shimoku_generated=with_shimoku_generated
    )


async def files(
    workspace_id: Optional[str],
    menu_path: str = CLIFuncParam(prompt=True),
    with_shimoku_generated: bool = CLIFuncParam(
        default=False, action="store_true", mandatory=False
    ),
    **kwargs,
):
    """Delete all files from a menu path
    :param workspace_id: UUID of the workspace to use
    :param menu_path: Menu path id or name to use
    :param with_shimoku_generated: Flag to delete the files even if they were generated by shimoku
    """
    resource_getter = ResourceGetter(
        InitOptions(workspace_id=workspace_id, menu_path=menu_path, **kwargs)
    )
    apps_layer = await resource_getter.get_apps_layer()
    app = await resource_getter.get_app()
    await apps_layer.delete_all_menu_path_files(
        uuid=app["id"], with_shimoku_generated=with_shimoku_generated
    )


async def ai_input_file(
    workspace_id: Optional[str],
    menu_path: str = CLIFuncParam(prompt=True),
    name: str = CLIFuncParam(prompt=True),
    **kwargs,
):
    """Delete the AI input file from a menu path
    :param workspace_id: UUID of the workspace to use
    :param menu_path: Menu path id or name to use
    :param name: AI input file name to delete
    """
    resource_getter = ResourceGetter(
        InitOptions(workspace_id=workspace_id, menu_path=menu_path, **kwargs)
    )
    ai_layer = await resource_getter.get_ai_layer()
    await ai_layer.delete_input_file(file_name=name)


async def ai_model(
    workspace_id: Optional[str],
    menu_path: str = CLIFuncParam(prompt=True),
    name: str = CLIFuncParam(prompt=True),
    **kwargs,
):
    """Delete the AI model from a menu path
    :param workspace_id: UUID of the workspace to use
    :param menu_path: Menu path id or name to use
    :param name: AI model name to delete
    """
    resource_getter = ResourceGetter(
        InitOptions(workspace_id=workspace_id, menu_path=menu_path, **kwargs)
    )
    ai_layer = await resource_getter.get_ai_layer()
    await ai_layer.delete_model(model_name=name)


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

    if not role_obj:
        logger.info(f"Role {role} not found")
        return
    if menu_path:
        layer = await resource_getter.get_apps_layer()
        resource_id = (await resource_getter.get_app())["id"]
    elif board:
        layer = await resource_getter.get_dashboards_layer()
        resource_id = (await resource_getter.get_dashboard())["id"]
    else:
        layer = await resource_getter.get_businesses_layer()
        resource_id = (await resource_getter.get_business())["id"]

    await layer.delete_role(uuid=resource_id, role_name=role_obj["role"])


if __name__ == "__main__":
    add_delete_parser().parse_args()
