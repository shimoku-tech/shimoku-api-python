# This file was generated automatically by scripts/user_classes_header_generator.py do not modify it!
# If the user access files are modified, this file has to be regenerated with the script.
from typing import Optional, Union
from pandas import DataFrame


class ActivitiesLayerHeader:
    """
    This class is used to interact with the activities that are available in a menu path, through the API.
    """

    def create_activity(
        self,
        name: str,
        settings: Optional[dict] = None,
        template_id: Optional[str] = None,
        template_name_version: Optional[tuple[str, str]] = None,
        template_mode: str = "LIGHT",
        universe_api_key: str = "",
    ) -> dict:
        """
        Create an activity by its name and app id
        :param name: the name of the activity
        :param settings: the settings of the activity
        :param template_id: the template id of the activity
        :param template_name_version: the template name and version of the activity
        :param template_mode: the template mode of the activity
        :param universe_api_key: the universe api key of the activity
        :return: the dictionary representation of the activity
        """
        pass

    def create_run(
        self,
        uuid: Optional[str] = None,
        name: Optional[str] = None,
        settings: Union[dict, str] = None,
    ) -> dict:
        """
        Create a run for an activity by its name
        :param name: the name of the activity
        :param uuid: the id of the activity
        :param settings: the settings of the run, or the id of the run to clone settings from
        :return: the run created as a dictionary
        """
        pass

    def create_run_log(
        self,
        run_id: str,
        message: str,
        severity: Optional[str] = "INFO",
        tags: Optional[dict[str, str]] = None,
        pretty_print: bool = False,
        uuid: Optional[str] = None,
        name: Optional[str] = None,
    ) -> dict:
        """
        Create a log for a run by its id
        :param name: the name of the activity
        :param uuid: the id of the activity
        :param run_id: the id of the run
        :param message: the message to log
        :param severity: the severity of the log
        :param tags: the tags of the log
        :param pretty_print: if True, the log is printed in a pretty format
        :return:
        """
        pass

    def create_webhook(
        self,
        url: str,
        uuid: Optional[str] = None,
        name: Optional[str] = None,
        method: str = "GET",
        headers: Optional[dict] = None,
    ):
        """
        Create a webhook by its name and app id
        :param name: the name of the activity
        :param uuid: the id of the activity
        :param url: the url of the webhook
        :param method: the method of the webhook
        :param headers: the headers of the webhook
        """
        pass

    def delete_activity(
        self,
        uuid: Optional[str] = None,
        name: Optional[str] = None,
        with_linked_to_templates: Optional[bool] = False,
    ):
        """
        Delete an activity by its name and app id
        :param name: the name of the activity
        :param uuid: the id of the activity
        :param with_linked_to_templates: if the activity is linked to a template, delete it anyway
        """
        pass

    def execute_activity(
        self,
        uuid: Optional[str] = None,
        name: Optional[str] = None,
        run_settings: Union[dict, str] = None,
    ) -> dict:
        """
        Execute an activity by its name or id
        :param name: the name of the activity
        :param uuid: the id of the activity
        :param run_settings: the settings of the run, or the id of the run to clone settings from
        :return: the run of the activity as a dictionary
        """
        pass

    def execute_run(
        self,
        run_id: str,
        uuid: Optional[str] = None,
        name: Optional[str] = None,
    ):
        """
        Execute a run by its id
        :param name: the name of the activity
        :param uuid: the id of the activity
        :param run_id: the id of the run
        :return:
        """
        pass

    def get_activities(
        self,
        pretty_print: bool = False,
        print_names: bool = False,
    ) -> list:
        """
        Get the list of activities in the app
        :param pretty_print: if True, the activities are printed in a pretty format
        :param print_names: if True and pretty_print is False, only the names of the activities are printed
        :return: a list of activities as dictionaries
        """
        pass

    def get_activity(
        self,
        uuid: Optional[str] = None,
        name: Optional[str] = None,
        pretty_print: bool = False,
        how_many_runs: Optional[int] = None,
    ) -> Optional[dict]:
        """
        Get an activity by its name
        :param name: the name of the activity
        :param uuid: the id of the activity
        :param pretty_print: if True, the activity is printed in a pretty format
        :param how_many_runs: how many runs to get
        :return: the activity as a dictionary
        """
        pass

    def get_run_logs(
        self,
        run_id: str,
        uuid: Optional[str] = None,
        name: Optional[str] = None,
    ) -> list:
        """
        Get the logs of a run by its id
        :param name: the name of the activity
        :param uuid: the id of the activity
        :param run_id: the id of the run
        :return: the logs of the run as a list of dictionaries
        """
        pass

    def get_run_settings(
        self,
        run_id: str,
        uuid: Optional[str] = None,
        name: Optional[str] = None,
    ) -> dict:
        """
        Get the settings of a run by its id
        :param name: the name of the activity
        :param uuid: the id of the activity
        :param run_id: the id of the run
        :return: the settings of the run as a dictionary
        """
        pass

    def update_activity(
        self,
        uuid: Optional[str] = None,
        name: Optional[str] = None,
        new_name: Optional[str] = None,
        settings: Optional[dict] = None,
    ):
        """
        Update an activity by its name or id
        :param name: the name of the activity
        :param uuid: the id of the activity
        :param new_name: the new name of the activity
        :param settings: the default settings of the activity
        :return: the updated activity as a dictionary
        """
        pass
