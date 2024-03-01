# This file was generated automatically by scripts/user_classes_header_generator.py do not modify it!
# If the user access files are modified, this file has to be regenerated with the script.
from typing import Optional, Union
from pandas import DataFrame


class BoardsLayerHeader:
    """
    This class is used to interact with the API at the board level.
    """

    def add_menu_path_in_board(
        self,
        menu_path_name: Optional[str] = None,
        menu_path_id: Optional[str] = None,
        uuid: Optional[str] = None,
        name: Optional[str] = None,
    ):
        """
        Add an app in a board
        :param menu_path_name: name of the board
        :param menu_path_id: UUID of the board
        :param name: name of the board
        :param uuid: UUID of the board
        """
        pass

    def create_board(
        self,
        name: str,
        order: Optional[int] = None,
        is_public: bool = False,
        is_disabled: bool = False,
        theme: Optional[dict] = None,
    ) -> dict:
        """
        Create a board
        :param name: name of the board
        :param order: order of the board
        :param is_public: is the board public
        :param is_disabled: is the board disabled
        :param theme: theme of the board
        :return: board metadata
        """
        pass

    def create_role(
        self,
        uuid: Optional[str] = None,
        name: Optional[str] = None,
        resource: Optional[str] = None,
        role_name: Optional[str] = None,
        permission: Optional[str] = None,
        target: Optional[str] = None,
    ) -> dict:
        """
        Create a new role at the resource level
        :param name: name of the resource
        :param uuid: uuid of the resource
        :param resource: resource of the role
        :param role_name: name of the role
        :param permission: permission of the role
        :param target: target of the role
        """
        pass

    def delete_board(
        self,
        uuid: Optional[str] = None,
        name: Optional[str] = None,
    ) -> bool:
        """
        Delete a board
        :param name: name of the board
        :param uuid: UUID of the board
        """
        pass

    def delete_role(
        self,
        uuid: Optional[str] = None,
        name: Optional[str] = None,
        role_id: Optional[str] = None,
        role_name: Optional[str] = None,
    ):
        """
        Delete the role at the resource level
        :param name: name of the resource
        :param uuid: uuid of the resource
        :param role_id: id of the role
        :param role_name: name of the role
        """
        pass

    def force_delete_board(
        self,
        uuid: Optional[str] = None,
        name: Optional[str] = None,
    ):
        """
        Force delete a board, this will delete the links between the board and the boards first, so that
        the board can always be deleted, but the apps will not be deleted
        :param name: name of the board
        :param uuid: UUID of the board
        """
        pass

    def get_board(
        self,
        uuid: Optional[str] = None,
        name: Optional[str] = None,
    ) -> Optional[dict]:
        """
        Get the board metadata
        :param name: name of the board
        :param uuid: UUID of the board
        :return: board metadata
        """
        pass

    def get_board_menu_path_ids(
        self,
        uuid: Optional[str] = None,
        name: Optional[str] = None,
    ) -> list:
        """
        Get the list of the ids of the boards in the board
        :param name: name of the board
        :param uuid: UUID of the board
        :return: list of the ids of the boards in the board
        """
        pass

    def get_role(
        self,
        uuid: Optional[str] = None,
        name: Optional[str] = None,
        role_name: Optional[str] = None,
    ) -> list:
        """
        Get the role at the resource level
        :param name: name of the resource
        :param uuid: uuid of the resource
        :param role_name: name of the role
        """
        pass

    def get_roles(
        self,
        uuid: Optional[str] = None,
        name: Optional[str] = None,
    ) -> list:
        """
        Get the roles at the resource level
        :param name: name of the resource
        :param uuid: uuid of the resource
        """
        pass

    def group_menu_paths(
        self,
        menu_path_names: Union[list[str], None, str] = None,
        menu_path_ids: Optional[list[str]] = None,
        uuid: Optional[str] = None,
        name: Optional[str] = None,
    ):
        """
        Add multiple boards in a board, if the board does not exist create it
        :param menu_path_names: list of board names
        :param menu_path_ids: list of board UUIDs
        :param name: name of the board
        :param uuid: UUID of the board
        """
        pass

    def is_menu_path_in_board(
        self,
        menu_path_name: Optional[str] = None,
        menu_path_id: Optional[str] = None,
        uuid: Optional[str] = None,
        name: Optional[str] = None,
    ) -> bool:
        """
        Check if an app is in a board
        :param menu_path_name: name of the board
        :param menu_path_id: UUID of the board
        :param name: name of the board
        :param uuid: UUID of the board
        :return: True if the app is in the board, False otherwise
        """
        pass

    def remove_all_menu_paths_from_board(
        self,
        uuid: Optional[str] = None,
        name: Optional[str] = None,
    ):
        """
        Delete all boards links of a board
        :param name: name of the board
        :param uuid: UUID of the board
        """
        pass

    def remove_menu_path_from_board(
        self,
        menu_path_name: Optional[str] = None,
        menu_path_id: Optional[str] = None,
        uuid: Optional[str] = None,
        name: Optional[str] = None,
    ):
        """
        Remove an app from a board
        :param menu_path_name: name of the board
        :param menu_path_id: UUID of the board
        :param name: name of the board
        :param uuid: UUID of the board
        """
        pass

    def update_board(
        self,
        uuid: Optional[str] = None,
        name: Optional[str] = None,
        new_name: Optional[str] = None,
        order: Optional[int] = None,
        is_public: Optional[bool] = None,
        is_disabled: Optional[bool] = None,
        theme: Optional[dict] = None,
    ) -> bool:
        """
        Update a board
        :param new_name: name of the board
        :param uuid: UUID of the board
        :param name: new name of the board
        :param order: new order of the board
        :param is_public: new public permission of the board
        :param is_disabled: new is_disabled of the board
        :param theme: new theme of the board
        """
        pass
