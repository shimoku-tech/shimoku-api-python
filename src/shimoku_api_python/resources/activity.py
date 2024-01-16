import datetime
import datetime as dt

import asyncio
import json

from typing import List, Dict, Optional, Union, TYPE_CHECKING, TypedDict, Any

from ..base_resource import Resource

if TYPE_CHECKING:
    from .app import App

import logging
from ..execution_logger import logging_before_and_after, log_error
logger = logging.getLogger(__name__)


class Activity(Resource):
    """
    A class that contains all the information necessary to create and run an activity.
    """

    resource_type = 'activity'
    alias_field = 'name'
    plural = 'activities'

    class ActivityParams(TypedDict):
        name: Optional[str]
        settings: dict
        activityTemplateWithMode: Optional[dict]
        universeApiKeyId: Optional[str]

    class Run(Resource):
        """
        Run of an activity, which is a single execution of the activity.
        """

        resource_type = 'run'
        plural = 'runs'

        class Log(Resource):
            """
            Log of an activity run.
            """

            resource_type = 'log'
            plural = 'logs'

            @logging_before_and_after(logging_level=logger.debug)
            def __init__(self, parent: 'Activity.Run', uuid: Optional[str] = None, db_resource: Optional[Dict] = None):

                params = dict(
                    dateTime=str(dt.datetime.now().isoformat())[:-3] + "Z",
                    message='message',
                    severity='INFO',
                    tags={},
                )

                super().__init__(parent=parent, uuid=uuid, db_resource=db_resource,
                                 check_params_before_creation=['message', 'severity'],
                                 params_to_serialize=['tags'], params=params)

        @logging_before_and_after(logging_level=logger.debug)
        def __init__(self, parent: 'Activity', uuid: Optional[str] = None, db_resource: Optional[Dict] = None):

            params = dict(
                settings={},
            )

            super().__init__(parent=parent, uuid=uuid, db_resource=db_resource, children=[Activity.Run.Log],
                             params_to_serialize=['settings'], params=params)

        @logging_before_and_after(logging_level=logger.debug)
        async def create_log(self, message: str, severity: str, tags: Dict[str, str]) -> 'Activity.Run.Log':
            """
            Creates a log for the activity run.
            :param message: The message of the log.
            :param severity: The severity of the log.
            :param tags: The tags of the log.
            :return: The created log.
            """
            if tags and (not isinstance(tags, Dict) or any([not isinstance(key, str) or not isinstance(value, str)
                                                            for key, value in tags.items()])):
                log_error(logger, 'The tags must be a dictionary of strings.', ValueError)

            return await self._base_resource.create_child(Activity.Run.Log,
                                                          message=message, severity=severity, tags=tags)

        @logging_before_and_after(logging_level=logger.debug)
        async def get_log(self, uuid: str) -> Optional['Activity.Run.Log']:
            """
            Gets a log of the activity run.
            :param uuid: The uuid of the log.
            :return: The log.
            """
            return await self._base_resource.get_child(Activity.Run.Log, uuid)

        @logging_before_and_after(logging_level=logger.debug)
        async def get_logs(self) -> List['Activity.Run.Log']:
            """
            Gets all the logs of the activity run.
            :return: The logs.
            """
            logs = await self._base_resource.get_children(Activity.Run.Log)
            return sorted(logs, key=lambda log: log['dateTime'])

        @logging_before_and_after(logging_level=logger.debug)
        async def trigger_webhook(self):
            """
            Triggers the webhook of the activity in a run.
            """
            endpoint = self._base_resource.base_url + f'run/{self._base_resource.id}/triggerWebhook'

            response = await(
                self._base_resource.api_client.query_element(
                    method='POST', endpoint=endpoint,
                )
            )

            return response['STATUS']

        @logging_before_and_after(logging_level=logger.debug)
        def cascade_to_dict(self) -> Dict[str, Any]:
            """
            Returns the run as a dictionary.
            :return: The run as a dictionary.
            """
            run_dict = super().cascade_to_dict()
            run_dict['logs'] = sorted(run_dict['logs'], key=lambda log: log['dateTime'])
            return run_dict

    @staticmethod
    def _runs_ordering(run: 'Activity.Run') -> dt.datetime:
        """ Returns the datetime of the last log of the run. Used for sorting runs.
        :param run: The run.
        :return: The datetime of the last log of the run.
        """
        logs = run._base_resource.children[Activity.Run.Log]
        if len(logs) > 0:
            return max([
                dt.datetime.strptime(log['dateTime'], "%Y-%m-%dT%H:%M:%S.%fZ")
                if log['dateTime'] else dt.datetime.min
                for log_id, log in logs
            ])
        else:
            return dt.datetime.min

    @staticmethod
    @logging_before_and_after(logging_level=logger.debug)
    async def sort_runs_by_log_time(runs: List['Activity.Run']) -> List['Activity.Run']:
        """ Returns the runs ordered by the datetime of the last log of the run.
        :param runs: The runs.
        :return: The runs ordered by the datetime of the last log of the run.
        """
        await asyncio.gather(*[run.get_logs() for run in runs])
        return sorted(runs, key=Activity._runs_ordering)

    @logging_before_and_after(logging_level=logger.debug)
    def __init__(self, parent: 'App', uuid: Optional[str] = None, alias: Optional[str] = None,
                 db_resource: Optional[Dict] = None):

        params: Activity.ActivityParams = dict(
            name=alias,
            settings={},
            activityTemplateWithMode=None,
            universeApiKeyId=None,
        )

        super().__init__(
            parent=parent, uuid=uuid, db_resource=db_resource, params=params,
            children=[Activity.Run], check_params_before_creation=['name'],
            params_to_serialize=['settings'],

        )

    @logging_before_and_after(logging_level=logger.debug)
    async def delete(self):
        """ Deletes the activity. """
        return await self._base_resource.delete()

    @logging_before_and_after(logging_level=logger.debug)
    async def update(self):
        """ Updates the activity. """
        return await self._base_resource.update()

    # Webhook methods
    @logging_before_and_after(logging_level=logger.debug)
    async def create_webhook(self, url: str, method: str, headers: Dict[str, str]):
        """ Creates a webhook for the activity.
        :param url: The url of the webhook.
        :param method: The method of the webhook.
        :param headers: The headers of the webhook.
        """
        if not headers:
            headers = {}
        if not isinstance(headers, Dict) or any([not isinstance(key, str) or not isinstance(value, str)
                                                for key, value in headers.items()]):
            log_error(logger, 'The headers must be a dictionary of strings.', ValueError)

        endpoint = self._base_resource.base_url + f'activity/{self._base_resource.id}/webhook'
        params = dict(
            url=url,
            method=method,
            headers=json.dumps(headers),
        )
        await self._base_resource.api_client.query_element(
            method='POST', endpoint=endpoint,
            **{'body_params': params}
        )

    # Run methods
    @logging_before_and_after(logging_level=logger.debug)
    async def get_run(self, uuid: str) -> Optional['Activity.Run']:
        """ Gets a run of the activity.
        :param uuid: The uuid of the run.
        :return: The run.
        """
        return await self._base_resource.get_child(Activity.Run, uuid)

    @logging_before_and_after(logging_level=logger.debug)
    async def get_runs(self, how_many_runs: Optional[int] = None) -> List['Activity.Run']:
        """ Gets the last runs of the activity.
        :param how_many_runs: The number of runs to get.
        :return: The runs.
        """
        runs = await Activity.sort_runs_by_log_time(await self._base_resource.get_children(Activity.Run))
        return runs[-how_many_runs:] if how_many_runs is not None else runs

    @logging_before_and_after(logging_level=logger.debug)
    async def create_run(self, settings: Optional[Union[Dict, str]] = None) -> 'Activity.Run':
        """ Creates a run of the activity.
        :param settings: The settings of the run or id of the run to copy the settings from.
        :return: The run.
        """
        if isinstance(settings, str):
            settings = (await self.get_run(settings))['settings']
            assert isinstance(settings, dict)

        return await self._base_resource.create_child(Activity.Run, settings=settings)
