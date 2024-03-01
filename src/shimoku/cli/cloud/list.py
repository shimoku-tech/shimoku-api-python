from typing import Optional

import os

from shimoku.ai.ai_layer import (
    get_model_metadata,
    check_and_get_model,
    get_output_file_metadata,
    get_activity_template,
    get_activity_from_template,
    get_runs_message,
)

from shimoku.api.resources.file import File
from shimoku.api.resources.app import App
from shimoku.api.resources.activity import Activity
from shimoku.api.resources.activity_template import ActivityTemplate

from shimoku.cli import CLIParser, CLIFuncParam
from shimoku.cli.utils import list_filtering_and_display, display_list, save_as_file
from shimoku.cli.cloud.cascade_get_resources import (
    InitOptions,
    ResourceGetter,
    Universe,
)

import logging

logger = logging.getLogger(__name__)


def add_list_parser(parser: Optional[CLIParser] = None):
    """
    Function to add the list parser to a parser
    :param parser: Parser to add the listing parser to
    :return: Listing parser
    """
    params = {"name": "list", "description": "Commands to list resources"}
    if parser:
        list_parser = parser.add_command(**params)
    else:
        list_parser = CLIParser(**params)

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
            name="count",
            arg_help="Flag to show the count of items",
            action="store_true",
            mandatory=False,
        ),
        CLIFuncParam(
            name="prefix",
            arg_type=str,
            arg_help="Prefix to filter the items",
            mandatory=False,
        ),
        CLIFuncParam(
            name="contains",
            arg_type=str,
            arg_help="String to filter the items",
            mandatory=False,
        ),
        CLIFuncParam(
            name="filter-field",
            arg_type=str,
            arg_help="Field to filter the items",
            mandatory=False,
        ),
        CLIFuncParam(
            name="sort-field",
            arg_type=str,
            arg_help="Field to sort the items",
            mandatory=False,
        ),
        CLIFuncParam(
            name="equal-to",
            arg_type=str,
            arg_help="String to match the items",
            mandatory=False,
        ),
        CLIFuncParam(
            name="not-equal-to",
            arg_type=str,
            arg_help="String to not match the items",
            mandatory=False,
        ),
        CLIFuncParam(
            name="case-sensitive",
            arg_help="Flag to set the case sensitivity of the string filters",
            action="store_true",
            mandatory=False,
        ),
    ]

    module_functions = [
        actions,
        universe_api_keys,
        activity_templates,
        workspaces,
        boards,
        menu_paths,
        components,
        sub_paths,
        data_sets,
        data,
        activities,
        runs,
        run_logs,
        files,
        ai_input_files,
        ai_functions,
        ai_function_parameters,
        ai_models,
        ai_execution_logs,
        ai_output_files,
        roles,
    ]

    for func in module_functions:
        list_parser.decor_add_command(common_args=common_args)(func)

    return list_parser


async def universe_api_keys(**kwargs):
    """List the universe api keys in the universe"""
    universe: Universe = await ResourceGetter(InitOptions(**kwargs)).get_universe()
    list_filtering_and_display(
        [u.cascade_to_dict() for u in await universe.get_universe_api_keys()],
        table_title=f"Universe api keys from Universe {universe['id']}",
        fields=["id", "description", "enabled"],
        **kwargs,
    )


async def actions(**kwargs):
    """List the actions in the universe"""
    universe: Universe = await ResourceGetter(InitOptions(**kwargs)).get_universe()
    list_filtering_and_display(
        [u.cascade_to_dict() for u in await universe.get_actions()],
        table_title=f"Actions from Universe {universe['id']}",
        fields=["id", "name", "description"],
        **kwargs,
    )


async def workspaces(
    show_theme: bool = CLIFuncParam(
        default=False, action="store_true", mandatory=False
    ),
    **kwargs,
):
    """List the workspaces in the universe
    :param show_theme: Flag to show the theme
    """
    resource_getter = ResourceGetter(InitOptions(**kwargs))
    universes_layer = await resource_getter.get_universes_layer()
    universe = await resource_getter.get_universe()
    if kwargs["filter_field"] is None:
        kwargs["filter_field"] = "name"
    if not kwargs["sort_field"] and kwargs["filter_field"] == "theme":
        kwargs["sort_field"] = "name"
    list_filtering_and_display(
        await universes_layer.get_universe_workspaces(universe["id"]),
        table_title=f"Workspaces from Universe {universe['id']}",
        fields=resource_getter.get_business_fields_to_show(show_theme),
        table_lines=False,
        **kwargs,
    )


async def activity_templates(
    show_input_settings: bool = CLIFuncParam(
        default=False, action="store_true", mandatory=False
    ),
    **kwargs,
):
    """List the activity templates in the universe
    :param show_input_settings: Flag to show the input settings
    """
    resource_getter = ResourceGetter(InitOptions(**kwargs))
    universes_layer = await resource_getter.get_universes_layer()
    universe = await resource_getter.get_universe()
    list_filtering_and_display(
        await universes_layer.get_universe_activity_templates(universe["id"]),
        table_title=f"Activity templates from Universe {universe['id']}",
        fields=resource_getter.get_activity_template_fields_to_show(
            show_input_settings
        ),
        **kwargs,
    )


async def boards(
    workspace_id: Optional[str],
    show_public_permission: bool = CLIFuncParam(
        default=False, action="store_true", mandatory=False
    ),
    show_theme: bool = CLIFuncParam(
        default=False, action="store_true", mandatory=False
    ),
    **kwargs,
):
    """List the boards in the workspace
    :param workspace_id: UUID of the workspace to use
    :param show_public_permission: Flag to show the public permission
    :param show_theme: Flag to show the theme
    """
    resource_getter = ResourceGetter(InitOptions(workspace_id=workspace_id, **kwargs))
    businesses_layer = await resource_getter.get_businesses_layer()
    business = await resource_getter.get_business()
    board_items = await businesses_layer.get_workspace_boards(business["id"])
    fields = resource_getter.get_dashboard_fields_to_show(
        show_public_permission, show_theme
    )
    if kwargs["filter_field"] is None:
        kwargs["filter_field"] = "name"
    if not kwargs["sort_field"]:
        kwargs["sort_field"] = "order"
    list_filtering_and_display(
        board_items,
        table_title=f"Boards from Workspace {str(business)}",
        fields=fields,
        **kwargs,
    )


async def menu_paths(board: Optional[str], workspace_id: Optional[str], **kwargs):
    """List the menu paths in the board
    :param board: Board id or name to use
    :param workspace_id: UUID of the workspace to use
    """
    resource_getter = ResourceGetter(
        InitOptions(workspace_id=workspace_id, board=board, **kwargs)
    )
    business_layer = await resource_getter.get_businesses_layer()
    business = await resource_getter.get_business()
    board_obj = None
    if board:
        board_obj = await resource_getter.get_dashboard()
    fields = resource_getter.get_app_fields_to_show()
    if kwargs["filter_field"] is None:
        kwargs["filter_field"] = "name"
    if not kwargs["sort_field"]:
        kwargs["sort_field"] = "order"
    menu_path_objs = await business_layer.get_workspace_menu_paths(business["id"])
    if board_obj:
        board_menu_path_ids = await board_obj.list_app_ids()
        menu_path_objs = [
            menu_path
            for menu_path in menu_path_objs
            if menu_path["id"] in board_menu_path_ids
        ]
    list_filtering_and_display(
        menu_path_objs,
        table_title=f"Menu paths from Workspace {str(business)}"
        if not board_obj
        else f"Menu paths from Board {str(board_obj)}",
        fields=fields,
        **kwargs,
    )


async def data_sets(
    workspace_id: Optional[str], menu_path: str = CLIFuncParam(prompt=True), **kwargs
):
    """List the data sets in the menu path
    :param workspace_id: UUID of the workspace to use
    :param menu_path: Menu path id or name to use
    """
    resource_getter = ResourceGetter(
        InitOptions(workspace_id=workspace_id, menu_path=menu_path, **kwargs)
    )
    apps_layer = await resource_getter.get_apps_layer()
    app = await resource_getter.get_app()
    fields = resource_getter.get_data_set_fields_to_show()
    if kwargs["filter_field"] is None:
        kwargs["filter_field"] = "name"
    list_filtering_and_display(
        await apps_layer.get_menu_path_data_sets(app["id"]),
        table_title=f"Data sets from Menu path {str(app)}",
        table_lines=False,
        fields=fields,
        **kwargs,
    )


async def components(
    workspace_id: Optional[str],
    sub_path: Optional[str],
    menu_path: str = CLIFuncParam(prompt=True),
    show_all_fields: bool = CLIFuncParam(
        default=False, action="store_true", mandatory=False
    ),
    **kwargs,
):
    """List the components in the menu path
    :param workspace_id: UUID of the workspace to use
    :param menu_path: Menu path id or name to use
    :param show_all_fields: Flag to show all the fields
    :param sub_path: Sub path to filter the components
    """
    resource_getter = ResourceGetter(
        InitOptions(workspace_id=workspace_id, menu_path=menu_path, **kwargs)
    )
    apps_layer = await resource_getter.get_apps_layer()
    app = await resource_getter.get_app()
    fields = resource_getter.get_report_fields_to_show(show_all_fields=show_all_fields)
    reports = await apps_layer.get_menu_path_components(app["id"])
    if sub_path:
        reports = [report for report in reports if report["path"] == sub_path]
        fields.pop(fields.index("path"))
        fields.pop(fields.index("pathOrder"))
    if kwargs["filter_field"] is None:
        kwargs["filter_field"] = "reportType"
    if not kwargs["sort_field"]:
        kwargs["sort_field"] = "pathOrder"
    list_filtering_and_display(
        reports,
        table_title=f"Components from menu path ({str(app)+(f'/{sub_path}' if sub_path else '')})",
        fields=fields,
        table_lines=show_all_fields,
        **kwargs,
    )


async def sub_paths(
    workspace_id: Optional[str], menu_path: str = CLIFuncParam(prompt=True), **kwargs
):
    """List the sub paths in the menu path
    :param workspace_id: UUID of the workspace to use
    :param menu_path: Menu path id or name to use
    """
    resource_getter = ResourceGetter(
        InitOptions(workspace_id=workspace_id, menu_path=menu_path, **kwargs)
    )
    apps_layer = await resource_getter.get_apps_layer()
    app = await resource_getter.get_app()
    display_list(
        f"Sub paths from Menu path {str(app)}",
        await apps_layer.get_menu_path_sub_paths(app["id"]),
    )


async def data(
    workspace_id: Optional[str],
    menu_path: str = CLIFuncParam(prompt=True),
    data_set: str = CLIFuncParam(prompt=True),
    limit: int = CLIFuncParam(default=100, mandatory=False),
    **kwargs,
):
    """List the data in the data set
    :param workspace_id: UUID of the workspace to use
    :param menu_path: Menu path id or name to use
    :param data_set: Data set id or name to use
    :param limit: Limit the number of results returned, negative or zero to show all
    """
    resource_getter = ResourceGetter(
        InitOptions(
            workspace_id=workspace_id, menu_path=menu_path, data_set=data_set, **kwargs
        )
    )
    data_sets_layer = await resource_getter.get_data_sets_layer()
    data_set = await resource_getter.get_data_set()
    data = await data_sets_layer.get_data_from_data_set(
        data_set["id"], limit=limit if limit > 0 else None
    )
    show_custom_field = "customField1" in data[0] if data else False
    fields = resource_getter.get_data_fields_to_show(show_custom_field)
    list_filtering_and_display(
        data,
        table_title=f"Data from Data set ({str(data_set)})",
        fields=fields,
        table_lines=False,
        **kwargs,
    )


async def activities(
    workspace_id: Optional[str],
    menu_path: str = CLIFuncParam(prompt=True),
    show_templates: bool = CLIFuncParam(
        default=False, action="store_true", mandatory=False
    ),
    **kwargs,
):
    """List the activities in the menu path
    :param workspace_id: UUID of the workspace to use
    :param menu_path: Menu path id or name to use
    :param show_templates: Flag to show the templates
    """
    resource_getter = ResourceGetter(
        InitOptions(workspace_id=workspace_id, menu_path=menu_path, **kwargs)
    )
    apps_layer = await resource_getter.get_apps_layer()
    app = await resource_getter.get_app()
    fields = resource_getter.get_activity_fields_to_show(show_templates)
    if kwargs["filter_field"] is None:
        kwargs["filter_field"] = "name"
    list_filtering_and_display(
        await apps_layer.get_menu_path_activities(app["id"]),
        table_title=f"Activities from Menu path {str(app)}",
        fields=fields,
        **kwargs,
    )


async def runs(
    workspace_id: Optional[str],
    menu_path: str = CLIFuncParam(prompt=True),
    activity: str = CLIFuncParam(prompt=True),
    **kwargs,
):
    """List the runs of an activity
    :param workspace_id: UUID of the workspace to use
    :param menu_path: Menu path id or name to use
    :param activity: Activity id or name to use
    """
    resource_getter = ResourceGetter(
        InitOptions(
            workspace_id=workspace_id, menu_path=menu_path, activity=activity, **kwargs
        )
    )
    activity = await resource_getter.get_activity()
    runs_objs = await activity.get_runs()
    list_filtering_and_display(
        [run.cascade_to_dict() for run in runs_objs],
        table_title=f"Runs from Activity {str(activity)}",
        **kwargs,
    )


async def run_logs(
    workspace_id: Optional[str],
    menu_path: str = CLIFuncParam(prompt=True),
    activity: str = CLIFuncParam(prompt=True),
    run_id: str = CLIFuncParam(prompt=True),
    **kwargs,
):
    """List the logs of a run
    :param workspace_id: UUID of the workspace to use
    :param menu_path: Menu path id or name to use
    :param activity: Activity id or name to use
    :param run_id: Run id to use
    """
    resource_getter = ResourceGetter(
        InitOptions(
            workspace_id=workspace_id,
            menu_path=menu_path,
            activity=activity,
            run_id=run_id,
            **kwargs,
        )
    )
    activity = await resource_getter.get_activity()
    run = await activity.get_run(run_id)
    list_filtering_and_display(
        run["logs"], table_title=f"Logs from Run {run_id}", **kwargs
    )


async def files(
    workspace_id: Optional[str],
    menu_path: str = CLIFuncParam(prompt=True),
    with_shimoku_generated: bool = CLIFuncParam(
        default=False, action="store_true", mandatory=False
    ),
    **kwargs,
):
    """List the files in the menu path
    :param workspace_id: UUID of the workspace to use
    :param menu_path: Menu path id or name to use
    :param with_shimoku_generated: Flag to show the shimoku generated files
    """
    resource_getter = ResourceGetter(
        InitOptions(workspace_id=workspace_id, menu_path=menu_path, **kwargs)
    )
    apps_layer = await resource_getter.get_apps_layer()
    app = await resource_getter.get_app()
    fields = resource_getter.get_file_fields_to_show()
    if kwargs["filter_field"] is None:
        kwargs["filter_field"] = "name"
    list_filtering_and_display(
        await apps_layer.get_menu_path_files(
            app["id"], with_shimoku_generated=with_shimoku_generated
        ),
        table_title=f"Files from Menu path {str(app)}",
        fields=fields,
        **kwargs,
    )


async def roles(
    workspace_id: Optional[str],
    menu_path: str = CLIFuncParam(group="menu_path_or_board", mandatory=False),
    board: str = CLIFuncParam(group="menu_path_or_board", mandatory=False),
    **kwargs,
):
    """List the roles in the menu path, board or workspace. If menu path is specified, it will list the roles in the
    menu path. If board is specified, it will list the roles in the board. If none is specified, it will list the roles
    in the workspace. Don't specify both menu path and board.
    :param workspace_id: UUID of the workspace to use
    :param menu_path: Menu path id or name to use
    :param board: Board id or name to use
    """
    resource_getter = ResourceGetter(
        InitOptions(
            workspace_id=workspace_id, menu_path=menu_path, board=board, **kwargs
        )
    )

    if menu_path:
        app = await resource_getter.get_app()
        title = f"Roles from Menu path {str(app)}"
    elif board:
        dashboard = await resource_getter.get_dashboard()
        title = f"Roles from Board {str(dashboard)}"
    else:
        business = await resource_getter.get_business()
        title = f"Roles from Workspace {str(business)}"

    list_filtering_and_display(
        await resource_getter.get_role_dicts(), table_title=title, **kwargs
    )


# AI functions


async def ai_input_files(
    workspace_id: Optional[str], menu_path: str = CLIFuncParam(prompt=True), **kwargs
):
    """List the AI input files in the menu path
    :param workspace_id: UUID of the workspace to use
    :param menu_path: Menu path id or name to use
    """
    ai_layer = await ResourceGetter(
        InitOptions(workspace_id=workspace_id, menu_path=menu_path, **kwargs)
    ).get_ai_layer()
    message = [
        "",
        "///////////////////////////////////////////////////",
        "///////////////// Available Files /////////////////",
    ]
    input_files = await ai_layer.get_available_input_files()
    for file in input_files:
        metadata = {k: v for k, v in file.items() if k not in ["file_name"]}
        message.extend(
            [
                "",
                f" \033[1m- File name:\033[0m {file['file_name']}",
            ]
        )
        if metadata:
            message.extend(
                [
                    "   \033[1mMetadata:\033[0m",
                    *[f"     \033[1m- {k}:\033[0m {v}" for k, v in metadata.items()],
                ]
            )

    message.extend(["", "///////////////////////////////////////////////////", ""])
    print("\n".join(message))


def add_input_params_to_message(params: dict[str, dict]):
    """Add the parameters to a message
    :param params: Parameters to add
    """
    message = []
    for param_name, param in params.items():
        message.append(
            f"\033[1m- {param_name}"
            f"{' (Optional)' if not param['mandatory'] else ''}:\033[0m {param['datatype']}"
        )
        if param["description"]:
            message.append(f"  {param['description']}")
    return message


def add_args_and_files_to_message(input_settings: dict[str, dict]) -> list[str]:
    """Add the args and files to a message
    :param input_settings: Input settings of the ai_function
    """
    message = []
    input_files = {
        key: param
        for key, param in input_settings.items()
        if isinstance(param, dict) and param["datatype"] == "file"
    }
    input_args = {
        key: param
        for key, param in input_settings.items()
        if isinstance(param, dict) and param["datatype"] != "file"
    }
    message.append("--- args ---")
    message.extend(["  " + line for line in add_input_params_to_message(input_args)])
    message.append("--- files ---")
    message.extend(["  " + line for line in add_input_params_to_message(input_files)])
    return message


async def ai_functions(
    show_input_parameters: bool = CLIFuncParam(
        default=False, action="store_true", mandatory=False
    ),
    **kwargs,
):
    """Show the available ai_functions
    :param show_input_parameters: Show the input parameters of each ai_function
    """
    universe = await ResourceGetter(InitOptions(**kwargs)).get_universe()
    message = [
        "",
        "///////////////////////////////////////////////////",
        "/////////////// Available ai_functions ///////////////",
    ]
    templates = await universe.get_activity_templates()
    while len(templates) > 0:
        template = templates.pop(0)
        if not template["enabled"]:
            continue
        versions = [template["version"]]
        while len(templates) > 0 and templates[0]["name"] == template["name"]:
            template = templates.pop(0)
            versions.append(template["version"])
        message.append("")
        message.append(
            f" \033[1m- AI function:\033[0m {template['name']} (v{', v'.join(versions)})"
        )
        message.append(
            f"   \033[1mDescription:\033[0m {template['description']} "
            f"(wait time between runs: >{template['minRunInterval']}s)"
        )
        if show_input_parameters:
            message.append("   \033[1mInput parameters:\033[0m")
            message.extend(
                [
                    "     " + line
                    for line in add_args_and_files_to_message(template["inputSettings"])
                ]
            )

    message.extend(["", "///////////////////////////////////////////////////", ""])
    print("\n".join(message))


async def ai_function_parameters(
    ai_function: str = CLIFuncParam(prompt=True), **kwargs
):
    """Show the parameters of a ai_function
    :param ai_function: Name of the ai_function
    """
    universe = await ResourceGetter(InitOptions(**kwargs)).get_universe()
    activity_templates = await universe.get_activity_templates()
    template = [
        template for template in activity_templates if template["name"] == ai_function
    ][-1]
    message = [
        "",
        "///////////////////////////////////////////////////",
        f" {ai_function} parameters ".center(51, "/"),
        "",
        f"  \033[1mDescription:\033[0m {template['description']} "
        f"(wait time between runs: >{template['minRunInterval']}s)",
        "  \033[1mInput parameters:\033[0m",
    ]
    message.extend(
        [
            "    " + line
            for line in add_args_and_files_to_message(template["inputSettings"])
        ]
    )

    message.extend(["", "///////////////////////////////////////////////////", ""])
    print("\n".join(message))


async def ai_models(
    workspace_id: Optional[str], menu_path: str = CLIFuncParam(prompt=True), **kwargs
):
    """Show the available models
    :param workspace_id: UUID of the workspace to use
    :param menu_path: Menu path id or name to use
    """
    message = [
        "",
        "///////////////////////////////////////////////////",
        "//////////////// Available models /////////////////",
    ]
    resource_getter = ResourceGetter(
        InitOptions(workspace_id=workspace_id, menu_path=menu_path, **kwargs)
    )
    app = await resource_getter.get_app()
    app_files: list[File] = await app.get_files()
    model_files = [
        file
        for file in app_files
        if "shimoku_generated" in file["tags"] and "ai_model" in file["tags"]
    ]
    model_files = sorted(model_files, key=lambda file: file["metadata"]["model_name"])
    for file in model_files:
        message.extend(
            [
                "",
                f" \033[1m- Model name:\033[0m {file['metadata']['model_name']}",
                "   \033[1mMetadata:\033[0m",
            ]
        )
        for key, value in get_model_metadata(file).items():
            if key in ["model_name", "creator_ai_function_version"]:
                continue
            message.append(f"     \033[1m- {key}:\033[0m {value}")

    message.extend(["", "///////////////////////////////////////////////////", ""])
    print("\n".join(message))


async def ai_execution_logs(
    workspace_id: Optional[str],
    menu_path: str = CLIFuncParam(prompt=True),
    ai_function: str = CLIFuncParam(prompt=True),
    version: str = CLIFuncParam(mandatory=False),
    run_id: str = CLIFuncParam(group="filtering", mandatory=False),
    model_name: str = CLIFuncParam(group="filtering", mandatory=False),
    how_many: int = CLIFuncParam(default=1, mandatory=False),
    **kwargs,
):
    """Show the logs of the executions of a ai_function
    :param workspace_id: UUID of the workspace to use
    :param menu_path: Menu path id or name to use
    :param ai_function: Name of the ai_function to execute
    :param version: Version of the ai_function to execute
    :param run_id: Id of the run to get the logs from
    :param model_name: Name of the model to get the logs from
    :param how_many: Number of executions to get
    """

    async def show_last_execution_logs_by_model(
        _app: App,
    ):
        app_files: list[File] = await _app.get_files()
        model_file: File = await check_and_get_model(_app, model_name)
        model_metadata: dict = get_model_metadata(model_file)
        runs: list[Activity.Run] = []
        input_settings_by_run_id: dict[str, dict] = {}
        for file in app_files:
            if (
                "shimoku_generated" not in file["tags"]
                or "ai_output_file" not in file["tags"]
            ):
                continue
            output_file_metadata: dict = get_output_file_metadata(file)
            output_file_model_name = (
                output_file_metadata.pop("model_name") if model_metadata else None
            )
            if output_file_model_name == model_name:
                activity_template: ActivityTemplate = await get_activity_template(
                    _app.parent.parent,
                    output_file_metadata["creator_ai_function"],
                    output_file_metadata["creator_ai_function_version"],
                )
                activity: Activity = await get_activity_from_template(
                    _app, activity_template, create_if_not_exists=False
                )
                run_id = output_file_metadata["run_id"]
                input_settings = activity_template["inputSettings"]
                runs.append(await activity.get_run(run_id))
                input_settings_by_run_id[run_id] = input_settings
        runs = (await Activity.sort_runs_by_log_time(runs))[-how_many:]
        message = [
            "",
            "///////////////////////////////////////////////////",
            f" LOGS OF EXECUTIONS BY {model_name.upper()} ".center(51, "/"),
        ]
        input_settings_list = [input_settings_by_run_id[run["id"]] for run in runs]
        message.extend(await get_runs_message(runs, input_settings_list))
        print("\n".join(message))

    async def show_last_execution_logs_by_ai_function(
        _app: App,
    ):
        activity_template: ActivityTemplate = await get_activity_template(
            _app.parent.parent, ai_function, version
        )
        input_settings = activity_template["inputSettings"]
        activity: Activity = await get_activity_from_template(
            _app, activity_template, create_if_not_exists=False
        )
        runs: list[Activity.Run] = await activity.get_runs(how_many)
        if run_id:
            runs = [run for run in runs if run["id"] == run_id]
        message = [
            "",
            "///////////////////////////////////////////////////",
            f" LOGS OF {ai_function.upper()} ".center(51, "/"),
        ]
        message.extend(await get_runs_message(runs, input_settings))
        print("\n".join(message))

    resource_getter = ResourceGetter(
        InitOptions(workspace_id=workspace_id, menu_path=menu_path, **kwargs)
    )
    app = await resource_getter.get_app()
    if model_name:
        await show_last_execution_logs_by_model(app)
    else:
        await show_last_execution_logs_by_ai_function(app)


async def ai_output_files(
    workspace_id: Optional[str],
    menu_path: str = CLIFuncParam(prompt=True),
    ai_function: str = CLIFuncParam(mandatory=False),
    version: str = CLIFuncParam(mandatory=False),
    model_name: str = CLIFuncParam(mandatory=False),
    file_name: str = CLIFuncParam(mandatory=False),
    save_to_path: str = CLIFuncParam(mandatory=False),
    **kwargs,
):
    """Show the output file of the execution of a ai_function
    :param workspace_id: UUID of the workspace to use
    :param menu_path: Menu path id or name to use
    :param ai_function: Name of the ai_function to execute
    :param version: Version of the ai_function to execute
    :param model_name: Name of the model to get the logs from
    :param file_name: Name of the file to get
    :param save_to_path: Path to store the file objects, leave empty to not download the files content
    """
    resource_getter = ResourceGetter(
        InitOptions(workspace_id=workspace_id, menu_path=menu_path, **kwargs)
    )
    ai_layer = await resource_getter.get_ai_layer()
    files_dict = []
    if ai_function:
        files_dict.extend(
            await ai_layer.get_output_files_by_ai_function(
                ai_function, version, file_name, get_objects=str(save_to_path) != ""
            )
        )
    elif model_name:
        files_dict.extend(
            await ai_layer.get_output_files_by_model(
                model_name, file_name, get_objects=str(save_to_path) != ""
            )
        )
    else:
        raise ValueError("You must specify either the ai_function or the model_name")
    if save_to_path:
        for run in files_dict:
            file_dir = os.path.join(save_to_path, run["id"])
            for file_name, file_obj in run["files"]:
                save_as_file(logger, file_dir, file_obj, file_name)
    list_filtering_and_display(
        files_dict,
        table_title=f"Output files from {ai_function or model_name}",
        **kwargs,
    )


if __name__ == "__main__":
    add_list_parser().parse_args()
