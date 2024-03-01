# This file was generated automatically by scripts/user_classes_header_generator.py do not modify it!
# If the user access files are modified, this file has to be regenerated with the script.
from typing import Optional, Union
from pandas import DataFrame


class DataSetsLayerHeader:
    """
    This class is used to interact with the API at the data set level.
    """

    def append_to_data_set(
        self,
        data: Union[list[dict], DataFrame],
        uuid: Optional[str] = None,
        name: Optional[str] = None,
    ) -> str:
        """
        Appends data to a dataset, if the dataset does not exist it will be created.
        :param name: name of the dataset
        :param uuid: uuid of the dataset
        :param data: data to be stored in the dataset
        :return: dataset id
        """
        pass

    def delete_data_set(
        self,
        uuid: Optional[str] = None,
        name: Optional[str] = None,
    ):
        """
        Delete a dataset in the app
        :param name: name of the dataset
        :param uuid: uuid of the dataset
        """
        pass

    def get_data_from_data_set(
        self,
        uuid: Optional[str] = None,
        name: Optional[str] = None,
        limit: Optional[int] = None,
    ) -> list:
        """Get the data in a dataset in the app
        :param name: name of the dataset
        :param uuid: uuid of the dataset
        :param limit: limit of the data points to be returned
        :return: data in the dataset
        """
        pass

    def replace_data_from_data_set(
        self,
        data: Union[list[dict], DataFrame],
        uuid: Optional[str] = None,
        name: Optional[str] = None,
    ):
        """Replace the data in a dataset in the app
        :param name: name of the dataset
        :param uuid: uuid of the dataset
        :param data: data to be stored in the dataset
        """
        pass
