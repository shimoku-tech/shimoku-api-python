# This file was generated automatically by scripts/user_classes_header_generator.py do not modify it!
# If the user access files are modified, this file has to be regenerated with the script.
from typing import Optional, Union
from pandas import DataFrame


class ActionsLayerHeader:
    """
    This class is used to interact with the API at the Workspace layer
    """

    def create_action(
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
        pass

    def delete_action(
        self,
        uuid: Optional[str] = None,
        name: Optional[str] = None,
    ):
        """
        Delete an action.
        :param uuid: uuid of the action
        :param name: name of the action
        """
        pass

    def get_action_code(
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
        pass

    def get_action_metadata(
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
        pass

    def update_action(
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
        pass
