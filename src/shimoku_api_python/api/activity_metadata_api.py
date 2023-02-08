""""""

from abc import ABC

from shimoku_api_python.api.app_metadata_api import AppMetadataApi
from shimoku_api_python.api.business_metadata_api import BusinessMetadataApi
from shimoku_api_python.async_execution_pool import async_auto_call_manager

from typing import List, Dict, Optional, Union, Tuple, Any, Iterable, Callable

import asyncio

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
        async def _api_create_run_log(self):
            """
            Creates the log of the run on the server.
            """
            # TODO this should be handled by the structure of the SDK #
            endpoint: str = f'business/{self.activity.business_id}/' \
                            f'app/{self.activity.app_id}/' \
                            f'activity/{self.activity.id}/' \
                            f'run/{self.id}/' \
                            f'log'

            response = await(
                self.activity.api_client.query_element(
                    method='POST', endpoint=endpoint,
                )
            )
            ###########################################################
            return response['dateTime'], response['message'], response['severity']

        @logging_before_and_after(logging_level=logger.debug)
        async def _api_create_execution(self):
            """
            Creates the execution of the run on the server.
            """
            # TODO this should be handled by the structure of the SDK #
            endpoint: str = f'business/{self.activity.business_id}/' \
                            f'app/{self.activity.app_id}/' \
                            f'activity/{self.activity.id}/' \
                            f'run/{self.id}/' \
                            f'execute'

            response = await(
                self.activity.api_client.query_element(
                    method='POST', endpoint=endpoint,
                )
            )
            ###########################################################
            return response['STATUS']

        @logging_before_and_after(logging_level=logger.debug)
        async def _api_create_run(self, params: Dict[str, Any] = None):
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
                    **{'body_params': params}
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
        def __init__(self, activity, id=None):
            self.activity = activity
            self.id = id
            self.logs = []

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
            logs = [(log['dateTime'], log['message'], log['severity']) for log in logs['items']]
            logs.sort(key=lambda x: str(x[0]))
            return logs

        @logging_before_and_after(logging_level=logger.debug)
        async def _async_init(self):
            """
            Asynchonous initialization of the run, it's called when the run is awaited.
            It creates the run on the server.
            """
            if self.id:
                self.logs = await self._api_get_run_logs()
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
            }

        @logging_before_and_after(logging_level=logger.debug)
        async def run(self):
            """
            Executes the run and then returns the status of the run.
            """
            if self.id is None:
                error = 'The run has not been created yet. Make sure to await the run before running it.'
                logger.error(error)
                raise RuntimeError(error)

            status = await self._api_create_execution()

            return status

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
    def __init__(self, api_client, business_id: str, app_id: str, name: str, id: Optional[str] = None):
        # TODO this should be handled by the structure of the SDK #
        self.business_id: str = business_id
        self.app_id: Optional[str] = app_id
        self.api_client = api_client
        ###########################################################

        self.name: str = name
        self.id: str = id
        self.runs: Dict[str, Activity.Run] = {}

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
        if self.id:
            for run in (await self._api_get_runs()):
                self.runs[run['id']] = Activity.Run(activity=self, id=run['id'])

            await asyncio.gather(*[run for run in self.runs.values()])
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
            'runs': [run.to_dict() for run in self.runs.values()],
        }

    @logging_before_and_after(logging_level=logger.debug)
    async def create_new_run(self):
        """
        Creates a new run for the activity.
        """
        if self.id is None:
            error = 'The activity has not been created yet. Make sure to await the activity before creating a run.'
            logger.error(error)
            raise RuntimeError(error)

        run = await Activity.Run(self)
        self.runs[run.id] = run

    @logging_before_and_after(logging_level=logger.debug)
    async def execute_last_run(self):
        """
        Executes the last run of the activity.
        """
        if len(self.runs) == 0:
            error = 'There is no run to execute. Make sure to create a run before executing the activity.'
            logger.error(error)
            raise RuntimeError(error)

        return await list(self.runs.values())[-1].run()

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
    async def update(self, new_name: str):
        """
        Updates the activity from the business.
        """
        if self.id is None:
            error = 'The activity has not been created yet. Make sure to await the activity before updating it.'
            logger.error(error)
            raise RuntimeError(error)

        # TODO this should be handled by the structure of the SDK #
        endpoint: str = f'business/{self.business_id}/' \
                        f'app/{self.app_id}/' \
                        f'activity/{self.id}'

        item = {'name': new_name}

        await self.api_client.query_element(method='PUT', endpoint=endpoint, **{'body_params': item})
        ###########################################################

        self.name = new_name


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
        set_business_id: Set the business_id attribute.
        _create_activity: Create an activity in the business.
        _execute_activity: Execute an activity in the business.
        delete_activity: Delete an activity in the business.
        run_activity: Check if an activity has been created in the business, and if not, create it. Then, execute it.
    """
    @logging_before_and_after(logging_level=logger.debug)
    def __init__(self, api_client, app_metadata_api: AppMetadataApi, business_metadata_api: BusinessMetadataApi,
                 business_id: Optional[str] = None):
        self.api_client = api_client
        self.business_id: Optional[str] = business_id
        self.activities: Dict[(str, str), Activity] = {}
        self._app_metadata_api: AppMetadataApi = app_metadata_api
        self._business_metadata_api: BusinessMetadataApi = business_metadata_api
        self._get_business_activities()

    @logging_before_and_after(logging_level=logger.debug)
    def _get_business_activities(self):
        """
        Get the activities available in the business and store them in the activities attribute.
        The key of the dictionary is a tuple with the app id and the activity name.
        """
        activities = self._business_metadata_api.get_business_activities(self.business_id)
        for activity in activities:
            activity_entry = (activity['appId'], activity['name'])
            self.activities[activity_entry] = Activity(
                api_client=self.api_client, business_id=self.business_id,
                app_id=activity['appId'], name=activity['name'], id=activity['id']
            )

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

    @logging_before_and_after(logging_level=logger.info)
    def set_business(self, business_id: str):
        """
        Set the business id to which the activities belong. Test if the business exists.
        :param business_id: the UUID of the business
        :return:
        """
        # If the business id does not exists it raises an ApiClientError
        _ = self._business_metadata_api.get_business(business_id)
        self.activities = {}
        self.business_id = business_id
        self._get_business_activities()

    @async_auto_call_manager(execute=True)
    @logging_before_and_after(logging_level=logger.info)
    async def create_activity(self, menu_path:str, name: str):
        """
        Create an activity by its name and app id
        :param name: the name of the activity
        :param app_id: the UUID of the app to which the activity belongs
        :return:
        """
        app_name, _ = self._clean_menu_path(menu_path=menu_path)

        app: Dict = await self._app_metadata_api.get_or_create_app_and_apptype(name=app_name)
        app_id: str = app['id']

        self.activities[name] = await Activity(self.api_client, self.business_id, app_id, name)

    @async_auto_call_manager(execute=True)
    @logging_before_and_after(logging_level=logger.info)
    async def delete_activity(self, menu_path: str, name: str):
        """
        Delete an activity by its name
        :param name: the name of the activity
        :return:
        """
        app_name, _ = self._clean_menu_path(menu_path=menu_path)

        app: Dict = await self._app_metadata_api.get_or_create_app_and_apptype(name=app_name)
        app_id: str = app['id']
        activity_entry = (app_id, name)

        if activity_entry not in self.activities:
            error = f'Activity {name} does not exist in the app {app_name}'
            logger.error(error)
            raise ValueError(error)

        activity = self.activities[activity_entry]
        await activity.delete()
        del self.activities[activity_entry]

    @async_auto_call_manager(execute=True)
    @logging_before_and_after(logging_level=logger.info)
    async def create_run(self, menu_path: str, name: str):
        """
        Create a run for an activity by its name
        :param menu_path: the menu path of the app where the activity is located
        :param name: the name of the activity
        :return:
        """
        app_name, _ = self._clean_menu_path(menu_path=menu_path)

        app: Dict = await self._app_metadata_api.get_or_create_app_and_apptype(name=app_name)
        app_id: str = app['id']
        activity_entry = (app_id, name)

        if activity_entry not in self.activities:
            error = f'Activity {name} not found in app {app_name}.'
            logger.error(error)
            raise RuntimeError(error)

        activity = self.activities[activity_entry]
        await activity.create_new_run()

    @async_auto_call_manager()
    @logging_before_and_after(logging_level=logger.info)
    async def execute_activity(self, menu_path: str, name: str):
        """
        Execute an activity by its name and menu path
        :param menu_path: the menu path of the app where the activity is located
        :param name: the name of the activity
        :return:
        """

        app_name, _ = self._clean_menu_path(menu_path=menu_path)

        app: Dict = await self._app_metadata_api.get_or_create_app_and_apptype(name=app_name)
        app_id: str = app['id']
        activity_entry = (app_id, name)

        if activity_entry not in self.activities:
            error = f'Activity {name} not found in app {app_name}.'
            logger.error(error)
            raise RuntimeError(error)

        activity = self.activities[activity_entry]
        await activity.create_new_run()
        result = await activity.execute_last_run()
        logger.info(f'Activity {name} executed with result {result}')

    @async_auto_call_manager(execute=True)
    @logging_before_and_after(logging_level=logger.info)
    async def update_activity(self, menu_path: str, name: str, new_name: str):
        """
        Update an activity by its name
        :param menu_path: the menu path of the app where the activity is located
        :param name: the name of the activity
        :param new_name: the new name of the activity
        :return:
        """
        app_name, _ = self._clean_menu_path(menu_path=menu_path)

        app: Dict = await self._app_metadata_api.get_or_create_app_and_apptype(name=app_name)
        app_id: str = app['id']
        activity_entry = (app_id, name)

        if activity_entry not in self.activities:
            error = f'Activity {name} does not exist in the app {app_name}'
            logger.error(error)
            raise ValueError(error)

        activity = self.activities[activity_entry]
        await activity.update(new_name=new_name)
        self.activities[(app_id, new_name)] = activity
        del self.activities[activity_entry]

    @async_auto_call_manager(execute=True)
    @logging_before_and_after(logging_level=logger.info)
    async def get_activities(self) -> List[Dict]:
        """
        Get the list of activities in the business
        :return: a list of activities
        """

        await asyncio.gather(*[activity for activity in self.activities.values()])

        return [activity.to_dict() for activity in self.activities.values()]

