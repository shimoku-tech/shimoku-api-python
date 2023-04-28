""""""
import datetime
import datetime as dt

import asyncio

from shimoku_api_python.async_execution_pool import async_auto_call_manager, ExecutionPoolContext

from typing import List, Dict, Optional, Union, Any, TYPE_CHECKING

from shimoku_api_python.base_resource import Resource, ResourceCache

if TYPE_CHECKING:
    from shimoku_api_python.api.app_metadata_api import App

import json

import logging
from shimoku_api_python.execution_logger import logging_before_and_after, log_error

logger = logging.getLogger(__name__)


class Activity(Resource):

    resource_type = 'activity'
    alias_field = 'name'
    plural = 'activities'

    class Run(Resource):

        resource_type = 'run'
        plural = 'runs'

        class Log(Resource):

            resource_type = 'log'
            plural = 'logs'

            def __init__(self, parent: 'Activity.Run', uuid: Optional[str] = None, message: Optional[str] = None,
                         severity: Optional[str] = None, tags: Optional[Dict[str, str]] = None):
                super().__init__(parent=parent, uuid=uuid, check_params_before_creation=['message', 'severity'],
                                 params_to_serialize=['tags'])

                self._base_resource.params = {
                    'dateTime': str(dt.datetime.now().isoformat())[:-3] + "Z",
                    'message': message,
                    'severity': severity,
                    'tags': tags if tags else {},
                }

            def set_params(self, message: Optional[str] = None, severity: Optional[str] = None,
                           tags: Optional[Dict[str, str]] = None):
                if message:
                    self._base_resource.params['message'] = message
                if severity:
                    self._base_resource.params['severity'] = severity
                if tags:
                    self._base_resource.params['tags'] = tags if tags else {}

        def __init__(self, parent: 'Activity', uuid: Optional[str] = None, settings: Optional[Dict] = None):
            super().__init__(parent=parent, uuid=uuid, children=[Activity.Run.Log],
                             params_to_serialize=['settings'])

            self._base_resource.params = {
                'settings': settings if settings else {},
            }

        async def create_log(self, message: str, severity: str, tags: Dict[str, str]) -> 'Activity.Run.Log':

            if tags and (not isinstance(tags, Dict) or any([not isinstance(key, str) or not isinstance(value, str)
                                                            for key, value in tags.items()])):
                log_error(logger, 'The tags must be a dictionary of strings.', ValueError)

            log = await Activity.Run.Log(parent=self, message=message, severity=severity, tags=tags)
            await self._base_resource.children[Activity.Run.Log].add(log)
            return log

        async def get_log(self, uuid: str) -> 'Activity.Run.Log':
            return await self._base_resource.get_child(Activity.Run.Log, uuid)

        async def get_logs(self) -> List['Activity.Run.Log']:
            logs = await self._base_resource.get_children(Activity.Run.Log)
            return sorted(logs, key=lambda log: log['dateTime'])

        async def trigger_webhook(self):
            endpoint = self._base_resource.base_url + f'run/{self._base_resource.id}/triggerWebhook'

            response = await(
                self._base_resource.api_client.query_element(
                    method='POST', endpoint=endpoint,
                )
            )

            return response['STATUS']

    def __init__(self, parent: 'App', uuid: Optional[str] = None, alias: Optional[str] = None,
                 settings: Optional[dict] = None, how_many_runs: int = 1):
        super().__init__(parent=parent, uuid=uuid, children=[Activity.Run], check_params_before_creation=['name'],
                         params_to_serialize=['settings'])

        self._base_resource.params = {
            'name': alias,
            'settings': settings if settings else {},
        }

        self.how_many_runs = how_many_runs

    async def delete(self):
        return await self._base_resource.delete()

    async def update(self):
        return await self._base_resource.update()

    async def create_run(self, settings: Optional[Union[Dict, str]] = None) -> 'Activity.Run':

        cache: ResourceCache = self._base_resource.children[Activity.Run]

        if isinstance(settings, str):

            if settings not in cache:
                await self._base_resource.children[Activity.Run].list()
                if settings not in cache:
                    log_error(logger, f'The run with id {settings} does not exist in the activity'
                                      f' {self._base_resource.params["name"]}.', ValueError)

            settings = (await cache[settings])['settings']

            assert isinstance(settings, dict)

        run = await Activity.Run(parent=self, settings=settings if isinstance(settings, dict) else {})
        await cache.add(run)
        return run

    async def get_run(self, uuid: str) -> 'Activity.Run':
        return await self._base_resource.get_child(Activity.Run, uuid)

    async def get_runs(self, how_many_runs) -> List['Activity.Run']:
        def runs_ordering(run: 'Activity.Run') -> dt.datetime:
            logs = run._base_resource.children[Activity.Run.Log]
            if len(logs) > 0:
                return max([
                    dt.datetime.strptime(log['dateTime'], "%Y-%m-%dT%H:%M:%S.%fZ")
                    if log['dateTime'] else dt.datetime.min
                    for log_id, log in logs
                ])
            else:
                return dt.datetime.min

        runs = await self._base_resource.get_children(Activity.Run)

        await asyncio.gather(*runs)

        return sorted(runs, key=runs_ordering)[-how_many_runs:]

    def set_params(self, name: Optional[str] = None, settings: Optional[dict] = None,
                   how_many_runs: Optional[int] = None):
        if isinstance(name, str):
            self._base_resource.params['name'] = name
        if isinstance(settings, dict):
            self._base_resource.params['settings'] = settings
        if isinstance(how_many_runs, int):
            self.how_many_runs = how_many_runs


class ActivityMetadataApi:
    """
    This class is used to interact with the activities that are available in an app, through the API.
    """

    @logging_before_and_after(logging_level=logger.debug)
    def __init__(self, app: 'App', execution_pool_context: ExecutionPoolContext):
        self._app = app
        self.epc: ExecutionPoolContext = execution_pool_context

    @async_auto_call_manager(execute=True)
    @logging_before_and_after(logging_level=logger.info)
    async def create_activity(self, name: str, settings: Optional[Dict] = None) -> Dict:
        """
        Create an activity by its name and app id
        :param name: the name of the activity
        :param settings: the settings of the activity
        :return: the dictionary representation of the activity
        """
        return (await self._app.create_activity(name=name, settings=settings)).cascade_to_dict()

    @async_auto_call_manager(execute=True)
    @logging_before_and_after(logging_level=logger.info)
    async def delete_activity(self, name: Optional[str] = None, uuid: Optional[str] = None):
        """
        Delete an activity by its name and app id
        :param name: the name of the activity
        :param uuid: the id of the activity
        :return:
        """
        await self._app.delete_activity(uuid=uuid, name=name)

    @async_auto_call_manager(execute=True)
    @logging_before_and_after(logging_level=logger.info)
    async def update_activity(self, name: Optional[str] = None, uuid: Optional[str] = None,
                              new_name: Optional[str] = None, settings: Optional[Dict] = None) -> Dict:
        """
        Update an activity by its name or id
        :param name: the name of the activity
        :param uuid: the id of the activity
        :param new_name: the new name of the activity
        :param settings: the default settings of the activity
        :return: the updated activity as a dictionary
        """
        activity: Activity = await self._app.get_activity(uuid=uuid, name=name)

        activity.set_params(name=new_name, settings=settings)
        await activity.update()

        return activity.cascade_to_dict()

    @async_auto_call_manager(execute=True)
    @logging_before_and_after(logging_level=logger.info)
    async def execute_activity(self, name: Optional[str] = None, uuid: Optional[str] = None,
                               run_settings: Union[Dict, str] = None) -> Dict:
        """
        Execute an activity by its name or id
        :param name: the name of the activity
        :param uuid: the id of the activity
        :param run_settings: the settings of the run, or the id of the run to clone settings from
        :return: the run of the activity as a dictionary
        """
        activity: Activity = await self._app.get_activity(uuid=uuid, name=name)
        run = await activity.create_run(settings=run_settings)
        result = await run.trigger_webhook()
        await run
        logger.info(f'Activity {name if name else uuid} executed with result {result}')
        return run.cascade_to_dict()

    @async_auto_call_manager(execute=True)
    @logging_before_and_after(logging_level=logger.info)
    async def get_activity(self, name: Optional[str] = None, uuid: Optional[str] = None,
                           pretty_print: bool = False, how_many_runs: Optional[int] = None) -> Dict:
        """
        Get an activity by its name
        :param name: the name of the activity
        :param uuid: the id of the activity
        :param pretty_print: if True, the activity is printed in a pretty format
        :param how_many_runs: how many runs to get
        :return: the activity as a dictionary
        """
        activity: Activity = await self._app.get_activity(uuid=uuid, name=name)
        activity.set_params(how_many_runs=how_many_runs)
        await activity.get()
        activity_as_dict = activity.cascade_to_dict()

        if how_many_runs:
            activity_as_dict['runs'] = [run.cascade_to_dict() for run in
                                        (await activity.get_runs(how_many_runs=how_many_runs))]
        if pretty_print:
            print(json.dumps(activity_as_dict, indent=2))

        return activity_as_dict

    @async_auto_call_manager(execute=True)
    @logging_before_and_after(logging_level=logger.info)
    async def get_activities(self, pretty_print: bool = False, print_names: bool = False) -> List[Dict]:
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
            logger.info(f'Activities available in the app: '
                        f'{", ".join([activity["name"] for activity in activities])}')

        return activities_as_dicts

    @async_auto_call_manager(execute=True)
    @logging_before_and_after(logging_level=logger.info)
    async def create_run(self, name: Optional[str] = None, uuid: Optional[str] = None,
                         settings: Union[Dict, str] = None) -> Dict[str, Any]:
        """
        Create a run for an activity by its name
        :param name: the name of the activity
        :param uuid: the id of the activity
        :param settings: the settings of the run, or the id of the run to clone settings from
        :return: the run created as a dictionary
        """

        activity = await self._app.get_activity(uuid=uuid, name=name)

        run = await activity.create_run(settings=settings)

        logger.info(f'New run with id {run["id"]} created for activity {name if name else uuid}.')

        return run.cascade_to_dict()

    @async_auto_call_manager(execute=True)
    @logging_before_and_after(logging_level=logger.info)
    async def execute_run(self, run_id: str, name: Optional[str] = None, uuid: Optional[str] = None):
        """
        Execute a run by its id
        :param name: the name of the activity
        :param uuid: the id of the activity
        :param run_id: the id of the run
        :return:
        """
        activity = await self._app.get_activity(uuid=uuid, name=name)

        run = await activity.get_run(uuid=run_id)
        result = await run.trigger_webhook()
        await run

        logger.info(f'Run with id {run_id} executed with result {result}')

    @async_auto_call_manager(execute=True)
    @logging_before_and_after(logging_level=logger.info)
    async def create_run_log(self, run_id: str, message: str, severity: Optional[str] = 'INFO',
                             tags: Optional[Dict[str, str]] = None, pretty_print: bool = False,
                             name: Optional[str] = None, uuid: Optional[str] = None
                             ) -> Dict[str, str]:
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
        activity = await self._app.get_activity(uuid=uuid, name=name)
        run: Activity.Run = await activity.get_run(uuid=run_id)
        log: Dict = (
            await run.create_log(message=message, severity=severity, tags=tags if tags else {})
        ).cascade_to_dict()

        if pretty_print:
            print(json.dumps(log, indent=2))

        return log

    @async_auto_call_manager(execute=True)
    @logging_before_and_after(logging_level=logger.info)
    async def get_run_settings(self, run_id: str, name: Optional[str] = None, uuid: Optional[str] = None
                               ) -> Dict[str, Any]:
        """
        Get the settings of a run by its id
        :param name: the name of the activity
        :param uuid: the id of the activity
        :param run_id: the id of the run
        :return: the settings of the run as a dictionary
        """

        activity = await self._app.get_activity(uuid=uuid, name=name)
        run = await activity.get_run(uuid=run_id)
        return run["settings"]

    @async_auto_call_manager(execute=True)
    @logging_before_and_after(logging_level=logger.info)
    async def get_run_logs(self, run_id: str, name: Optional[str] = None, uuid: Optional[str] = None
                           ) -> List[Dict[str, Any]]:
        """
        Get the logs of a run by its id
        :param name: the name of the activity
        :param uuid: the id of the activity
        :param run_id: the id of the run
        :return: the logs of the run as a list of dictionaries
        """

        activity = await self._app.get_activity(uuid=uuid, name=name)
        run = await activity.get_run(uuid=run_id)
        return [log.cascade_to_dict() for log in await run.get_logs()]
