from typing import Optional, TYPE_CHECKING, TypedDict

import asyncio

from shimoku.api.base_resource import Resource

if TYPE_CHECKING:
    from shimoku.api.resources.universe import Universe

import logging

logger = logging.getLogger(__name__)

MAX_CODE_FRAGMENT_SIZE = 8000


class ActionScript(Resource):
    _module_logger = logger
    resource_type = "script"
    plural = "scripts"

    class ActionScriptParams(TypedDict):
        order: int
        codeFragment: str

    def __init__(
        self,
        parent: "Action",
        uuid: Optional[str] = None,
        db_resource: Optional[dict] = None,
    ):
        params = ActionScript.ActionScriptParams(
            order=0,
            codeFragment="",
        )

        super().__init__(
            parent=parent,
            uuid=uuid,
            db_resource=db_resource,
            check_params_before_creation=["order"],
            params=params,
        )

    async def delete(self):
        """Deletes the action script."""
        return await self._base_resource.delete()


class Action(Resource):
    _module_logger = logger
    resource_type = "action"
    alias_field = "name"
    plural = "actions"

    class ActionParams(TypedDict):
        name: Optional[str]
        description: Optional[str]
        actionTemplateId: Optional[str]
        universeApiKeyId: Optional[str]
        pythonLibraries: Optional[list[str]]

    def __init__(
        self,
        parent: "Universe",
        uuid: Optional[str] = None,
        alias: Optional[str] = None,
        db_resource: Optional[dict] = None,
    ):
        params = Action.ActionParams(
            name=alias,
            description=None,
            actionTemplateId=None,
            universeApiKeyId=None,
            pythonLibraries=None,
        )

        super().__init__(
            parent=parent,
            uuid=uuid,
            db_resource=db_resource,
            children=[ActionScript],
            check_params_before_creation=["name"],
            params=params,
        )

    async def delete(self):
        """Deletes the action."""
        return await self._base_resource.delete()

    async def update(self):
        """Updates the action."""
        return await self._base_resource.update()

    async def get_code(self) -> str:
        """Gets the code of the action."""
        scripts = sorted(
            await self._base_resource.get_children(ActionScript),
            key=lambda s: s["order"],
        )
        return "".join([script["codeFragment"] for script in scripts])

    async def upload_code(self, code: str):
        """Uploads the code of the action."""
        current_action_scripts = await self._base_resource.get_children(ActionScript)
        if current_action_scripts:
            logger.warning(
                "The action already contains code. The current code will be deleted."
            )
            await asyncio.gather(
                *[script.delete() for script in current_action_scripts]
            )
        await asyncio.gather(
            *[
                self._base_resource.create_child(
                    ActionScript,
                    order=i,
                    codeFragment=code_fragment,
                )
                for i, code_fragment in enumerate(
                    code[i : i + MAX_CODE_FRAGMENT_SIZE]
                    for i in range(0, len(code), MAX_CODE_FRAGMENT_SIZE)
                )
            ]
        )

    async def delete_code(self):
        """Deletes the code of the action."""
        current_action_scripts = await self._base_resource.get_children(ActionScript)
        await asyncio.gather(*[script.delete() for script in current_action_scripts])
