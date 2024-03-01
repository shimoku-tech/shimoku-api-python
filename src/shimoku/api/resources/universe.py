from typing import Optional, List, Tuple

from shimoku.api.base_resource import Resource
from shimoku.api.resources.business import Business
from shimoku.api.resources.activity_template import ActivityTemplate
from shimoku.api.client import ApiClient
from shimoku.api.resources.action import Action
from shimoku.api.resources.action_template import ActionTemplate

import logging
from shimoku.execution_logger import log_error

logger = logging.getLogger(__name__)


class UniverseApiKey(Resource):
    _module_logger = logger
    resource_type = "apiKey"
    plural = "apiKeys"

    def __init__(
        self,
        parent: "Universe",
        uuid: Optional[str] = None,
        db_resource: Optional[dict] = None,
    ):
        params = dict(
            userType="ADMIN",
            enabled=True,
            description="",
        )

        super().__init__(
            parent=parent,
            uuid=uuid,
            db_resource=db_resource,
            params=params,
        )


class Universe(Resource):
    _module_logger = logger
    resource_type = "universe"

    def __init__(self, api_client: ApiClient, uuid: str):
        super().__init__(
            api_client=api_client,
            uuid=uuid,
            children=[Business, ActivityTemplate, Action, UniverseApiKey],
        )

    async def create_universe_api_key(self, description: str) -> UniverseApiKey:
        return await self._base_resource.create_child(
            UniverseApiKey, userType="ADMIN", enabled=True, description=description
        )

    async def get_universe_api_keys(self) -> list[UniverseApiKey]:
        return await self._base_resource.get_children(UniverseApiKey)

    async def delete_universe_api_key(self, uuid: str) -> bool:
        return await self._base_resource.delete_child(UniverseApiKey, uuid)

    # Business methods
    async def create_business(
        self, name: str, theme: Optional[dict] = None
    ) -> Business:
        if self._base_resource.api_client.playground:
            log_error(
                logger, "Cannot create business in local environment", RuntimeError
            )
        return await self._base_resource.create_child(
            Business, alias=name, theme=theme if theme else {}
        )

    async def update_business(
        self, uuid: Optional[str] = None, name: Optional[str] = None, **params
    ) -> bool:
        if params.get("new_name") is not None:
            params["name"] = params.pop("new_name")
            params["new_alias"] = True
        if self._base_resource.api_client.playground:
            uuid, name = "local", None
        return await self._base_resource.update_child(
            Business, uuid=uuid, alias=name, **params
        )

    async def get_business(
        self, uuid: Optional[str] = None, name: Optional[str] = None
    ) -> Optional[Business]:
        if self._base_resource.api_client.playground:
            uuid, name = "local", None
        return await self._base_resource.get_child(Business, uuid, name)

    async def get_businesses(self) -> List[Business]:
        return await self._base_resource.get_children(Business)

    async def delete_business(
        self, uuid: Optional[str] = None, name: Optional[str] = None
    ) -> bool:
        if self._base_resource.api_client.playground:
            log_error(logger, "Cannot delete local business", RuntimeError)
        return await self._base_resource.delete_child(Business, uuid, name)

    # Activity template methods
    async def get_activity_template(
        self, uuid: Optional[str] = None, name_version: Optional[Tuple[str, str]] = None
    ) -> Optional[ActivityTemplate]:
        return await self._base_resource.get_child(ActivityTemplate, uuid, name_version)

    @staticmethod
    def interpret_version(version: str) -> list:
        """Interpret a version string by appending '0' to each section for sorting."""
        numbers = "0123456789"
        if not version:
            return [0, 0, 0]

        def interpret_version_section(section: str) -> list:
            """Interpret a version section, considering non-numeric characters as earlier."""
            res_section = []
            number = ""
            for c in section:
                if c in numbers:
                    number += c
                else:
                    if number:
                        res_section.append(ord("z") + int(number))
                        number = ""
                    res_section.append(ord(c))
            if number:
                res_section.append(ord("z") + int(number))
            return res_section

        return [
            interpret_version_section(section + "0") for section in version.split(".")
        ]

    async def get_activity_templates(self) -> list[ActivityTemplate]:
        templates = await self._base_resource.get_children(ActivityTemplate)
        return sorted(
            templates, key=lambda t: [t["name"]] + self.interpret_version(t["version"])
        )

    # action methods
    async def get_action(
        self, uuid: Optional[str] = None, name: Optional[str] = None
    ) -> Optional[Action]:
        return await self._base_resource.get_child(Action, uuid, name)

    async def get_actions(self) -> list[Action]:
        return await self._base_resource.get_children(Action)

    async def create_action(
        self,
        name: str,
        description: Optional[str] = None,
        action_template_id: Optional[str] = None,
        universe_api_key_id: Optional[str] = None,
        libraries: Optional[List[str]] = None,
    ) -> Action:
        return await self._base_resource.create_child(
            Action,
            alias=name,
            description=description,
            actionTemplateId=action_template_id,
            universeApiKeyId=universe_api_key_id,
            pythonLibraries=libraries,
        )

    async def delete_action(
        self, uuid: Optional[str] = None, name: Optional[str] = None
    ) -> bool:
        return await self._base_resource.delete_child(Action, uuid, name)

    async def update_action(
        self,
        uuid: Optional[str] = None,
        name: Optional[str] = None,
        new_name: Optional[str] = None,
        new_description: Optional[str] = None,
    ) -> bool:
        return await self._base_resource.update_child(
            Action,
            uuid=uuid,
            alias=name,
            new_alias=new_name,
            new_description=new_description,
        )

    # action template methods
    async def get_action_templates(self) -> list[ActionTemplate]:
        return await self._base_resource.get_children(ActionTemplate)
