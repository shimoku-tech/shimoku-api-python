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

    def delete_data_point_from_data_set(
        self,
        data_point_id: str,
        uuid: Optional[str] = None,
        name: Optional[str] = None,
    ):
        """Delete a data point from a dataset in the menu path
        :param data_point_id: id of the data point
        :param name: name of the dataset
        :param uuid: uuid of the dataset
        """
        pass

    def delete_data_set(
        self,
        uuid: Optional[str] = None,
        name: Optional[str] = None,
    ):
        """
        Delete a dataset in the menu path
        :param name: name of the dataset
        :param uuid: uuid of the dataset
        """
        pass

    def get_columns_mapping_from_data_point(
        self,
        data: dict,
    ) -> dict:
        """Get the columns mapping from a data point in the menu path,
        assuming that the null values are empty strings.

        :param data: data to be stored in the dataset
        :return: columns mapping
        """
        pass

    def get_data_from_data_set(
        self,
        uuid: Optional[str] = None,
        name: Optional[str] = None,
        limit: Optional[int] = None,
    ) -> list:
        """Get the data in a dataset in the menu path
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
        """Replace the data in a dataset in the menu path
        :param name: name of the dataset
        :param uuid: uuid of the dataset
        :param data: data to be stored in the dataset
        """
        pass

    def update_data_point_from_data_set(
        self,
        data_point_id: str,
        data: dict,
        uuid: Optional[str] = None,
        name: Optional[str] = None,
    ):
        """Update a data point from a dataset in the menu path,
        data has to follow the schema of the dataset!

        e.g. if your dataset has columns 'id', 'name' and 'age',
        the format to update a data point should be:
        {'stringField2': 'new_name', 'intField1': 25}
             ^ because 'id' is the first string column and you wouldnt want to update it

        suggestion: use get_columns_mapping_from_data_point
        to get the columns mapping from a data point

        :param data_point_id: id of the data point
        :param data: data to be stored in the dataset
        :param name: name of the dataset
        :param uuid: uuid of the dataset
        """
        pass
