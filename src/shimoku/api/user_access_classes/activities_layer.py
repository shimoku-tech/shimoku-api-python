from typing import Optional, Union, TYPE_CHECKING

from shimoku.api.resources.activity import Activity
from shimoku.exceptions import ActivityError

import json

import logging
from shimoku.execution_logger import log_error, ClassWithLogging

logger = logging.getLogger(__name__)

if TYPE_CHECKING:
    from shimoku import App


class ActivitiesLayer(ClassWithLogging):
    """
    This class is used to interact with the activities that are available in a menu path, through the API.
    """

    _module_logger = logger
    _use_info_logging = True

    def __init__(self, app: Optional["App"]):
        self._app = app

    async def _get_activity_with_error(self, uuid: Optional[str], name: Optional[str]):
        """
        Get an activity by its name or id, with error handling
        :param name: the name of the activity
        :param uuid: the id of the activity
        """
        activity: Activity = await self._app.get_activity(uuid=uuid, name=name)
        if not activity:
            log_error(logger, f"Activity ({name}) not found", ActivityError)
        return activity

    async def create_activity(
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
        return (
            await self._app.create_activity(
                name=name,
                settings=settings,
                template_id=template_id,
                template_name_version=template_name_version,
                template_mode=template_mode,
                universe_api_key=universe_api_key,
            )
        ).cascade_to_dict()

    async def delete_activity(
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
        activity: Activity = await self._get_activity_with_error(uuid=uuid, name=name)
        if not with_linked_to_templates and activity["activityTemplateWithMode"]:
            log_error(
                logger,
                f"Activity ({str(activity)}) is linked to a template please use the "
                f"(with_linked_to_templates) parameter set to True to delete it",
                ActivityError,
            )
        await self._app.delete_activity(uuid=uuid, name=name)

    async def update_activity(
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
        await self._app.update_activity(
            uuid=uuid, name=name, new_name=new_name, settings=settings
        )

    async def create_webhook(
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
        activity: Activity = await self._get_activity_with_error(uuid=uuid, name=name)
        await activity.create_webhook(url=url, method=method, headers=headers or {})

    async def execute_activity(
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
        activity: Activity = await self._get_activity_with_error(uuid=uuid, name=name)
        run = await activity.create_run(settings=run_settings)
        result = await run.trigger_webhook()
        await run
        logger.info(f"Activity {name if name else uuid} executed with result {result}")
        return run.cascade_to_dict()

    async def get_activity(
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
        activity: Activity = await self._app.get_activity(uuid=uuid, name=name)
        if not activity:
            return None

        await activity.get()
        activity_as_dict = activity.cascade_to_dict()

        if how_many_runs:
            activity_as_dict["runs"] = [
                run.cascade_to_dict()
                for run in (await activity.get_runs(how_many_runs=how_many_runs))
            ]
        if pretty_print:
            print(json.dumps(activity_as_dict, indent=2))

        return activity_as_dict

    async def get_activities(
        self, pretty_print: bool = False, print_names: bool = False
    ) -> list[dict]:
        """
        Get the list of activities in the app
        :param pretty_print: if True, the activities are printed in a pretty format
        :param print_names: if True and pretty_print is False, only the names of the activities are printed
        :return: a list of activities as dictionaries
        """

        activities = await self._app.get_activities()
        activities_as_dicts = [activity.cascade_to_dict() for activity in activities]

        if pretty_print:
            print(json.dumps(activities_as_dicts, indent=2))
        elif print_names:
            logger.info(
                f"Activities available in the app: "
                f'{", ".join([activity["name"] for activity in activities])}'
            )

        return activities_as_dicts

    async def create_run(
        self,
        uuid: Optional[str] = None,
        name: Optional[str] = None,
        settings: Union[dict, str] = None,
    ) -> dict[str, any]:
        """
        Create a run for an activity by its name
        :param name: the name of the activity
        :param uuid: the id of the activity
        :param settings: the settings of the run, or the id of the run to clone settings from
        :return: the run created as a dictionary
        """

        activity: Activity = await self._get_activity_with_error(uuid=uuid, name=name)
        run = await activity.create_run(settings=settings)

        logger.info(
            f'New run with id {run["id"]} created for activity {name if name else uuid}.'
        )

        return run.cascade_to_dict()

    async def execute_run(
        self, run_id: str, uuid: Optional[str] = None, name: Optional[str] = None
    ):
        """
        Execute a run by its id
        :param name: the name of the activity
        :param uuid: the id of the activity
        :param run_id: the id of the run
        :return:
        """
        activity: Activity = await self._get_activity_with_error(uuid=uuid, name=name)
        run = await activity.get_run(uuid=run_id)
        result = await run.trigger_webhook()
        await run
        logger.info(f"Run with id {run_id} executed with result {result}")

    async def create_run_log(
        self,
        run_id: str,
        message: str,
        severity: Optional[str] = "INFO",
        tags: Optional[dict[str, str]] = None,
        pretty_print: bool = False,
        uuid: Optional[str] = None,
        name: Optional[str] = None,
    ) -> dict[str, str]:
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
        activity: Activity = await self._get_activity_with_error(uuid=uuid, name=name)
        run: Activity.Run = await activity.get_run(uuid=run_id)
        log: dict = (
            await run.create_log(
                message=message, severity=severity, tags=tags if tags else {}
            )
        ).cascade_to_dict()

        if pretty_print:
            print(json.dumps(log, indent=2))

        return log

    async def get_run_settings(
        self, run_id: str, uuid: Optional[str] = None, name: Optional[str] = None
    ) -> dict[str, any]:
        """
        Get the settings of a run by its id
        :param name: the name of the activity
        :param uuid: the id of the activity
        :param run_id: the id of the run
        :return: the settings of the run as a dictionary
        """

        activity: Activity = await self._get_activity_with_error(uuid=uuid, name=name)
        run = await activity.get_run(uuid=run_id)
        return run["settings"]

    async def get_run_logs(
        self, run_id: str, uuid: Optional[str] = None, name: Optional[str] = None
    ) -> list[dict[str, any]]:
        """
        Get the logs of a run by its id
        :param name: the name of the activity
        :param uuid: the id of the activity
        :param run_id: the id of the run
        :return: the logs of the run as a list of dictionaries
        """

        activity: Activity = await self._get_activity_with_error(uuid=uuid, name=name)
        run = await activity.get_run(uuid=run_id)
        return [log.cascade_to_dict() for log in await run.get_logs()]
