""""""
import datetime
import datetime as dt

from shimoku_api_python.api.app_metadata_api import AppMetadataApi
from shimoku_api_python.api.business_metadata_api import BusinessMetadataApi
from shimoku_api_python.api.plot_api import PlotApi
from shimoku_api_python.async_execution_pool import async_auto_call_manager, ExecutionPoolContext

from typing import List, Dict, Optional, Union, Tuple, Any, Iterable, Callable

import asyncio

import json

import logging
from shimoku_api_python.execution_logger import logging_before_and_after

logger = logging.getLogger(__name__)


class Activity:
    """
    A class that contains all the information necessary to create and run an activity.

    Attributes:
        business_id (str): The UUID of the business that the activity belongs to.
        app_id (str): The UUID of the app that the activity belongs to.
        id (str): The UUID of the activity.
        name (str): The name of the activity.
        runs (List[Run]): The list of runs of the activity.

    Methods:
        create_new_run(): Creates a new run of the activity.
        _api_create_activity(name: str): Creates the activity on the server.

    """

    class Run:
        """
        Run of an activity, which is a single execution of the activity.
        Attributes:
            activity (Activity): The activity that the run belongs to.
            id (str): The UUID of the run.
            logs (List[str, str, str]): The list of logs of the run.

        Methods:
            _api_create_run(): Creates the run on the server.
            _api_create_execution(): Creates the execution of the run on the server.
            _api_create_run_log(): Creates the log of the run on the server.
        """

        @logging_before_and_after(logging_level=logger.debug)
        async def _api_create_run_log(self, message: str, severity: str, tags: Dict[str, str]):
            # TODO this should be handled by the structure of the SDK #
            endpoint: str = f'business/{self.activity.business_id}/' \
                            f'app/{self.activity.app_id}/' \
                            f'activity/{self.activity.id}/' \
                            f'run/{self.id}/' \
                            f'log'

            log = {'dateTime': str(datetime.datetime.now().isoformat())[:-3]+"Z", 'message': message,
                   'severity': severity, 'tags': json.dumps(tags)}

            response = await self.activity.api_client.query_element(
                method='POST', endpoint=endpoint,
                **{'body_params': log}
            )
            ###########################################################
            response['tags'] = json.loads(response['tags'])
            return response

        @logging_before_and_after(logging_level=logger.debug)
        async def _api_trigger_webhook(self):
            """
            Creates the execution of the run on the server.
            """
            # TODO this should be handled by the structure of the SDK #
            endpoint: str = f'business/{self.activity.business_id}/' \
                            f'app/{self.activity.app_id}/' \
                            f'activity/{self.activity.id}/' \
                            f'run/{self.id}/' \
                            f'triggerWebhook'

            response = await(
                self.activity.api_client.query_element(
                    method='POST', endpoint=endpoint,
                )
            )
            ###########################################################
            return response['STATUS']

        @logging_before_and_after(logging_level=logger.debug)
        async def _api_create_run(self):
            """
            Creates the run on the server.
            """
            # TODO this should be handled by the structure of the SDK #
            endpoint: str = f'business/{self.activity.business_id}/' \
                            f'app/{self.activity.app_id}/' \
                            f'activity/{self.activity.id}/' \
                            f'run'

            response = await(
                self.activity.api_client.query_element(
                    method='POST', endpoint=endpoint,
                    **{'body_params': {'settings': json.dumps(self.settings)} if self.settings is not None else {}}
                )
            )
            ###########################################################
            return response['id']

        @logging_before_and_after(logging_level=logger.debug)
        async def _api_get_run(self, run_id: str):
            """
            Gets the run from the server.
            """
            # TODO this should be handled by the structure of the SDK #
            endpoint: str = f'business/{self.activity.business_id}/' \
                            f'app/{self.activity.app_id}/' \
                            f'activity/{self.activity.id}/' \
                            f'run/{run_id}'

            response = await(
                self.activity.api_client.query_element(
                    method='GET', endpoint=endpoint,
                )
            )
            ###########################################################
            return response

        @logging_before_and_after(logging_level=logger.debug)
        def __init__(self, activity, id: str = None, settings: Optional[Dict] = None):
            self.activity = activity
            self.id = id
            self.logs = []
            self.settings = settings

        @logging_before_and_after(logging_level=logger.debug)
        async def _api_get_run_logs(self):
            """
            Gets the logs of the run from the server.
            """
            # TODO this should be handled by the structure of the SDK #
            endpoint: str = f'business/{self.activity.business_id}/' \
                            f'app/{self.activity.app_id}/' \
                            f'activity/{self.activity.id}/' \
                            f'run/{self.id}/' \
                            f'logs'

            logs = await self.activity.api_client.query_element(
                method='GET', endpoint=endpoint,
            )
            ###########################################################
            return logs['items']

        @logging_before_and_after(logging_level=logger.debug)
        async def _async_init(self):
            """
            Asynchonous initialization of the run, it's called when the run is awaited.
            It creates the run on the server.
            """
            if self.id:
                run = await self._api_get_run(self.id)
                self.settings = json.loads(run['settings']) if run.get('settings') else {}
                await self.get_logs()
            else:
                self.id = await self._api_create_run()

            return self

        @logging_before_and_after(logging_level=logger.debug)
        def __await__(self):
            """
            Allows the run to be awaited.
            """
            return self._async_init().__await__()

        @logging_before_and_after(logging_level=logger.debug)
        def to_dict(self) -> Dict[str, Any]:
            """
            Returns a dictionary representation of the run.
            """
            return {
                'id': self.id,
                'logs': self.logs,
                'settings': self.settings,
            }

        @logging_before_and_after(logging_level=logger.debug)
        async def execute(self):
            """
            Executes the run and then returns the status of the run.
            """
            if self.id is None:
                error = 'The run has not been created yet. Make sure to await the run before running it.'
                logger.error(error)
                raise RuntimeError(error)

            status = await self._api_trigger_webhook()

            return status

        @logging_before_and_after(logging_level=logger.debug)
        async def create_log(self, message: str, severity: str, tags: Dict[str, str]) -> Dict[str, str]:
            """
            Creates a log on the server.
            :param message: The message of the log.
            :param severity: The severity of the log.
            :param tags: The tags of the log.
            :return: The log.
            """
            if self.id is None:
                error = 'The run has not been created yet. Make sure to await the run before creating a log.'
                logger.error(error)
                raise RuntimeError(error)

            if tags and (not isinstance(tags, Dict) or any([not isinstance(key, str) or not isinstance(value, str)
                                                            for key, value in tags.items()])):
                error = 'The tags must be a dictionary of strings.'
                logger.error(error)
                raise ValueError(error)

            log = await self._api_create_run_log(message=message, severity=severity, tags=tags)
            self.logs.append(log)

            return log

        @logging_before_and_after(logging_level=logger.debug)
        async def get_logs(self) -> List[Dict[str, str]]:
            """
            Gets the logs of the run from the server and returns them as a list of dictionaries.
            """
            if self.id is None:
                error = 'The run has not been created yet. Make sure to await the run before getting the logs.'
                logger.error(error)
                raise RuntimeError(error)

            self.logs = await self._api_get_run_logs()

            for log in self.logs:
                log['tags'] = json.loads(log['tags']) if log.get('tags') else {}

            self.logs.sort(
                key=lambda log:
                dt.datetime.strptime(log['dateTime'], "%Y-%m-%dT%H:%M:%S.%fZ")
                if log.get('dateTime') else dt.datetime.min
            )

            return self.logs

    @logging_before_and_after(logging_level=logger.debug)
    async def _api_create_activity(self, name: str):
        """
        Creates the activity on the server.
        """
        # TODO this should be handled by the structure of the SDK #
        endpoint: str = f'business/{self.business_id}/' \
                        f'app/{self.app_id}/' \
                        f'activity'

        item = {'name': name}

        response = await(
            self.api_client.query_element(
                method='POST', endpoint=endpoint,
                **{'body_params': item}
            )
        )
        ###########################################################
        return response['id']

    @logging_before_and_after(logging_level=logger.debug)
    def __init__(self, api_client, business_id: str, app_id: str, name: str,
                 id: Optional[str] = None, settings: Optional[Dict] = None):
        # TODO this should be handled by the structure of the SDK #
        self.business_id: str = business_id
        self.app_id: Optional[str] = app_id
        self.api_client = api_client
        ###########################################################

        self.name: str = name
        self.id: str = id
        self.runs: Dict[str, Activity.Run] = {}
        self.how_many_runs: int = 1
        self.settings = settings
        self.awaited = False

    @logging_before_and_after(logging_level=logger.debug)
    async def _api_get_runs(self):
        """
        Returns the runs of the activity from the server.
        """
        # TODO this should be handled by the structure of the SDK #
        endpoint: str = f'business/{self.business_id}/' \
                        f'app/{self.app_id}/' \
                        f'activity/{self.id}/' \
                        f'runs'

        response = await self.api_client.query_element(
            method='GET', endpoint=endpoint,
        )
        ###########################################################
        return response['items']

    @logging_before_and_after(logging_level=logger.debug)
    async def _async_init(self):
        """
        Asyncronous initialization of the activity, it's called when the activity is awaited.
        """

        if self.awaited:
            return self
        self.awaited = True

        if self.id:
            for run in (await self._api_get_runs()):
                self.runs[run['id']] = Activity.Run(activity=self, id=run['id'],
                                                    settings=json.loads(run['settings']) if run.get('settings') else {})

            await asyncio.gather(*[run for run in self.runs.values()])

            # Sort the runs by the date of the last log
            self.runs = dict(
                sorted(
                    list(self.runs.items()),
                    key=lambda rid_r: max(
                        [
                            dt.datetime.strptime(log['dateTime'], "%Y-%m-%dT%H:%M:%S.%fZ")
                            if log.get('dateTime') else dt.datetime.min
                            for log in rid_r[1].logs
                        ]
                        if len(rid_r[1].logs) > 0 else [dt.datetime.min]
                    )
                )
            )
        else:
            self.id = await self._api_create_activity(self.name)

        return self

    @logging_before_and_after(logging_level=logger.debug)
    def __await__(self):
        """
        Allows the activity to be awaited.
        """
        return self._async_init().__await__()

    @logging_before_and_after(logging_level=logger.debug)
    def to_dict(self) -> Dict[str, Any]:
        """
        Returns a dictionary representation of the activity.
        """
        return {
            'id': self.id,
            'name': self.name,
            'runs': [run.to_dict() for run in list(self.runs.values())[-self.how_many_runs:]],
            'settings': self.settings
        }

    @logging_before_and_after(logging_level=logger.debug)
    async def create_new_run(self, settings: Union[Dict, str]) -> Run:
        """
        Creates a new run for the activity.
        :param settings: The settings of the run, or the id of the run to copy the settings from.
        :return: The newly created run.
        """
        if self.id is None:
            error = 'The activity has not been created yet. Make sure to await the activity before creating a run.'
            logger.error(error)
            raise RuntimeError(error)

        if isinstance(settings, str):
            if settings not in self.runs:
                error = f'The run with id {settings} does not exist in the activity {self.name}.'
                logger.error(error)
                raise RuntimeError(error)
            settings = self.runs[settings].settings

        run = await Activity.Run(self, settings=settings)
        self.runs[run.id] = run
        return run

    @logging_before_and_after(logging_level=logger.debug)
    async def get_run(self, run_id: str) -> Run:
        """
        Returns the run with the given id.
        """
        if self.id is None:
            error = 'The activity has not been created yet. Make sure to await the activity before getting a run.'
            logger.error(error)
            raise RuntimeError(error)

        if run_id not in self.runs:
            run = await Activity.Run(self, id=run_id)
            self.runs[run.id] = run

        return self.runs[run_id]

    @logging_before_and_after(logging_level=logger.debug)
    async def delete(self):
        """
        Deletes the activity from the business.
        """
        if self.id is None:
            error = 'The activity has not been created yet. Make sure to await the activity before deleting it.'
            logger.error(error)
            raise RuntimeError(error)

        # TODO this should be handled by the structure of the SDK #
        endpoint: str = f'business/{self.business_id}/' \
                        f'app/{self.app_id}/' \
                        f'activity/{self.id}'

        await self.api_client.query_element(method='DELETE', endpoint=endpoint)
        ###########################################################

    @logging_before_and_after(logging_level=logger.debug)
    async def update(self, new_name: Optional[str] = None, settings: Optional[Dict] = None):
        """
        Updates the activity from the business.
        :param new_name: The new name of the activity.
        :param settings: The new default settings of the activity.
        """
        if self.id is None:
            error = 'The activity has not been created yet. Make sure to await the activity before updating it.'
            logger.error(error)
            raise RuntimeError(error)

        # TODO this should be handled by the structure of the SDK #
        endpoint: str = f'business/{self.business_id}/' \
                        f'app/{self.app_id}/' \
                        f'activity/{self.id}'

        item = {}
        if new_name is not None:
            item['name'] = new_name

        if settings is not None:
            item['settings'] = json.dumps(settings)

        if len(item) == 0:
            logger.warning('No changes were made to the activity.')
            return

        await self.api_client.query_element(method='PATCH', endpoint=endpoint, **{'body_params': item})
        ###########################################################

        if new_name is not None:
            self.name = new_name

        if settings is not None:
            self.settings = settings


# TODO: the menu path should be handled by the structure of the SDK and not checked for every function call
class ActivityMetadataApi:
    """
    This class is used to interact with the activities that are available in the business, through the API.

    Attributes:
        api_client: The API client used to interact with the API.
        business_id: The UUID of the business.
        activities: A dictionary of the activities available in the business, with the activity name as key.
        _app_metadata_api: The AppMetadataApi instance used to interact with the apps.
        _business_metadata_api: The BusinessMetadataApi instance used to interact with the business.

    Methods:
        _get_business_activities: Get the activities available in the business.
        _clear_local_activities: Clear the local activities.
        set_business: Set the business to interact with.
        create_activity: Create an activity in the business
        update_activity: Update an activities name in the business.
        delete_activity: Delete an activity in the business.
        execute_activity: Execute an activity in the business, creating a new run.
        get_activity: Get an activity from the business.
        _get_activity: private method to get an activity from the business.
        get_acticities: Get all the activities from the app.
        create_run: Create a new run for an activity.
        execute_run: Execute a run for an activity.
        create_run_log: Create a new run log for a run.
        get_run_settings: Get the settings of a run.


    """

    @logging_before_and_after(logging_level=logger.debug)
    def __init__(self, api_client, app_metadata_api: AppMetadataApi, business_metadata_api: BusinessMetadataApi,
                 plot_api: PlotApi, execution_pool_context: ExecutionPoolContext, business_id: Optional[str] = None):
        self.api_client = api_client
        self.business_id: Optional[str] = business_id
        self.activities: Dict[(str, str), Activity] = {}
        self.activities_by_id: Dict[str, Activity] = {}
        # TODO this should be handled by the structure of the SDK #
        self._app_metadata_api: AppMetadataApi = app_metadata_api
        self._business_metadata_api: BusinessMetadataApi = business_metadata_api
        self._plot_api: PlotApi = plot_api
        self.epc: ExecutionPoolContext = execution_pool_context
        ###########################################################

    @logging_before_and_after(logging_level=logger.debug)
    async def _get_business_activities(self):
        """
        Get the activities available in the business and store them in the activities attribute.
        The key of the dictionary is a tuple with the app id and the activity name.
        """
        activities = await self._business_metadata_api.async_get_business_activities(self.business_id)
        for activity in activities:
            activity_entry = (activity['appId'], activity['name'])

            activity_obj = Activity(
                api_client=self.api_client, business_id=self.business_id,
                app_id=activity['appId'], name=activity['name'], id=activity['id'],
                settings=json.loads(activity['settings']) if activity.get('settings') else {},
            )

            if 'settings' not in activity:
                await activity_obj.update(settings={})

            self.activities[activity_entry] = activity_obj
            self.activities_by_id[activity['id']] = activity_obj

    @logging_before_and_after(logging_level=logger.debug)
    def _clear_local_activities(self):
        """
        Clear the activities and activities_by_id attributes.
        """
        self.activities = {}
        self.activities_by_id = {}

    @staticmethod
    def _clean_menu_path(menu_path: str) -> Tuple[str, str]:
        """
        Break the menu path in the apptype or app normalizedName
        and the path normalizedName if any
        :param menu_path: the menu path
        """
        # remove empty spaces
        menu_path: str = menu_path.strip()
        # replace "_" for www protocol it is not good
        menu_path = menu_path.replace('_', '-')

        try:
            assert len(menu_path.split('/')) <= 2  # we allow only one level of path
        except AssertionError:
            raise ValueError(
                f'We only allow one subpath in your request | '
                f'you introduced {menu_path} it should be maximum '
                f'{"/".join(menu_path.split("/")[:1])}'
            )

        # Split AppType or App Normalized Name
        normalized_name: str = menu_path.split('/')[0]
        name: str = (
            ' '.join(normalized_name.split('-'))
        )

        try:
            path_normalized_name: str = menu_path.split('/')[1]
            path_name: str = (
                ' '.join(path_normalized_name.split('-'))
            )
        except IndexError:
            path_name = None

        return name, path_name

    @logging_before_and_after(logging_level=logger.debug)
    async def _resolve_app_id(self, app_id: Optional[str] = None, menu_path: Optional[str] = None) -> str:
        """
        Resolve the app id from the app id or the menu path.
        :param app_id: the app id
        :param menu_path: the menu path
        :return: the app id
        """
        if app_id:
            return app_id
        if not menu_path:
            raise ValueError("Either an app_id or a menu_path has to be provided")

        app_name, _ = self._clean_menu_path(menu_path=menu_path)
        return (await self._app_metadata_api._async_get_or_create_app_and_apptype(name=app_name))['id']

    @logging_before_and_after(logging_level=logger.info)
    def set_business(self, business_id: str):
        """
        Set the business id to which the activities belong. Test if the business exists.
        :param business_id: the UUID of the business
        :return:
        """
        # If the business id does not exists it raises an ApiClientError
        _ = self._business_metadata_api.get_business(business_id)
        self._clear_local_activities()
        self.business_id = business_id


    @async_auto_call_manager(execute=True)
    @logging_before_and_after(logging_level=logger.info)
    async def create_activity(self,  activity_name: str,
                              menu_path: Optional[str] = None, app_id: Optional[str] = None) -> Dict:
        """
        Create an activity by its name and app id
        :param activity_name: the name of the activity
        :param menu_path: the menu path of the app to which the activity belongs
        :param app_id: the id of the app to which the activity belongs
        :return:
        """
        app_id: str = await self._resolve_app_id(menu_path=menu_path, app_id=app_id)
        activity_entry = (app_id, activity_name)

        if activity_entry not in self.activities:
            activity = await Activity(self.api_client, self.business_id, app_id, activity_name)
            self.activities[activity_entry] = activity
            self.activities_by_id[activity.id] = activity
        else:
            logger.info(f'Activity {activity_name} already exists in app {app_id}.')

        return self.activities[activity_entry].to_dict()

    @logging_before_and_after(logging_level=logger.debug)
    async def _get_activity(self, menu_path: Optional[str] = None, app_id: Optional[str] = None,
                            activity_name: Optional[str] = None, activity_id: Optional[str] = None,
                            how_many_runs: int = -1) -> Activity:
        """
        Get an activity by its name and app, or by its id.
        :param activity_name: the name of the activity
        :param menu_path: the menu path of the app to which the activity belongs
        :param app_id: the id of the app to which the activity belongs
        :param activity_id: the id of the activity
        :param how_many_runs: the number of runs to get from the activity
        :return: the activity object
        """
        app_id: str = await self._resolve_app_id(menu_path=menu_path, app_id=app_id)

        activity_entry = (app_id, activity_name)

        if not activity_id and not activity_name:
            error = 'Either activity_id or activity_name must be provided.'
            logger.error(error)
            raise ValueError(error)

        if (activity_id and activity_id not in self.activities_by_id) or \
           (activity_name and activity_entry not in self.activities):
            self._clear_local_activities()
            await self._get_business_activities()

            if (activity_id and activity_id not in self.activities_by_id) or \
               (activity_name and activity_entry not in self.activities):
                error = f'Activity {activity_name} not found in app {app_id}.'
                logger.error(error)
                raise RuntimeError(error)

        activity = self.activities_by_id[activity_id] if activity_id else self.activities[activity_entry]

        if how_many_runs > 0:
            activity.how_many_runs = how_many_runs

        return await activity

    @async_auto_call_manager(execute=True)
    @logging_before_and_after(logging_level=logger.info)
    async def delete_activity(self, menu_path: Optional[str] = None, app_id: Optional[str] = None,
                              activity_name: Optional[str] = None, activity_id: Optional[str] = None):
        """
        Delete an activity by its name and app id
        :param activity_name: the name of the activity
        :param activity_id: the id of the activity
        :param menu_path: the menu path of the app to which the activity belongs
        :param app_id: the id of the app to which the activity belongs
        :return:
        """
        app_id = await self._resolve_app_id(menu_path=menu_path, app_id=app_id)
        activity = await self._get_activity(app_id=app_id, activity_id=activity_id, activity_name=activity_name)
        activity_name = activity.name
        activity_entry = (app_id, activity_name)

        await activity.delete()
        del self.activities[activity_entry]
        del self.activities_by_id[activity.id]

    @async_auto_call_manager(execute=True)
    @logging_before_and_after(logging_level=logger.info)
    async def update_activity(self,
                              menu_path: Optional[str] = None, app_id: Optional[str] = None,
                              activity_name: Optional[str] = None, activity_id: Optional[str] = None,
                              new_activity_name: Optional[str] = None, settings: Optional[Dict] = None) -> Dict:
        """
        Update an activity by its name
        :param menu_path: the menu path of the app where the activity is located
        :param app_id: the id of the app where the activity is located
        :param activity_name: the name of the activity
        :param activity_id: the id of the activity
        :param new_activity_name: the new name of the activity
        :param settings: the default settings of the activity
        :return: the updated activity as a dictionary
        """
        app_id = await self._resolve_app_id(menu_path=menu_path, app_id=app_id)
        activity = await self._get_activity(app_id=app_id, activity_id=activity_id, activity_name=activity_name)
        activity_name = activity.name
        activity_entry = (app_id, activity_name)

        await activity.update(new_name=new_activity_name, settings=settings)

        if new_activity_name is not None:
            self.activities[(app_id, new_activity_name)] = activity
            del self.activities[activity_entry]

        return activity.to_dict()

    @async_auto_call_manager(execute=True)
    @logging_before_and_after(logging_level=logger.info)
    async def execute_activity(self, menu_path: Optional[str] = None, app_id: Optional[str] = None,
                               activity_name: Optional[str] = None, activity_id: Optional[str] = None,
                               settings: Union[Dict, str] = None) -> Dict:
        """
        Execute an activity by its name and menu path
        :param menu_path: the menu path of the app where the activity is located
        :param app_id: the id of the app where the activity is located
        :param activity_name: the name of the activity
        :param activity_id: the id of the activity
        :param settings: the settings of the run, or the id of the run to clone settings from
        :return: the run of the activity as a dictionary
        """
        activity = await self._get_activity(menu_path=menu_path, app_id=app_id,
                                            activity_name=activity_name, activity_id=activity_id)
        run = await activity.create_new_run(settings=settings)
        result = await run.execute()
        await run
        logger.info(f'Activity {activity_name if activity_name else activity_id} executed with result {result}')
        return run.to_dict()

    @async_auto_call_manager(execute=True)
    @logging_before_and_after(logging_level=logger.info)
    async def get_activity(self, menu_path: Optional[str] = None, app_id: Optional[str] = None,
                           activity_name: Optional[str] = None, activity_id: Optional[str] = None,
                           pretty_print: bool = False, how_many_runs: int = -1) -> Dict:
        """
        Get an activity by its name
        :param menu_path: the menu path of the app where the activity is located
        :param app_id: the id of the app where the activity is located
        :param activity_name: the name of the activity
        :param activity_id: the id of the activity
        :param pretty_print: if True, the activity is printed in a pretty format
        :param how_many_runs: how many runs to get
        :return: the activity as a dictionary
        """
        activity = await self._get_activity(
            menu_path=menu_path, activity_name=activity_name,
            app_id=app_id, activity_id=activity_id,
            how_many_runs=how_many_runs
        )
        if pretty_print:
            print(json.dumps(activity.to_dict(), indent=2))

        return activity.to_dict()

    @async_auto_call_manager(execute=True)
    @logging_before_and_after(logging_level=logger.info)
    async def get_activities(self, menu_path: Optional[str] = None, app_id: Optional[str] = None, pretty_print: bool = False,
                             print_names: bool = False, how_many_runs: int = -1) -> List[Dict]:
        """
        Get the list of activities in the app
        :param menu_path: the menu path of the app
        :param app_id: the id of the app
        :param pretty_print: if True, the activities are printed in a pretty format
        :param print_names: if True and pretty_print is False, only the names of the activities are printed
        :param how_many_runs: how many runs to get
        :return: a list of activities as dictionaries
        """

        app_id: str = await self._resolve_app_id(menu_path=menu_path, app_id=app_id)

        self._clear_local_activities()
        await self._get_business_activities()

        activity_tasks = [self._get_activity(app_id=app_id, activity_name=activity.name, how_many_runs=how_many_runs)
                          for (activity_app_id, _), activity in self.activities.items() if activity_app_id == app_id]

        activities = [activity.to_dict() for activity in await asyncio.gather(*activity_tasks)]

        if pretty_print:
            print(json.dumps(activities, indent=2))
        elif print_names:
            logger.info(f'Activities available in the business: '
                        f'{", ".join([activity["app_id"]+"/"+activity["name"] for activity in activities])}')

        return activities

    @async_auto_call_manager(execute=True)
    @logging_before_and_after(logging_level=logger.info)
    async def create_run(self, menu_path: Optional[str] = None, app_id: Optional[str] = None,
                         activity_name: Optional[str] = None, activity_id: Optional[str] = None,
                         settings: Union[Dict, str] = None) -> Dict[str, Any]:
        """
        Create a run for an activity by its name
        :param menu_path: the menu path of the app where the activity is located
        :param app_id: the id of the app where the activity is located
        :param activity_name: the name of the activity
        :param activity_id: the id of the activity
        :param settings: the settings of the run, or the id of the run to clone settings from
        :return: the run created as a dictionary
        """

        activity = await self._get_activity(menu_path=menu_path, app_id=app_id,
                                            activity_name=activity_name, activity_id=activity_id)

        run = await activity.create_new_run(settings=settings)

        if menu_path is not None:
            app_name, _ = self._clean_menu_path(menu_path=menu_path)

        logger.info(f'New run with id {run.id} created for activity {activity_name if activity_name else activity_id}'
                    f' in app {app_id if app_id else app_name}.')
        return run.to_dict()

    @async_auto_call_manager(execute=True)
    @logging_before_and_after(logging_level=logger.info)
    async def execute_run(self, run_id: str,
                          menu_path: Optional[str] = None, app_id: Optional[str] = None,
                          activity_name: Optional[str] = None, activity_id: Optional[str] = None):
        """
        Execute a run by its id
        :param menu_path: the menu path of the app where the activity is located
        :param app_id: the id of the app where the activity is located
        :param activity_name: the name of the activity
        :param activity_id: the id of the activity
        :param run_id: the id of the run
        :return:
        """
        activity = await self._get_activity(menu_path=menu_path, app_id=app_id,
                                            activity_name=activity_name, activity_id=activity_id)
        run = await activity.get_run(run_id=run_id)
        result = await run.execute()
        await run
        logger.info(f'Run with id {run_id} executed with result {result}')

    @async_auto_call_manager(execute=True)
    @logging_before_and_after(logging_level=logger.info)
    async def create_run_log(self, run_id: str, message: str, severity: Optional[str] = 'INFO',
                             tags: Optional[Dict[str, str]] = None,
                             menu_path: Optional[str] = None, app_id: Optional[str] = None,
                             activity_name: Optional[str] = None, activity_id: Optional[str] = None,
                             pretty_print: bool = False) -> Dict[str, str]:
        """
        Create a log for a run by its id
        :param menu_path: the menu path of the app where the activity is located
        :param app_id: the id of the app where the activity is located
        :param activity_name: the name of the activity
        :param activity_id: the id of the activity
        :param run_id: the id of the run
        :param message: the message to log
        :param severity: the severity of the log
        :param tags: the tags of the log
        :param pretty_print: if True, the log is printed in a pretty format
        :return:
        """
        activity = await self._get_activity(menu_path=menu_path, app_id=app_id,
                                            activity_name=activity_name, activity_id=activity_id)
        run = await activity.get_run(run_id=run_id)
        log = await run.create_log(message=message, severity=severity, tags=tags if tags else {})

        if pretty_print:
            print(json.dumps(log, indent=2))

        return log

    @async_auto_call_manager(execute=True)
    @logging_before_and_after(logging_level=logger.info)
    async def get_run_settings(self, run_id: str,
                               menu_path: Optional[str] = None, app_id: Optional[str] = None,
                               activity_name: Optional[str] = None, activity_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Get the settings of a run by its id
        :param menu_path: the menu path of the app where the activity is located
        :param app_id: the id of the app where the activity is located
        :param activity_name: the name of the activity
        :param activity_id: the id of the activity
        :param run_id: the id of the run
        :return: the settings of the run as a dictionary
        """

        activity = await self._get_activity(menu_path=menu_path, app_id=app_id,
                                            activity_name=activity_name, activity_id=activity_id)
        run = await activity.get_run(run_id=run_id)
        return run.settings

    @async_auto_call_manager(execute=True)
    @logging_before_and_after(logging_level=logger.info)
    async def get_run_logs(self, run_id: str,
                           menu_path: Optional[str] = None, app_id: Optional[str] = None,
                           activity_name: Optional[str] = None, activity_id: Optional[str] = None) \
            -> List[Dict[str, Any]]:
        """
        Get the logs of a run by its id
        :param menu_path: the menu path of the app where the activity is located
        :param app_id: the id of the app where the activity is located
        :param activity_name: the name of the activity
        :param activity_id: the id of the activity
        :param run_id: the id of the run
        :return: the logs of the run as a list of dictionaries
        """

        activity = await self._get_activity(menu_path=menu_path, app_id=app_id,
                                            activity_name=activity_name, activity_id=activity_id)
        run = await activity.get_run(run_id=run_id)
        return await run.get_logs()

    @logging_before_and_after(logging_level=logger.info)
    def button_execute_activity(
            self, order: int, label: str,
            activity_name: Optional[str] = None, activity_id: Optional[str] = None,
            menu_path: Optional[str] = None, app_id: Optional[str] = None,
            rows_size: Optional[int] = 1, cols_size: Optional[int] = 2,
            align: Optional[str] = 'stretch',
            padding: Optional[str] = None, bentobox_data: Optional[Dict] = None,
            tabs_index: Optional[Tuple[str, str]] = None
    ):
        """
        Create an execute button report in the dashboard for the activity.
        :param activity_name: the name of the activity
        :param order: the order of the button in the dashboard
        :param menu_path: the menu path of the app to which the activity belongs
        :param label: the name of the button to be clicked
        :param rows_size: the number of rows of the button
        :param cols_size: the number of columns of the button
        :param align: the alignment of the button
        :param padding: the padding of the button
        :param bentobox_data: the bentobox metadata for FE
        :param tabs_index: the index of the tab in the dashboard
        :return:
        """
        # TODO: handle this correctly, this solution is a bottleneck

        activity = self.get_activity(menu_path=menu_path, app_id=app_id,
                                     activity_name=activity_name, activity_id=activity_id)

        self._plot_api.button(
            menu_path=menu_path,
            order=order, label=label,
            rows_size=rows_size, cols_size=cols_size,
            align=align,
            padding=padding,
            bentobox_data=bentobox_data,
            tabs_index=tabs_index,
            on_click_events=[
                {
                    "action": "runActivity",
                    "params": {
                        "activityId": activity['id'],
                    }
                }
            ]
        )
