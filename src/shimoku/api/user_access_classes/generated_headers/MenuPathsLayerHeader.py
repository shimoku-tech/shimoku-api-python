# This file was generated automatically by scripts/user_classes_header_generator.py do not modify it!
# If the user access files are modified, this file has to be regenerated with the script.
from typing import Optional, Union
from pandas import DataFrame


class MenuPathsLayerHeader:
    """
    This class is used to interact with the API at the Menu Path level.
    """

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

    def delete_all_menu_path_activities(
        self,
        uuid: Optional[str] = None,
        name: Optional[str] = None,
        with_linked_to_templates: Optional[bool] = False,
    ) -> bool:
        """
        Delete all activities of a menu path
        :param uuid: uuid of the menu path
        :param name: name of the menu path
        :param with_linked_to_templates: if True, delete all activities, even those linked to templates
        """
        pass

    def delete_all_menu_path_components(
        self,
        uuid: Optional[str] = None,
        name: Optional[str] = None,
        sub_path: Optional[str] = None,
    ) -> bool:
        """
        Delete all reports of a menu path
        :param uuid: uuid of the menu path
        :param name: name of the menu path
        :param sub_path: sub path of the menu path
        """
        pass

    def delete_all_menu_path_data_sets(
        self,
        uuid: Optional[str] = None,
        name: Optional[str] = None,
    ) -> bool:
        """
        Delete all datasets of a menu path
        :param uuid: uuid of the menu path
        :param name: name of the menu path
        """
        pass

    def delete_all_menu_path_files(
        self,
        uuid: Optional[str] = None,
        name: Optional[str] = None,
        with_shimoku_generated: Optional[bool] = False,
    ) -> bool:
        """
        Delete all files of an menu path
        :param uuid: uuid of the menu path
        :param name: name of the menu path
        :param with_shimoku_generated: whether the file is generated internally by the SDK
        """
        pass

    def delete_menu_path(
        self,
        uuid: Optional[str] = None,
        name: Optional[str] = None,
    ) -> bool:
        """
        Delete a menu path
        :param uuid: uuid of the menu path
        :param name:
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

    def get_menu_path(
        self,
        uuid: Optional[str] = None,
        name: Optional[str] = None,
    ) -> dict:
        """
        Get a menu path
        :param uuid: uuid of the menu path
        :param name: name of the menu path
        :return: menu path metadata
        """
        pass

    def get_menu_path_activities(
        self,
        uuid: Optional[str] = None,
        name: Optional[str] = None,
    ) -> list:
        """
        Get the activities of a menu path
        :param uuid: uuid of the menu path
        :param name: name of the menu path
        """
        pass

    def get_menu_path_components(
        self,
        uuid: Optional[str] = None,
        name: Optional[str] = None,
    ) -> list:
        """
        Get the reports of a menu path
        :param uuid: uuid of the menu path
        :param name: name of the menu path
        """
        pass

    def get_menu_path_data_sets(
        self,
        uuid: Optional[str] = None,
        name: Optional[str] = None,
    ) -> list:
        """
        Get the datasets of a menu path
        :param uuid: uuid of the menu path
        :param name: name of the menu path
        """
        pass

    def get_menu_path_files(
        self,
        uuid: Optional[str] = None,
        name: Optional[str] = None,
        with_shimoku_generated: Optional[bool] = False,
    ) -> list:
        """
        Get the files of an menu path
        :param uuid: uuid of the menu path
        :param name: name of the menu path
        :param with_shimoku_generated: whether the file is generated internally by the SDK
        """
        pass

    def get_menu_path_sub_paths(
        self,
        uuid: Optional[str] = None,
        name: Optional[str] = None,
    ) -> list:
        """
        Get the path names of an menu path
        :param uuid: uuid of the menu path
        :param name: name of the menu path
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

    def update_menu_path(
        self,
        uuid: Optional[str] = None,
        name: Optional[str] = None,
        new_name: Optional[str] = None,
        hide_title: Optional[bool] = None,
        hide_path: Optional[bool] = None,
        show_breadcrumb: Optional[bool] = None,
        show_history_navigation: Optional[bool] = None,
        order: Optional[int] = None,
    ) -> bool:
        """
        Update a menu path
        :param uuid: uuid of the menu path
        :param name: the name of the menu path
        :param new_name: new name of the menu path
        :param hide_title: hide title of the menu path
        :param hide_path: hide path of the menu path
        :param show_breadcrumb: show breadcrumb of the menu path
        :param show_history_navigation: show history navigation of the menu path
        :param order: order of the menu path in the side menu
        :return: menu path metadata
        """
        pass
