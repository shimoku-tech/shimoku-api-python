from typing import Optional
from shimoku.cli import CLIParser, CLIFuncParam
from shimoku.cli.cloud.cascade_get_resources import ResourceGetter, InitOptions
from shimoku.cli.utils import choose_from_menu

from shimoku.exceptions import ActionError
from shimoku.execution_logger import configure_logging, log_error

import logging

logger = logging.getLogger(__name__)


def add_update_parser(parser: Optional[CLIParser] = None):
    """
    Function to add the update parser to a parser
    :param parser: Parser to add the update parser to
    :return: Update parser
    """
    params = {"name": "update", "description": "Commands to update existing resources"}
    if parser:
        update_parser = parser.add_command(**params)
    else:
        update_parser = CLIParser(**params)

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

    module_functions = [action, workspace, menu_path, menu_order, board, boards_order]

    for func in module_functions:
        update_parser.decor_add_command(common_args=common_args)(func)

    return update_parser


if __name__ == "__main__":
    add_update_parser().parse_args()


async def action(
    action: str = CLIFuncParam(prompt=True),
    new_name: str = CLIFuncParam(mandatory=False),
    new_description: str = CLIFuncParam(mandatory=False),
    **kwargs,
):
    """Update the properties of an action
    :param action: Name or id of the action
    :param new_name: New name for the action
    :param new_description: New description for the action
    """
    resource_getter = ResourceGetter(InitOptions(action=action, **kwargs))
    actions_layer = await resource_getter.get_actions_layer()
    action = await resource_getter.get_action()
    if not action:
        log_error(
            logger,
            f"Action {action} not found",
            ActionError,
        )
    await actions_layer.update_action(
        uuid=action["id"],
        new_name=new_name,
        new_description=new_description,
    )


async def workspace(
    new_name: str = CLIFuncParam(mandatory=False),
    reset_theme: bool = CLIFuncParam(
        default=False, action="store_true", mandatory=False
    ),
    **kwargs,
):
    """Update the name or reset the theme of a workspace
    :param new_name: New name for the workspace
    :param reset_theme: Flag to reset the theme of the workspace
    """
    resource_getter = ResourceGetter(InitOptions(**kwargs))
    businesses_layer = await resource_getter.get_businesses_layer()
    business_id = resource_getter.init_opts.workspace_id
    if not reset_theme:
        await businesses_layer.update_workspace(business_id, new_name=new_name)
    else:
        await businesses_layer.update_workspace(
            business_id, new_name=new_name, theme={}
        )


async def menu_order(
    change_sub_paths: bool = CLIFuncParam(
        default=False, action="store_true", mandatory=False
    ),
    **kwargs,
):
    """Update the order of menu paths
    :param change_sub_paths: Flag to change the order of the sub paths
    """
    resource_getter = ResourceGetter(InitOptions(**kwargs))
    businesses_layer = await resource_getter.get_businesses_layer()
    business = await resource_getter.get_business()

    apps_layer = await resource_getter.get_apps_layer()
    app_names = [app["name"] for app in await business.get_apps()] + [""]

    apps_order = []
    print("Choose the order of the menu paths, press enter to finish")
    previous_logging_level = logging.root.level
    if previous_logging_level == logging.INFO:
        configure_logging("WARNING")
    while True:
        next_app = choose_from_menu(app_names, "Next menu path: ")
        if next_app:
            if change_sub_paths:
                sub_paths_order = []
                sub_paths = (
                    await apps_layer.get_menu_path_sub_paths(name=next_app)
                ) + [""]
                print(
                    f"Choose the order of the sub paths in the menu path({next_app}), press enter to finish"
                )
                while True:
                    next_sub_path = choose_from_menu(sub_paths, "Next sub path: ")
                    if next_sub_path:
                        sub_paths_order.append(next_sub_path)
                    else:
                        break
                    sub_paths.remove(next_sub_path)
                    if len(sub_paths) == 1:
                        break
                apps_order.append((next_app, sub_paths_order))
            else:
                apps_order.append(next_app)
        else:
            break
        app_names.remove(next_app)
        if len(app_names) == 1:
            break
    if previous_logging_level == logging.INFO:
        configure_logging("INFO")

    await businesses_layer.change_menu_order(
        uuid=resource_getter.init_opts.workspace_id, menu_order=apps_order
    )


async def boards_order(**kwargs):
    """Update the order of the boards in a workspace"""
    resource_getter = ResourceGetter(InitOptions(**kwargs))
    businesses_layer = await resource_getter.get_businesses_layer()
    business = await resource_getter.get_business()

    dashboard_names = [d["name"] for d in await business.get_dashboards()] + [""]
    dashboards_order = []
    print("Choose the order of the dashboards in the workspace, press enter to finish")
    while True:
        next_dashboard = choose_from_menu(dashboard_names, "Next board: ")
        if next_dashboard:
            dashboards_order.append(next_dashboard)
        else:
            break
        dashboard_names.remove(next_dashboard)
        if len(dashboard_names) == 1:
            break
    await businesses_layer.change_boards_order(
        uuid=resource_getter.init_opts.workspace_id, boards=dashboards_order
    )


async def board(
    is_public: Optional[str],
    is_disabled: Optional[str],
    board: str = CLIFuncParam(prompt=True),
    new_name: str = CLIFuncParam(mandatory=False),
    order: int = CLIFuncParam(mandatory=False),
    **kwargs,
):
    """
    Update the properties of a board
    :param is_public: (true/false) Set the board as public
    :param is_disabled: (true/false) Set the board as disabled
    :param board: Name or id of the board
    :param new_name: New name for the board
    :param order: New order for the board
    """
    if is_public is not None:
        is_public = is_public.lower() == "true"
    if is_disabled is not None:
        is_disabled = is_disabled.lower() == "true"
    resource_getter = ResourceGetter(InitOptions(board=board, **kwargs))
    dashboards_layer = await resource_getter.get_dashboards_layer()
    dashboard = await resource_getter.get_dashboard()
    await dashboards_layer.update_board(
        uuid=dashboard["id"],
        new_name=new_name,
        order=order,
        is_public=is_public,
        is_disabled=is_disabled,
    )


async def menu_path(
    hide_title: Optional[str],
    hide_path: Optional[str],
    show_breadcrumb: Optional[str],
    show_history_navigation: Optional[str],
    menu_path: str = CLIFuncParam(prompt=True),
    new_name: str = CLIFuncParam(mandatory=False),
    order: int = CLIFuncParam(mandatory=False),
    **kwargs,
):
    """
    Update the properties of a menu path
    :param menu_path: Name or id of the menu path
    :param new_name: New name for the menu path
    :param order: New order for the menu path
    :param hide_title: (true/false) Hide the title of the menu path
    :param hide_path: (true/false) Hide the path of the menu path
    :param show_breadcrumb: (true/false) Show the breadcrumb of the menu path
    :param show_history_navigation: (true/false) Show the history navigation of the menu path
    """
    if hide_title is not None:
        hide_title = hide_title.lower() == "true"
    if hide_path is not None:
        hide_path = hide_path.lower() == "true"
    if show_breadcrumb is not None:
        show_breadcrumb = show_breadcrumb.lower() == "true"
    if show_history_navigation is not None:
        show_history_navigation = show_history_navigation.lower() == "true"
    resource_getter = ResourceGetter(InitOptions(menu_path=menu_path, **kwargs))
    apps_layer = await resource_getter.get_apps_layer()
    app = await resource_getter.get_app()

    await apps_layer.update_menu_path(
        uuid=app["id"],
        new_name=new_name,
        order=order,
        hide_title=hide_title,
        hide_path=hide_path,
        show_breadcrumb=show_breadcrumb,
        show_history_navigation=show_history_navigation,
    )
