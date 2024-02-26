# This file was generated automatically by scripts/user_classes_header_generator.py do not modify it!
# If the user access files are modified, this file has to be regenerated with the script.
from typing import Optional, Union
from pandas import DataFrame


class WorkspacesLayerHeader:
    """
    This class is used to interact with the API at the Workspace layer
    """

    def change_boards_order(
        self,
        boards: list,
        uuid: Optional[str] = None,
        name: Optional[str] = None,
    ):
        """Change the order of the boards of a workspace
        :param name: Name of the workspace
        :param uuid: UUID of the workspace
        :param boards: list of dashboard names
        """
        pass

    def change_menu_order(
        self,
        menu_order: list,
        uuid: Optional[str] = None,
        name: Optional[str] = None,
    ):
        """Change the order of the menu of a workspace
        :param name: Name of the workspace
        :param uuid: UUID of the workspace
        :param menu_order: list of menu names
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

    def create_workspace(
        self,
        name: str,
        create_default_roles: bool = True,
        theme: Optional[dict] = None,
    ) -> dict:
        """Create a new workspace and the necessary roles if specified
        :param name: Name of the workspace
        :param create_default_roles: Create the default roles for the workspace
        :param theme: Theme of the workspace
        :return: workspace data
        """
        pass

    def delete_all_workspace_boards(
        self,
        uuid: Optional[str] = None,
        name: Optional[str] = None,
        force: bool = False,
    ):
        """Delete all boards of a workspace
        :param name: Name of the workspace
        :param uuid: UUID of the workspace
        :param force: Flag to force delete the boards
        """
        pass

    def delete_all_workspace_menu_paths(
        self,
        uuid: Optional[str] = None,
        name: Optional[str] = None,
    ):
        """Delete all menu paths of a workspace
        :param name: Name of the workspace
        :param uuid: UUID of the workspace
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

    def delete_workspace(
        self,
        uuid: Optional[str] = None,
        name: Optional[str] = None,
    ) -> bool:
        """Delete a workspace
        :param name: Name of the workspace
        :param uuid: UUID of the workspace
        :return: True if the workspace was deleted
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

    def get_workspace(
        self,
        uuid: Optional[str] = None,
        name: Optional[str] = None,
    ) -> dict:
        """Get a workspace
        :param name: Name of the workspace
        :param uuid: UUID of the workspace
        :return: Workspace data
        """
        pass

    def get_workspace_boards(
        self,
        uuid: Optional[str] = None,
        name: Optional[str] = None,
    ) -> list:
        """Get the boards of a workspace
        :param name: Name of the workspace
        :param uuid: UUID of the workspace
        :return: list of dashboards
        """
        pass

    def get_workspace_menu_path_ids(
        self,
        uuid: Optional[str] = None,
        name: Optional[str] = None,
    ) -> list:
        """Get the menu path ids of a workspace
        :param name: Name of the workspace
        :param uuid: UUID of the workspace
        :return: list of app ids
        """
        pass

    def get_workspace_menu_paths(
        self,
        uuid: Optional[str] = None,
        name: Optional[str] = None,
    ) -> list:
        """Get the menu paths of a workspace
        :param name: Name of the workspace
        :param uuid: UUID of the workspace
        :return: list of apps
        """
        pass

    def update_workspace(
        self,
        uuid: Optional[str] = None,
        name: Optional[str] = None,
        new_name: Optional[str] = None,
        theme: Optional[dict] = None,
    ) -> bool:
        """Update a workspace
        :param name: Name of the workspace
        :param uuid: UUID of the workspace
        :param new_name: New name of the workspace
        :param theme: New theme of the workspace
        :return: True if the workspace was updated
        """
        pass
