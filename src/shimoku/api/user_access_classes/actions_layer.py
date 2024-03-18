from typing import Optional

from shimoku.api.resources.action import Action
from shimoku.api.resources.universe import Universe

from shimoku.exceptions import UniverseApiKeyError, ActionError

import logging
from shimoku.execution_logger import log_error, ClassWithLogging

logger = logging.getLogger(__name__)


async def get_universe_api_key(
    universe: Universe, universe_api_key: Optional[str]
) -> str:
    """Get the universe API key or create one if none exists
    :param universe: Universe
    :param universe_api_key: Universe API key
    :return: Universe API key
    """
    universe_api_keys = await universe.get_universe_api_keys()
    if universe_api_key is None:
        if len(universe_api_keys) == 0:
            return (await universe.create_universe_api_key("Actions key"))["id"]
        return universe_api_keys[0]["id"]
    if universe_api_key not in [k["id"] for k in universe_api_keys]:
        log_error(
            logger,
            f"Universe API key {universe_api_key} not found in {universe_api_keys}",
            UniverseApiKeyError,
        )
    return universe_api_key


class ActionsLayer(ClassWithLogging):
    """
    This class is used to interact with the API at the Workspace layer
    """

    _module_logger = logger
    _use_info_logging = True

    def __init__(
        self,
        universe: Universe,
    ):
        self._universe = universe

    # @add_to_general_async_group
    async def create_action(
        self,
        name: str,
        description: Optional[str] = None,
        action_template_id: Optional[str] = None,
        universe_api_key: Optional[str] = None,
        path_to_code: Optional[str] = None,
        code: Optional[str] = None,
        overwrite: Optional[bool] = False,
        libraries: Optional[list[str]] = None,
    ) -> str:
        """
        Create an action.
        :param name: name of the action
        :param description: description of the action
        :param action_template_id: id of the action template
        :param universe_api_key: id of the universe API key
        :param path_to_code: path to the code
        :param code: code of the action
        :param libraries: libraries of the action
        :param overwrite: whether to overwrite the action if it already exists
        """
        if not libraries:
            libraries = []
        if code and path_to_code:
            log_error(
                logger,
                "You cannot provide both a path to code and code",
                ActionError,
            )
        if path_to_code:
            with open(path_to_code, "r") as file:
                code = file.read()
        if not code:
            log_error(
                logger,
                "Code is empty, make sure to provide a path to code or code itself",
                ActionError,
            )
        universe_api_key = await get_universe_api_key(
            universe=self._universe, universe_api_key=universe_api_key
        )
        if overwrite:
            action = await self._universe.get_action(name=name)
            if action:
                await self._universe.delete_action(uuid=action["id"])
        action: Action = await self._universe.create_action(
            name=name,
            description=description,
            action_template_id=action_template_id,
            universe_api_key_id=universe_api_key,
            libraries=libraries,
        )
        await action.upload_code(code)
        logger.info(
            f"Action ({name}) created with id ({action['id']}) and code uploaded"
        )
        return action["id"]

    # @add_to_individual_async_group
    async def update_action(
        self,
        uuid: Optional[str] = None,
        name: Optional[str] = None,
        new_name: Optional[str] = None,
        new_description: Optional[str] = None,
    ):
        """
        Update an action.
        :param uuid: uuid of the action
        :param name: name of the action
        :param new_name: new name of the action
        :param new_description: new description of the action
        """
        await self._universe.update_action(
            uuid=uuid, name=name, new_name=new_name, new_description=new_description
        )

    # @add_to_individual_async_group
    async def delete_action(
        self,
        uuid: Optional[str] = None,
        name: Optional[str] = None,
    ):
        """
        Delete an action.
        :param uuid: uuid of the action
        :param name: name of the action
        """
        await self._universe.delete_action(uuid=uuid, name=name)
        logger.info(f"Action ({name or uuid}) deleted")

    async def get_action_metadata(
        self,
        uuid: Optional[str] = None,
        name: Optional[str] = None,
    ) -> dict:
        """
        Get an action.
        :param uuid: uuid of the action
        :param name: name of the action
        :return: The action
        """
        action = await self._universe.get_action(uuid=uuid, name=name)
        if not action:
            log_error(
                logger,
                f"Action ({name}) not found",
                ActionError,
            )
        action_as_dict = action.cascade_to_dict()
        del action_as_dict["scripts"]
        return action_as_dict

    async def get_action_code(
        self,
        uuid: Optional[str] = None,
        name: Optional[str] = None,
    ) -> str:
        """
        Get the code of the action.
        :param uuid: uuid of the action
        :param name: name of the action
        :return: The code of the action
        """
        action = await self._universe.get_action(uuid=uuid, name=name)
        if not action:
            log_error(
                logger,
                f"Action ({name}) not found",
                ActionError,
            )
        return await action.get_code()
