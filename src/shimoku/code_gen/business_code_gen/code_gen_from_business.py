import tqdm
from typing import Optional, List

from shimoku.api.resources.business import Business

from shimoku.utils import create_function_name, create_normalized_name

from shimoku.code_gen.file_generator import CodeGenFileHandler
from shimoku.code_gen.business_code_gen.apps_code_gen.code_gen_from_apps import (
    AppCodeGen,
)
from shimoku.code_gen.utils_code_gen import code_gen_from_list, code_gen_from_dict

from shimoku.execution_logger import ClassWithLogging
import logging

logger = logging.getLogger(__name__)


class BusinessCodeGen(ClassWithLogging):
    _module_logger = logger

    def __init__(self, business: Business, output_path: str):
        self._business = business
        self._output_path = f'{output_path}/{create_function_name(business["name"])}'
        self._file_generator = CodeGenFileHandler(self._output_path)

    async def generate_code(
        self, business_id: str, menu_paths: List[str], pbar: Optional[tqdm.tqdm] = None
    ):
        """Use the resources in the API to generate code_lines for the SDK. Create a file in
        the specified path with the generated code_lines.
        :param business_id: business id to use
        :param menu_paths: list of menu paths to generate code for
        :param pbar: progress bar to use
        """
        import_code_lines: List[str] = [
            "from shimoku import Client",
        ]
        main_code_lines: List[str] = [
            f'shimoku_client.set_workspace("{business_id}")',
            "",
        ]

        if self._business["theme"]:
            theme_code_lines = code_gen_from_dict(self._business["theme"], deep=4)
            main_code_lines.extend(
                [
                    f'shimoku_client.workspaces.update_workspace("{business_id}", theme={theme_code_lines[0][4:]})',
                    *theme_code_lines[1:],
                    "",
                ]
            )

        if menu_paths:
            menu_paths = [create_normalized_name(menu_path) for menu_path in menu_paths]
        apps = [
            app
            for app in sorted(await self._business.get_apps(), key=lambda x: x["order"])
            if menu_paths is None or app["normalizedName"] in menu_paths
        ]

        extra_apps_for_dashboard = {}
        last_dashboard = None
        dashboards = sorted(
            await self._business.get_dashboards(), key=lambda x: x["order"]
        )
        created_dashboards = []
        for app in apps:
            app_id = app["id"]
            app_code_gen = AppCodeGen(app, self._output_path, pbar=pbar)

            await app_code_gen.generate_code()

            import_code_lines.append(
                f"from .{app_code_gen.app_f_name}.app import {app_code_gen.app_f_name}"
            )
            aux_code_lines = []
            try:
                first_dashboard, *extra_dashboards = [
                    dashboard
                    for dashboard in dashboards
                    if app_id in await dashboard.list_app_ids()
                ]
            except IndexError:
                self._module_logger.warning(f'App {app["name"]} has no dashboards')
                continue
            created_dashboards.append(first_dashboard)
            if first_dashboard["name"] != last_dashboard:
                aux_code_lines.append(
                    f'shimoku_client.set_board("{first_dashboard["name"]}")'
                )
                last_dashboard = first_dashboard["name"]
            for dashboard in extra_dashboards:
                extra_apps_for_dashboard.setdefault(dashboard["name"], []).append(
                    app["name"]
                )

            aux_code_lines.append(f"{app_code_gen.app_f_name}(shimoku_client)")
            main_code_lines.extend(aux_code_lines)

        for dashboard_name, app_names in extra_apps_for_dashboard.items():
            app_names_code_lines = code_gen_from_list(app_names, deep=4)
            main_code_lines.extend(
                [
                    "",
                    "shimoku_client.boards.group_menu_paths("
                    '    name="' + dashboard_name + '",',
                    f"    menu_path_names={app_names_code_lines[0][4:]}",
                    *app_names_code_lines[1:],
                    ")",
                ]
            )

        if created_dashboards != dashboards:
            dashboards_code_lines = code_gen_from_list(
                [dashboard["name"] for dashboard in dashboards], deep=4
            )
            main_code_lines.extend(
                [
                    "",
                    "shimoku_client.workspaces.change_boards_order(",
                    f'   uuid="{business_id}",',
                    f"   boards={dashboards_code_lines[0][4:]}",
                    *dashboards_code_lines[1:],
                    ")",
                ]
            )

        business_name = create_function_name(self._business["name"])
        self._file_generator.generate_script_file(
            f"workspace_{business_name}",
            [
                *import_code_lines,
                "",
                "",
                f"def workspace_{business_name}(shimoku_client: Client):",
                *["    " + line for line in main_code_lines],
                "",
            ],
        )
        # Create an __init__.py file for the imports to work
        self._file_generator.generate_script_file("__init__", [""])
