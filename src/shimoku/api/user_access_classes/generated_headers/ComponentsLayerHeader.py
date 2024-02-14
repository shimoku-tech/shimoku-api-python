# This file was generated automatically by scripts/user_classes_header_generator.py do not modify it!
# If the user access files are modified, this file has to be regenerated with the script.
from typing import Optional, Union
from pandas import DataFrame


class ComponentsLayerHeader:
    """
    This class is used to interact with the API at the component level.
    """

    def delete_component(
        self,
        uuid: str,
    ):
        """
        :param uuid: uuid of the component
        """
        pass

    def get_component(
        self,
        uuid: str,
    ) -> dict:
        """
        :param uuid: uuid of the component
        :return: component
        """
        pass

    def get_component_data_set_links(
        self,
        uuid: str,
    ) -> list:
        """
        :param uuid: uuid of the component
        :return: list of data set links
        """
        pass

    def get_components_in_sub_path(
        self,
        path: str,
    ) -> list:
        """
        :param path: path to the components
        :return: list of components
        """
        pass
