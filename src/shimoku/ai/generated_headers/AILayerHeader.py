# This file was generated automatically by scripts/user_classes_header_generator.py do not modify it!
# If the user access files are modified, this file has to be regenerated with the script.
from typing import Optional, Union
from pandas import DataFrame


class AIFunctionMethodsHeader:
    """None"""

    def create_model(
        self,
        model_name: str,
        model: bytes,
        metadata: Optional[dict] = None,
    ):
        """Create a model
        :param model_name: Name of the model
        :param model: Model to be uploaded
        :param metadata: Metadata of the model
        """
        pass

    def create_output_files(
        self,
        files: dict,
        model_name: Optional[str] = None,
    ):
        """Create output files of a ai_function
        :param files: Files to be uploaded
        :param model_name: Name of the model used
        """
        pass

    def get_model(
        self,
        model_name: str,
    ) -> tuple:
        """Get a model
        :param model_name: Name of the model
        :return: The model if it exists
        """
        pass


class AILayerHeader:
    """None"""

    def check_for_private_access(
        self,
        ai_function_id: str,
        run_id: str,
    ):
        """Check if the credentials allow for private ai_function methods"""
        pass

    def create_input_files(
        self,
        input_files: dict,
        force_overwrite: bool = False,
    ):
        """Create input files for a ai_function
        :param input_files: dictionary of input files to create
        :param force_overwrite: Force the overwrite of the files
        """
        pass

    def delete_input_file(
        self,
        file_name: str,
    ):
        """Delete an input file
        :param file_name: Name of the file to delete
        """
        pass

    def delete_model(
        self,
        model_name: str,
    ):
        """Delete a model
        :param model_name: Name of the model
        """
        pass

    def generic_execute(
        self,
        ai_function: str,
        version: Optional[str] = None,
        universe_api_key: Optional[str] = None,
        **kwargs,
    ) -> str:
        """Execute a generic ai_function
        :param ai_function: Name of the ai_function to execute
        :param version: Version of the ai_function to execute
        :param universe_api_key: API key of the universe
        :param params: Parameters to be passed to the ai_function
        """
        pass

    def get_available_input_files(
        self,
    ) -> list:
        """Get available input files for a ai_function"""
        pass

    def get_last_executions_with_logs(
        self,
        ai_function: str,
        version: Optional[str] = None,
        how_many: int = 1,
    ):
        """Get the logs of the executions of a ai_function
        :param ai_function: Name of the ai_function to execute
        :param version: Version of the ai_function to execute
        :param how_many: Number of executions to get
        :return: The logs of the ai_function
        """
        pass

    def get_output_file_objects(
        self,
        run_id: str,
        file_name: Optional[str] = None,
    ) -> Union[tuple[bytes, dict], dict[str, tuple[bytes, dict]]]:
        """Get an output file object for a given ai_function and run id
        :param run_id: ID of the executed run
        :param file_name: Name of the file to get
        """
        pass

    def get_output_files_by_ai_function(
        self,
        ai_function: str,
        version: Optional[str] = None,
        file_name: Optional[str] = None,
        get_objects: bool = False,
    ):
        """Get output files for a generic ai_function
        :param ai_function: Name of the ai_function to execute
        :param version: Version of the ai_function to execute
        :return: The output files if they exist
        :param file_name: Name of the file to get
        :param get_objects: Get the file objects instead of the file metadata
        """
        pass

    def get_output_files_by_model(
        self,
        model_name: str,
        file_name: Optional[str] = None,
        get_objects: bool = False,
    ):
        """Get output files for the executions of ai_functions with a given model
        :param model_name: Name of the model to use
        :param file_name: Name of the file to get
        :param get_objects: Get the file objects instead of the file metadata
        :return: dictionary of output files by the execution identifier
        """
        pass

    def get_private_ai_function_methods(
        self,
    ) -> AIFunctionMethodsHeader:
        """Get the private ai_function methods if the credentials allow for it"""
        pass
