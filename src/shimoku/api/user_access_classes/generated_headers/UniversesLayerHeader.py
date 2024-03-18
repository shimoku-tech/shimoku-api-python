# This file was generated automatically by scripts/user_classes_header_generator.py do not modify it!
# If the user access files are modified, this file has to be regenerated with the script.
from typing import Optional, Union
from pandas import DataFrame


class UniversesLayerHeader:
    """
    Class used to interact with the API at the universe level
    """

    def create_universe_api_key(
        self,
        uuid: str,
        description: str,
    ) -> dict:
        """
        Create a universe API key, this key has admin privileges.
        :param uuid: uuid of the universe
        :param description: description of the key
        """
        pass

    def delete_universe_api_key(
        self,
        uuid: str,
        api_key_uuid: str,
    ) -> bool:
        """
        Delete a universe API key.
        :param uuid: uuid of the universe
        :param api_key_uuid: uuid of the API key
        """
        pass

    def get_universe_action_templates(
        self,
        uuid: str,
    ) -> list:
        """
        Get the universe action templates as a list of dictionaries.
        :param uuid: uuid of the universe
        """
        pass

    def get_universe_actions(
        self,
        uuid: Optional[str] = None,
    ) -> list:
        """
        Get the universe actions_execution as a list of dictionaries.
        :param uuid: uuid of the universe
        """
        pass

    def get_universe_activity_templates(
        self,
        uuid: str,
    ) -> list:
        """
        Get the universe activity templates as a list of dictionaries.
        :param uuid: uuid of the universe
        """
        pass

    def get_universe_api_keys(
        self,
        uuid: str,
    ) -> list:
        """
        Get the universe API keys.
        :param uuid: uuid of the universe
        """
        pass

    def get_universe_workspaces(
        self,
        uuid: str,
    ) -> list:
        """
        Get the universe workspaces.
        :param uuid: uuid of the universe
        """
        pass
