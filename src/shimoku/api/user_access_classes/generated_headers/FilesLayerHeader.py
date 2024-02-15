# This file was generated automatically by scripts/user_classes_header_generator.py do not modify it!
# If the user access files are modified, this file has to be regenerated with the script.
from typing import Optional, Union
from pandas import DataFrame


class FilesLayerHeader:
    """
    This class is used to interact with the API at the file level.
    """

    def delete_file(
        self,
        uuid: Optional[str] = None,
        file_name: Optional[str] = None,
        with_shimoku_generated: bool = False,
    ):
        """
        Delete a file
        :param uuid: uuid of the file
        :param file_name: name of the file
        :param with_shimoku_generated: if True, allow to delete a file with the tag 'shimoku_generated'
        """
        pass

    def deleted_batched_dataframe(
        self,
        file_name: str,
        with_shimoku_generated: bool = False,
    ):
        """
        Delete a batched dataframe
        :param file_name: name of the file
        :param with_shimoku_generated: if True, allow to delete a file with the tag 'shimoku_generated'
        """
        pass

    def get_ai_model(
        self,
        uuid: Optional[str] = None,
        model_name: Optional[str] = None,
    ) -> any:
        """
        Get a model
        :param uuid: uuid of the file
        :param model_name: name of the model
        :return: model
        """
        pass

    def get_batched_dataframe(
        self,
        file_name: str,
    ) -> DataFrame:
        """
        Get a batched dataframe file group
        :param file_name: name of the file
        :return: dataframe
        """
        pass

    def get_dataframe(
        self,
        uuid: Optional[str] = None,
        file_name: Optional[str] = None,
    ) -> DataFrame:
        """
        Get a dataframe file
        :param uuid: uuid of the file
        :param file_name: name of the file
        :return: dataframe
        """
        pass

    def get_file_metadata(
        self,
        uuid: Optional[str] = None,
        file_name: Optional[str] = None,
    ) -> dict:
        """
        Get file metadata
        :param uuid: uuid of the file
        :param file_name: name of the file
        :return: the metadata
        """
        pass

    def get_object(
        self,
        uuid: Optional[str] = None,
        file_name: Optional[str] = None,
    ) -> bytes:
        """
        Get an object
        :param file_name: name of the file
        :param uuid: uuid of the file
        :return: object
        """
        pass

    def post_ai_model(
        self,
        model_name: str,
        model: callable,
        overwrite: bool = True,
        tags: Optional[list] = None,
        metadata: Optional[dict] = None,
    ):
        """
        Save a model
        :param model_name: name of the model
        :param model: model to be saved
        :param overwrite: if True, overwrite the file if it already exists
        :param tags: tags to be added to the file
        :param metadata: metadata to be added to the file
        """
        pass

    def post_batched_dataframe(
        self,
        file_name: str,
        df: DataFrame,
        batch_size: int = 10000,
        overwrite: bool = True,
        tags: Optional[list] = None,
        metadata: Optional[dict] = None,
    ):
        """
        Creates an multiple files saving a dataframe in batches, for big dataframes
        Uploads a dataframe in batches, for big dataframes
        :param file_name: name of the file
        :param df: dataframe to be saved
        :param batch_size: size of the batches
        :param overwrite: if True, overwrite the file if it already exists
        :param tags: tags to be added to the file
        :param metadata: metadata to be added to the file
        """
        pass

    def post_dataframe(
        self,
        file_name: str,
        df: DataFrame,
        overwrite: bool = True,
        tags: Optional[list] = None,
        metadata: Optional[dict] = None,
    ):
        """
        Save a dataframe
        :param df: dataframe to be saved
        :param file_name: name of the file
        :param overwrite: if True, overwrite the file if it already exists
        :param tags: tags to be added to the file
        :param metadata: metadata to be added to the file
        :return: object
        """
        pass

    def post_object(
        self,
        file_name: str,
        obj: bytes,
        overwrite: bool = True,
        tags: Optional[list] = None,
        metadata: Optional[dict] = None,
    ):
        """
        Save an object
        :param file_name: name of the file
        :param obj: object to be saved
        :param overwrite: if True, overwrite the file if it already exists
        :param tags: tags to be added to the file
        :param metadata: metadata to be added to the file
        """
        pass
