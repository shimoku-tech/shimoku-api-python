from typing import Optional
from os import getenv
from dataclasses import dataclass
import asyncio
from shimoku.cli.utils import get_profile_config
from shimoku.exceptions import (
    WorkspaceError,
    BoardError,
    MenuPathError,
    FileError,
    ActivityTemplateError,
    ActivityError,
    RoleError,
)
from shimoku.execution_logger import log_error
from shimoku.api.client import ApiClient
from shimoku.api.resources.universe import Universe
from shimoku.api.resources.business import Business
from shimoku.api.resources.dashboard import Dashboard
from shimoku.api.resources.activity_template import ActivityTemplate
from shimoku.api.resources.app import App
from shimoku.api.resources.activity import Activity
from shimoku.api.resources.file import File
from shimoku.api.resources.data_set import DataSet
from shimoku.api.resources.report import Report
from shimoku.api.resources.action import Action

from shimoku.api.user_access_classes.universes_layer import UniversesLayer
from shimoku.api.user_access_classes.actions_layer import ActionsLayer
from shimoku.api.user_access_classes.businesses_layer import WorkspacesLayer
from shimoku.api.user_access_classes.dashboards_layer import BoardsLayer
from shimoku.api.user_access_classes.apps_layer import MenuPathsLayer
from shimoku.api.user_access_classes.files_layer import FilesLayer
from shimoku.api.user_access_classes.activity_templates_layer import (
    ActivityTemplatesLayer,
)
from shimoku.api.user_access_classes.activities_layer import ActivitiesLayer
from shimoku.api.user_access_classes.data_sets_layer import DataSetsLayer
from shimoku.api.user_access_classes.reports_layer import ComponentsLayer

from shimoku.ai.ai_layer import AILayer
import logging

logger = logging.getLogger(__name__)


@dataclass
class InitOptions:
    KEY_MAP = {
        "environment": "ENVIRONMENT",
        "access_token": "ACCESS_TOKEN",
        "universe_id": "UNIVERSE_ID",
        "workspace_id": "WORKSPACE_ID",
    }

    access_token: Optional[str] = getenv("SHIMOKU_ACCESS_TOKEN")
    environment: Optional[str] = getenv("SHIMOKU_ENVIRONMENT")
    universe_id: Optional[str] = getenv("SHIMOKU_UNIVERSE_ID")
    workspace_id: Optional[str] = getenv("SHIMOKU_WORKSPACE_ID")
    action: Optional[str] = None
    board: Optional[str] = None
    menu_path: Optional[str] = None
    role: Optional[str] = None
    activity: Optional[str] = None
    file: Optional[str] = None
    component_id: Optional[str] = None
    data_set: Optional[str] = None
    local_port: int = getenv("SHIMOKU_PLAYGROUND_PORT") or 8000

    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            self.set_value(key, value)

    def set_value(self, name: str, value: any):
        if value:
            setattr(self, name, value)

    def __getattribute__(self, item):
        attr = object.__getattribute__(self, item)
        if attr is None and item in InitOptions.KEY_MAP:
            config = get_profile_config()
            attr = config.get(InitOptions.KEY_MAP[item])
        return attr


class ResourceGetter:
    def __init__(self, init_opts: InitOptions):
        self.init_opts = init_opts
        self.universe: Optional[Universe] = None

    @staticmethod
    def get_resource_by_name_or_uuid(
        resource_list: list,
        reference: str,
        name_field: str = "name",
    ):
        return next(
            (
                resource
                for resource in resource_list
                if resource[name_field] == reference or resource["id"] == reference
            ),
            None,
        )

    async def get_api_client(self) -> ApiClient:
        api_client = ApiClient(
            environment=self.init_opts.environment,
            playground=self.init_opts.universe_id == "local",
            config={"access_token": self.init_opts.access_token},
            server_port=self.init_opts.local_port,
            retry_attempts=1,
        )
        api_client.semaphore = asyncio.Semaphore(
            api_client.semaphore_limit
        )  # need async for semaphore
        return api_client

    async def get_universes_layer(self) -> UniversesLayer:
        api_client: ApiClient = await self.get_api_client()
        return UniversesLayer(api_client=api_client)

    async def get_universe(self) -> Universe:
        if self.universe:
            return self.universe
        api_client: ApiClient = await self.get_api_client()
        api_client.semaphore = asyncio.Semaphore(api_client.semaphore_limit)
        return Universe(api_client, self.init_opts.universe_id)

    async def get_actions_layer(self) -> ActionsLayer:
        universe: Universe = await self.get_universe()
        return ActionsLayer(universe=universe)

    async def get_action(self) -> Action:
        universe: Universe = await self.get_universe()
        action_ref: Optional[str] = self.init_opts.action
        if not action_ref:
            log_error(logger, "Action not specified", ActivityTemplateError)
        action: Optional[Action] = self.get_resource_by_name_or_uuid(
            await universe.get_actions(), action_ref
        )
        if not action:
            log_error(logger, f"Action {action_ref} not found", ActivityTemplateError)
        return action

    async def get_activity_templates_layer(self) -> ActivityTemplatesLayer:
        universe: Universe = await self.get_universe()
        return ActivityTemplatesLayer(universe=universe)

    async def get_activity_template(self) -> ActivityTemplate:
        universe: Universe = await self.get_universe()
        activity_template_ref: Optional[str] = self.init_opts.activity_template
        if not activity_template_ref:
            log_error(logger, "Activity template not specified", ActivityTemplateError)
        activity_template: Optional[
            ActivityTemplate
        ] = self.get_resource_by_name_or_uuid(
            await universe.get_activity_templates(), activity_template_ref
        )
        if not activity_template:
            log_error(
                logger,
                f"Activity template {activity_template_ref} not found",
                ActivityTemplateError,
            )
        return activity_template

    @staticmethod
    def get_activity_template_fields_to_show(show_input_settings: bool) -> list[str]:
        fields = ["id", "name", "version"]
        if show_input_settings:
            fields.append("input_settings")
        return fields

    async def get_businesses_layer(self) -> WorkspacesLayer:
        universe: Universe = await self.get_universe()
        return WorkspacesLayer(universe=universe)

    async def get_business(self) -> Business:
        universe: Universe = await self.get_universe()
        business_id = self.init_opts.workspace_id
        if not business_id:
            log_error(logger, "Workspace not specified", WorkspaceError)
        business: Optional[Business] = await universe.get_business(business_id)
        if not business:
            log_error(logger, f"Workspace {business_id} not found", WorkspaceError)
        return business

    @staticmethod
    def get_business_fields_to_show(show_theme: bool) -> list[str]:
        fields = ["id", "name"]
        if show_theme:
            fields.append("theme")
        return fields

    async def get_dashboards_layer(self) -> BoardsLayer:
        business: Business = await self.get_business()
        return BoardsLayer(business=business)

    async def get_dashboard(self) -> Dashboard:
        business: Business = await self.get_business()
        dashboard_ref: Optional[str] = self.init_opts.board
        if not dashboard_ref:
            log_error(logger, "Board not specified", BoardError)
        dashboard: Optional[Dashboard] = self.get_resource_by_name_or_uuid(
            await business.get_dashboards(), dashboard_ref
        )
        if not dashboard:
            log_error(logger, f"Board {dashboard_ref} not found", BoardError)
        return dashboard

    @staticmethod
    def get_dashboard_fields_to_show(
        show_public_permission: bool, show_theme: bool
    ) -> list[str]:
        fields = ["id", "name", "order"]
        if show_public_permission:
            fields.append("publicPermission")
        if show_theme:
            fields.append("theme")
        return fields

    async def get_apps_layer(self) -> MenuPathsLayer:
        business: Business = await self.get_business()
        return MenuPathsLayer(business=business)

    async def get_app(self, app_ref: Optional[str] = None) -> App:
        business: Business = await self.get_business()
        app_ref: Optional[str] = app_ref or self.init_opts.menu_path
        if not app_ref:
            log_error(logger, "Menu path not specified", MenuPathError)
        app: Optional[App] = self.get_resource_by_name_or_uuid(
            await business.get_apps(), app_ref
        )
        if not app:
            log_error(logger, f"Menu path {app_ref} not found", MenuPathError)
        return app

    @staticmethod
    def get_app_fields_to_show() -> list[str]:
        return [
            "id",
            "name",
            "normalizedName",
            "order",
            "hideTitle",
            "hidePath",
            "showBreadcrumb",
            "showHistoryNavigation",
        ]

    async def get_reports_layer(self) -> ComponentsLayer:
        app: App = await self.get_app()
        return ComponentsLayer(app=app)

    async def get_report(self) -> Report:
        app: App = await self.get_app()
        return await app.get_report(uuid=self.init_opts.component_id)

    @staticmethod
    def get_report_fields_to_show(show_all_fields: bool = False) -> list[str]:
        fields = [
            "id",
            "title",
            "path",
            "pathOrder",
            "reportType",
            "order",
            "sizeColumns",
            "sizeRows",
            "sizePadding",
        ]
        if show_all_fields:
            fields.extend(
                ["bentobox", "properties", "dataFields", "chartData", "smartFilters"]
            )
        return fields

    async def get_data_sets_layer(self) -> DataSetsLayer:
        app: App = await self.get_app()
        return DataSetsLayer(app=app)

    async def get_data_set(self) -> DataSet:
        app: App = await self.get_app()
        data_set_ref: Optional[str] = self.init_opts.data_set
        if not data_set_ref:
            log_error(logger, "Data set not specified", ActivityError)
        data_set: Optional[DataSet] = self.get_resource_by_name_or_uuid(
            await app.get_data_sets(), data_set_ref
        )
        if not data_set:
            log_error(logger, f"Data set ({data_set_ref}) not found", ActivityError)
        return data_set

    @staticmethod
    def get_data_set_fields_to_show() -> list[str]:
        return ["id", "name"]

    @staticmethod
    def get_data_fields_to_show(show_custom_field: bool) -> list[str]:
        fields = ["orderField1", "description"]
        for i in range(1, 6):
            fields.append(f"dateField{i}")
        for i in range(1, 51):
            fields.append(f"stringField{i}")
            fields.append(f"intField{i}")
        if show_custom_field:
            fields.append("customField1")
        return fields

    async def get_activities_layer(self) -> ActivitiesLayer:
        app: App = await self.get_app()
        return ActivitiesLayer(app=app)

    async def get_activity(self) -> Activity:
        app: App = await self.get_app()
        activity_ref: Optional[str] = self.init_opts.activity
        if not activity_ref:
            log_error(logger, "Activity not specified", ActivityError)
        activity: Optional[Activity] = self.get_resource_by_name_or_uuid(
            await app.get_activities(), activity_ref
        )
        if not activity:
            log_error(logger, f"Activity {activity_ref} not found", ActivityError)
        return activity

    @staticmethod
    def get_activity_fields_to_show(show_template: bool) -> list[str]:
        fields = ["id", "name", "settings"]
        if show_template:
            fields.extend(["activityTemplateWithMode", "universeApiKeyId"])
        return fields

    async def get_files_layer(self) -> FilesLayer:
        app: App = await self.get_app()
        return FilesLayer(app=app)

    async def get_file(self) -> File:
        app: App = await self.get_app()
        file_ref: Optional[str] = self.init_opts.file
        if not file_ref:
            log_error(logger, "File not specified", FileError)
        file: Optional[File] = self.get_resource_by_name_or_uuid(
            await app.get_files(), file_ref
        )
        if not file:
            log_error(logger, f"File {file_ref} not found", FileError)
        return file

    @staticmethod
    def get_file_fields_to_show() -> list[str]:
        return ["id", "name", "contentType", "tags", "metadata"]

    async def get_ai_layer(self) -> AILayer:
        app = await self.get_app()
        return AILayer(
            access_token=self.init_opts.access_token,
            universe=app.parent.parent,
            app=app,
        )

    async def get_role_dicts(self) -> list[dict]:
        if self.init_opts.menu_path:
            apps_layer = await self.get_apps_layer()
            app = await self.get_app()
            return await apps_layer.get_roles(app["id"])
        if self.init_opts.board:
            dashboards_layer = await self.get_dashboards_layer()
            dashboard = await self.get_dashboard()
            return await dashboards_layer.get_roles(dashboard["id"])

        business = await self.get_business()
        business_layer = await self.get_businesses_layer()
        return await business_layer.get_roles(business["id"])

    async def get_role_dict(self) -> dict:
        role_dicts = await self.get_role_dicts()
        role = self.init_opts.role
        role_obj = self.get_resource_by_name_or_uuid(role_dicts, role, "role")
        if not role_obj:
            log_error(logger, f"Role {role} not found", RoleError)
        return role_obj
