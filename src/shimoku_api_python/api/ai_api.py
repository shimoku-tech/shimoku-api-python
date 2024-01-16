import asyncio
from typing import Optional, List, Dict, Tuple, Union, Any

from copy import copy

from ..resources.app import App
from ..resources.universe import Universe
from ..resources.activity import Activity
from ..resources.file import File
from ..resources.activity_template import ActivityTemplate
from ..async_execution_pool import async_auto_call_manager, ExecutionPoolContext
from ..exceptions import AIFunctionError, ShimokuFileError, ActivityError

import logging
from shimoku_api_python.execution_logger import logging_before_and_after, log_error

logger = logging.getLogger(__name__)


@logging_before_and_after(logging_level=logger.debug)
def check_app_is_set(self: Union['AiApi', 'AIFunctionMethods']):
    """ Check that the app is set """
    if self._app is None:
        log_error(logger, 'Menu path not set. Please use set_menu_path() method first.', AttributeError)


@logging_before_and_after(logging_level=logger.debug)
def get_model_metadata(model: File) -> dict:
    """ Get the metadata of a model
    :param model: Model
    :return: The metadata of the model
    """
    metadata: dict = copy(model['metadata'])
    for tag in model['tags']:
        if tag.startswith('creator_ai_function_version:'):
            metadata['creator_ai_function_version'] = tag[len('creator_ai_function_version:'):]
        elif tag.startswith('creator_ai_function_id'):
            metadata['creator_ai_function_id'] = tag[len('creator_ai_function_id:'):]
        elif tag.startswith('creator_ai_function'):
            metadata['creator_ai_function'] = tag[len('creator_ai_function:'):]
    return metadata


@logging_before_and_after(logging_level=logger.debug)
def get_output_file_metadata(file: File):
    """ Get the metadata of an output file
    :param file: File
    :return: The metadata of the output file
    """
    metadata: dict = copy(file['metadata'])
    for tag in file['tags']:
        if tag.startswith('creator_ai_function_version:'):
            metadata['creator_ai_function_version'] = tag[len('creator_ai_function_version:'):]
        elif tag.startswith('creator_ai_function:'):
            metadata['creator_ai_function'] = tag[len('creator_ai_function:'):]
        elif tag.startswith('model_name:'):
            metadata['model_name'] = tag[len('model_name:'):]
    return metadata


@logging_before_and_after(logging_level=logger.debug)
def get_output_file_name(
        activity_template: ActivityTemplate, file_name: str, run_id: str
) -> str:
    """ Get the name of an output file of a ai_function
    :param activity_template: Activity template of the ai_function
    :param file_name: Name of the file
    :param run_id: Id of the run
    :return: The name of the output file
    """
    name = activity_template['name']
    version = activity_template['version']
    return f"shimoku_generated_output_file_{name}_{version}_{run_id}_{file_name}"


@logging_before_and_after(logging_level=logger.debug)
def get_input_file_name(file_name: str):
    """ Get the name of an input file of a ai_function
    :param file_name: Name of the file
    :return: The name of the input file
    """
    return f"shimoku_generated_input_file_{file_name}"


@logging_before_and_after(logging_level=logger.debug)
async def check_and_get_model(app: App, model_name: str) -> File:
    """ Check that a model exists and get it
    :param app: App
    :param model_name: Name of the model
    """
    app_files = await app.get_files()
    for file in app_files:
        if 'shimoku_generated' not in file['tags'] or 'ai_model' not in file['tags']:
            continue
        metadata = get_model_metadata(file)
        if file['name'] == "shimoku_generated_model_" + model_name and metadata['model_name'] == model_name:
            return file
    log_error(logger, f"The model ({model_name}) does not exist", ShimokuFileError)


class AIFunctionMethods:

    def __init__(
            self, app: App, activity_template: ActivityTemplate,
            run_id: str, execution_pool_context: ExecutionPoolContext
    ):
        self._app: App = app
        self._private_ai_function: ActivityTemplate = activity_template
        self._run_id: str = run_id
        self.epc = execution_pool_context

    @logging_before_and_after(logging_level=logger.debug)
    async def _create_output_file(
            self, activity_template: ActivityTemplate, file_name: str,
            file: Union[bytes, Tuple[bytes, dict]], run_id: str, model_name: Optional[str] = None
    ) -> str:
        """ Create an output file of a ai_function
        :param activity_template: Activity template of the ai_function
        :param file: File to be uploaded
        :param run_id: Id of the run
        :return: The uuid of the created file
        """
        metadata = {}
        if isinstance(file, tuple):
            file, metadata = file

        complete_file_name = get_output_file_name(activity_template, file_name, run_id)

        tags = ['shimoku_generated', 'ai_output_file',
                f'creator_ai_function:{activity_template["name"]}',
                f'creator_ai_function_version:{activity_template["version"]}']
        if model_name is not None:
            tags.append(f'model_name:{model_name}')

        file = await self._app.create_file(
            name=complete_file_name, file_object=file, tags=tags,
            metadata={
                'file_name': file_name,
                'run_id': run_id,
                **metadata
            }
        )
        logger.info(f'Created output file ({file_name})')
        return file['id']

    @async_auto_call_manager(execute=True)
    @logging_before_and_after(logging_level=logger.info)
    async def create_model(
            self, model_name: str, model: bytes, metadata: Optional[dict] = None
    ):
        """ Create a model
        :param model_name: Name of the model
        :param model: Model to be uploaded
        :param metadata: Metadata of the model
        """
        if not model_name or not isinstance(model_name, str):
            log_error(logger, 'Model name has to be a non-empty string', ValueError)

        file_name = f"shimoku_generated_model_{model_name}"

        check_app_is_set(self)
        await self._app.create_file(
            name=file_name, file_object=model,
            tags=[
                'shimoku_generated', 'ai_model',
                f"creator_ai_function:{self._private_ai_function['name']}",
                f"creator_ai_function_version:{self._private_ai_function['version']}",
                f"creator_ai_function_id:{self._private_ai_function['id']}"
            ],
            metadata={
                'model_name': model_name,
                'run_id': self._run_id,
                **(metadata or {})
            }
        )
        logger.info(f'Created model ({model_name})')

    @async_auto_call_manager(execute=True)
    @logging_before_and_after(logging_level=logger.info)
    async def get_model(
            self, model_name: str
    ) -> Tuple[bytes, dict]:
        """ Get a model
        :param model_name: Name of the model
        :return: The model if it exists
        """
        check_app_is_set(self)
        model_file: File = await check_and_get_model(self._app, model_name)
        return await self._app.get_file_object(model_file['id']), get_model_metadata(model_file)

    @async_auto_call_manager(execute=True)
    @logging_before_and_after(logging_level=logger.info)
    async def create_output_files(
            self, files: Dict[str, Union[bytes, Tuple[bytes, dict]]], model_name: Optional[str] = None,
    ):
        """ Create output files of a ai_function
        :param files: Files to be uploaded
        :param model_name: Name of the model used
        """
        check_app_is_set(self)
        if model_name is not None:
            await check_and_get_model(self._app, model_name)
        else:
            model_name = ''

        await asyncio.gather(*[
            self._create_output_file(self._private_ai_function, file_name, file, self._run_id, model_name)
            for file_name, file in files.items()
        ])


class AiApi:

    @logging_before_and_after(logging_level=logger.debug)
    def __init__(
            self, access_token: str, universe: Universe, app: App,
            execution_pool_context: ExecutionPoolContext,
    ):
        self._app: App = app
        self._universe: Universe = universe
        self._access_token: str = access_token
        self._private_ai_function_and_run_id: Optional[Tuple[ActivityTemplate, str]] = None
        if app is not None and universe['id'] != app.parent.parent['id']:
            log_error(
                logger,
                f"Menu path ({str(app)}) does not belong to the universe ({str(universe)})",
                AIFunctionError
            )
        self.epc = execution_pool_context

    @logging_before_and_after(logging_level=logger.debug)
    async def _get_universe_api_key(self, universe_api_key: Optional[str]) -> str:
        """ Get the universe API key or create one if none exists
        :param universe_api_key: Optional universe API key
        :return: Universe API key
        """
        if universe_api_key is None:
            universe_api_keys = await self._universe.get_universe_api_keys()
            if len(universe_api_keys) == 0:
                return (await self._universe.create_universe_api_key('AI functions key'))['id']
            return universe_api_keys[0]['id']
        return universe_api_key

    @logging_before_and_after(logging_level=logger.debug)
    async def _get_activity_template(self, name: str, version: Optional[str]) -> ActivityTemplate:
        """ Get an activity template
        :param name: Name of the activity template
        :param version: Version of the activity template
        :return: Activity template
        """
        if version is not None:
            activity_template = await self._universe.get_activity_template(name_version=(name, version))
        else:
            activity_templates = await self._universe.get_activity_templates()
            activity_templates = [activity_template for activity_template in activity_templates
                                  if activity_template['name'] == name]
            activity_template = activity_templates[-1] if len(activity_templates) > 0 else None
        if activity_template is None:
            log_error(
                logger,
                f"The AI function ({name} {'v' + (version if version is not None else '')}) does not exist",
                AIFunctionError
            )
        return activity_template

    @logging_before_and_after(logging_level=logger.debug)
    async def _get_activity_from_template(
            self, activity_template: ActivityTemplate,
            universe_api_key: Optional[str] = None, create_if_not_exists: bool = True
    ) -> Activity:
        """ Get an activity from an activity template
        :param activity_template: Activity template
        :param universe_api_key: Universe API key
        :return: Activity
        """
        universe_api_key = await self._get_universe_api_key(universe_api_key)

        check_app_is_set(self)

        name = activity_template['name']
        activity_name = 'shimoku_generated_activity_' + name

        activity: Optional[Activity] = await self._app.get_activity(name=activity_name)
        if activity is None:
            if not create_if_not_exists:
                log_error(logger, f"The activity for the AI function ({name}) does not exist", AIFunctionError)
            activity: Activity = await self._app.create_activity(
                name=activity_name,
                template_id=activity_template['id'],
                universe_api_key=universe_api_key
            )
            logger.info(f'Created activity for ai_function {name}')

        return activity

    @logging_before_and_after(logging_level=logger.debug)
    async def _check_run_id_exists(self, activity_template: ActivityTemplate, run_id: str):
        """ Check if a run ID exists for the activity of a ai_function
        :param activity_template: Activity template to check
        :param run_id: ID of the run to check
        """
        activity: Activity = await self._get_activity_from_template(activity_template, create_if_not_exists=False)
        if not await activity.get_run(run_id):
            log_error(
                logger,
                f"Run ({run_id}) does not exist for the activity ({activity_template['name']})",
                ActivityError
            )

    @async_auto_call_manager(execute=True)
    @logging_before_and_after(logging_level=logger.info)
    async def check_for_private_access(self, ai_function_id: str, run_id: str):
        """ Check if the credentials allow for private ai_function methods """
        universe_api_keys = [uak['id'] for uak in await self._universe.get_universe_api_keys()]
        if self._access_token not in universe_api_keys:
            log_error(
                logger,
                f"The access key must be a universe API key to use private AI function methods",
                AIFunctionError
            )

        activity_template: ActivityTemplate = await self._universe.get_activity_template(ai_function_id)

        check_app_is_set(self)
        await self._check_run_id_exists(activity_template, run_id)

        self._private_ai_function_and_run_id = (activity_template, run_id)

    @logging_before_and_after(logging_level=logger.info)
    def get_private_ai_function_methods(self) -> AIFunctionMethods:
        """ Get the private ai_function methods if the credentials allow for it """
        if not self._private_ai_function_and_run_id:
            log_error(
                logger,
                "Credentials must be set to use private AI function methods, "
                "please call check_for_private_access first",
                AIFunctionError
            )
        activity_template, run_id = self._private_ai_function_and_run_id
        return AIFunctionMethods(self._app, activity_template, run_id, self.epc)

    @logging_before_and_after(logging_level=logger.debug)
    def _add_input_params_to_message(self, params: Dict[str, dict]):
        """ Add the parameters to a message
        :param params: Parameters to add
        :param message: Message to add the parameters to
        """
        message = []
        for param_name, param in params.items():
            message.append(f"\033[1m- {param_name}"
                           f"{' (Optional)' if not param['mandatory'] else ''}:\033[0m {param['datatype']}")
            if param['description']:
                message.append(f"  {param['description']}")
        return message

    @logging_before_and_after(logging_level=logger.debug)
    def _add_args_and_files_to_message(self, input_settings: Dict[str, dict]) -> List[str]:
        """ Add the args and files to a message
        :param input_settings: Input settings of the ai_function
        :param message: Message to add the args and files to
        """
        message = []
        input_files = {key: param for key, param in input_settings.items()
                       if isinstance(param, dict) and param['datatype'] == 'file'}
        input_args = {key: param for key, param in input_settings.items()
                      if isinstance(param, dict) and param['datatype'] != 'file'}
        message.append(f"--- args ---")
        message.extend(["  " + line for line in self._add_input_params_to_message(input_args)])
        message.append(f"--- files ---")
        message.extend(["  " + line for line in self._add_input_params_to_message(input_files)])
        return message

    @async_auto_call_manager(execute=True)
    @logging_before_and_after(logging_level=logger.info)
    async def show_available_ai_functions(self, show_input_parameters: bool = False):
        """ Show the available ai_functions
        :param show_input_parameters: Show the input parameters of each ai_function
        """
        message = [
            "",
            "///////////////////////////////////////////////////",
            "/////////////// Available ai_functions ///////////////",
        ]
        templates = await self._universe.get_activity_templates()
        while len(templates) > 0:
            template = templates.pop(0)
            if not template['enabled']:
                continue
            versions = [template['version']]
            while len(templates) > 0 and templates[0]['name'] == template['name']:
                template = templates.pop(0)
                versions.append(template['version'])
            message.append("")
            message.append(f" \033[1m- AI function:\033[0m {template['name']} (v{', v'.join(versions)})")
            message.append(
                f"   \033[1mDescription:\033[0m {template['description']} "
                f"(wait time between runs: >{template['minRunInterval']}s)"
            )
            if show_input_parameters:
                message.append(f"   \033[1mInput parameters:\033[0m")
                message.extend(["     " + line
                                for line in self._add_args_and_files_to_message(template['inputSettings'])])

        message.extend(["", "///////////////////////////////////////////////////", ""])
        print('\n'.join(message))

    @async_auto_call_manager(execute=True)
    @logging_before_and_after(logging_level=logger.info)
    async def show_ai_function_parameters(self, ai_function: str):
        """ Show the parameters of a ai_function
        :param ai_function: Name of the ai_function
        """
        template = await self._get_activity_template(ai_function, None)
        message = [
            "",
            "///////////////////////////////////////////////////",
            f" {ai_function} parameters ".center(51, '/'),
            "",
            f"  \033[1mDescription:\033[0m {template['description']} "
            f"(wait time between runs: >{template['minRunInterval']}s)",
            f"  \033[1mInput parameters:\033[0m"
        ]
        message.extend(["    " + line for line in self._add_args_and_files_to_message(template['inputSettings'])])

        message.extend(["", "///////////////////////////////////////////////////", ""])
        print('\n'.join(message))

    @async_auto_call_manager(execute=True)
    @logging_before_and_after(logging_level=logger.info)
    async def show_available_models(self):
        """ Show the available models """
        check_app_is_set(self)
        message = [
            "",
            "///////////////////////////////////////////////////",
            "//////////////// Available models /////////////////",
        ]
        app_files: List[File] = await self._app.get_files()
        model_files = [file for file in app_files if 'shimoku_generated' in file['tags'] and 'ai_model' in file['tags']]
        model_files = sorted(model_files, key=lambda file: file['metadata']['model_name'])
        for file in model_files:
            message.extend([
                '',
                f" \033[1m- Model name:\033[0m {file['metadata']['model_name']}",
                f"   \033[1mMetadata:\033[0m"
            ])
            for key, value in get_model_metadata(file).items():
                if key in ['model_name', 'creator_ai_function_version']:
                    continue
                message.append(f"     \033[1m- {key}:\033[0m {value}")

        message.extend(["", "///////////////////////////////////////////////////", ""])
        print('\n'.join(message))

    @async_auto_call_manager(execute=True)
    @logging_before_and_after(logging_level=logger.info)
    async def delete_model(self, model_name: str):
        """ Delete a model
        :param model_name: Name of the model
        """
        check_app_is_set(self)
        model_file: File = await check_and_get_model(self._app, model_name)
        await self._app.delete_file(model_file['id'])
        logger.info(f'Deleted model ({model_name})')

    @logging_before_and_after(logging_level=logger.debug)
    async def _get_runs_message(self, runs: List[Activity.Run], wf_input_settings: Union[dict, list]) -> List[str]:
        """ Get the output from a list of runs
        :param runs: List of runs
        :param wf_input_settings: Input settings of the ai_function/s
        :return: Message of the run
        """
        message = []
        # No need to use 'gather' here because logs are already cached from ordering the runs
        for i, run in enumerate(runs[::-1]):
            if isinstance(wf_input_settings, list):
                input_settings = wf_input_settings[i]
            else:
                input_settings = wf_input_settings
            run_settings = {k: v for k, v in run['settings'].items()
                            if k in input_settings and input_settings[k]['datatype'] != 'file'}
            message.extend([
                '',
                f' - Run {run["id"]}:',
                f'   Settings: {", ".join([f"{key}: {value}" for key, value in run_settings.items()])}',
                f'   Logs:',
                *[f'     - {log["severity"]} | {log["message"]}, at {log["dateTime"]}'
                  for log in (await run.get_logs())]
            ])

        message.extend(['', "///////////////////////////////////////////////////", ''])
        return message

    @async_auto_call_manager(execute=True)
    @logging_before_and_after(logging_level=logger.info)
    async def show_last_execution_logs_by_model(
            self, model_name: str, how_many: int = 1
    ):
        check_app_is_set(self)
        app_files: List[File] = await self._app.get_files()
        model_file: File = await check_and_get_model(self._app, model_name)
        model_metadata: dict = get_model_metadata(model_file)
        runs: List[Activity.Run] = []
        input_settings_by_run_id: Dict[str, dict] = {}
        for file in app_files:
            if 'shimoku_generated' not in file['tags'] or 'ai_output_file' not in file['tags']:
                continue
            output_file_metadata: dict = get_output_file_metadata(file)
            output_file_model_name = output_file_metadata.pop('model_name') if model_metadata else None
            if output_file_model_name == model_name:
                activity_template: ActivityTemplate = await self._get_activity_template(
                    output_file_metadata['creator_ai_function'],
                    output_file_metadata['creator_ai_function_version']
                )
                activity: Activity = await self._get_activity_from_template(
                    activity_template, create_if_not_exists=False
                )
                run_id = output_file_metadata['run_id']
                input_settings = activity_template['inputSettings']
                runs.append(await activity.get_run(run_id))
                input_settings_by_run_id[run_id] = input_settings
        runs = (await Activity.sort_runs_by_log_time(runs))[-how_many:]
        message = [
            '',
            '///////////////////////////////////////////////////',
            f' LOGS OF EXECUTIONS BY {model_name.upper()} '.center(51, '/')
        ]
        input_settings_list = [input_settings_by_run_id[run['id']] for run in runs]
        message.extend(await self._get_runs_message(runs, input_settings_list))
        print('\n'.join(message))

    @async_auto_call_manager(execute=True)
    @logging_before_and_after(logging_level=logger.info)
    async def show_last_execution_logs_by_ai_function(
            self, ai_function: str, version: Optional[str] = None, how_many: int = 1
    ):
        """ Show the logs of the executions of a ai_function
        :param ai_function: Name of the ai_function to execute
        :param version: Version of the ai_function to execute
        :param how_many: Number of executions to get
        """
        check_app_is_set(self)
        activity_template: ActivityTemplate = await self._get_activity_template(ai_function, version)
        input_settings = activity_template['inputSettings']
        activity: Activity = await self._get_activity_from_template(activity_template, create_if_not_exists=False)
        runs: List[Activity.Run] = await activity.get_runs(how_many)
        message = [
            '',
            '///////////////////////////////////////////////////',
            f' LOGS OF {ai_function.upper()} '.center(51, '/')
        ]
        message.extend(await self._get_runs_message(runs, input_settings))
        print('\n'.join(message))

    @async_auto_call_manager(execute=True)
    @logging_before_and_after(logging_level=logger.info)
    async def show_execution_logs(
            self, run_ids: list[str], ai_function: str, version: Optional[str] = None
    ):
        """ Show the logs of the executions of a ai_function
        :param run_ids: Ids of the runs to get
        :param ai_function: Name of the ai_function to execute
        :param version: Version of the ai_function to execute
        """
        check_app_is_set(self)
        activity_template: ActivityTemplate = await self._get_activity_template(ai_function, version)
        input_settings = activity_template['inputSettings']
        activity: Activity = await self._get_activity_from_template(activity_template, create_if_not_exists=False)
        runs: List[Activity.Run] = await asyncio.gather(*[activity.get_run(run_id) for run_id in run_ids])
        message = [
            '',
            '///////////////////////////////////////////////////',
            f' LOGS OF {ai_function.upper()} '.center(51, '/')
        ]
        message.extend(await self._get_runs_message(runs, input_settings))
        print('\n'.join(message))

    @async_auto_call_manager(execute=True)
    @logging_before_and_after(logging_level=logger.info)
    async def get_last_executions_with_logs(
            self, ai_function: str, version: Optional[str] = None, how_many: int = 1
    ):
        """ Get the logs of the executions of a ai_function
        :param ai_function: Name of the ai_function to execute
        :param version: Version of the ai_function to execute
        :param how_many: Number of executions to get
        :return: The logs of the ai_function
        """
        activity_template: ActivityTemplate = await self._get_activity_template(ai_function, version)
        activity: Activity = await self._get_activity_from_template(activity_template, create_if_not_exists=False)
        runs: List[Activity.Run] = await activity.get_runs(how_many)
        return [run.cascade_to_dict() for run in runs]

    @logging_before_and_after(logging_level=logger.debug)
    async def _check_and_store_output_file(
            self, file: File, files_by_run_id: List[dict], run_id: Optional[str] = None,
            model_metadata: Optional[dict] = None, activity_template: Optional[ActivityTemplate] = None,
            file_name: Optional[str] = None, get_objects: bool = False
    ):
        """ Check if a file is an output file then add it to the list of output files
        :param model_metadata: Metadata of the model used
        :param activity_template: ai_function used
        :param file: File to check
        :param files_by_run_id: Dictionary of output files by run ID
        :param run_id: ID of the run to check
        :param file_name: Name of the file to check
        :param get_objects: Get the objects of the files instead of their metadata
        """
        if 'shimoku_generated' not in file['tags'] or 'ai_output_file' not in file['tags']:
            return

        output_file_metadata: dict = {}
        aux_output_file_metadata: dict = get_output_file_metadata(file)
        output_file_metadata.update(aux_output_file_metadata)

        output_file_name: str = output_file_metadata.pop('file_name')
        output_file_model_name: Optional[str] = output_file_metadata.get('model_name')
        ai_function_name: str = output_file_metadata.pop('creator_ai_function')
        ai_function_version: str = output_file_metadata.pop('creator_ai_function_version')

        if ((activity_template and
             (ai_function_name != activity_template['name'] or ai_function_version != activity_template['version'])) or
                (model_metadata and output_file_model_name != model_metadata['model_name']) or
                (file_name and output_file_name != file_name)):
            return

        output_file_run_id: str = output_file_metadata.pop('run_id')
        if run_id and output_file_run_id != run_id:
            return

        run_metadata = {'run_id': output_file_run_id}
        if output_file_run_id not in [run['run_id'] for run in files_by_run_id]:
            if not model_metadata and output_file_model_name is not None:
                run_metadata.update({
                    'model_name': output_file_model_name
                })
            if not activity_template:
                run_metadata.update({
                    'ai_function_name': ai_function_name,
                    'ai_function_version': ai_function_version
                })
            run_metadata.update({
                'input': {'args': [], 'files': []},
                'output_files': {}
            })
            files_by_run_id.append(run_metadata)
        else:
            run_metadata = [run_d for run_d in files_by_run_id if run_d['run_id'] == output_file_run_id][0]

        if get_objects:
            output_file_metadata['object'] = await self._app.get_file_object(file['id'])

        output_file_metadata = {k: v for k, v in output_file_metadata.items()
                                if k not in ['creator_ai_function', 'creator_ai_function_version']}
        run_metadata['output_files'][output_file_name] = output_file_metadata

        await self._fill_run_metadata(run_metadata, output_file_run_id, ai_function_name, ai_function_version)

    @logging_before_and_after(logging_level=logger.debug)
    async def _fill_input_for_run_metadata(
            self, key: str, value: Any, args: dict, files: dict, input_settings: dict, app_files: List[File]
    ):
        """ Fill the files and args of a run metadata
        :param key: Key of the input
        :param value: Value of the input
        :param args: Args of the run metadata
        :param files: Files of the run metadata
        :param input_settings: Settings of the input
        :param app_files: Files of the app
        """
        if key not in input_settings:
            return
        if input_settings[key]['datatype'] == 'file':
            filtered_files: List[File] = [file for file in app_files if file['id'] == value]
            if len(filtered_files) > 1:
                log_error(logger, f"More than one file with ID {value} found", ValueError)
            elif len(filtered_files) == 0:
                value = '# file not found #'
            else:
                file = filtered_files[0]
                value = file['metadata']
            files[key] = value
        else:
            args[key] = value

    @logging_before_and_after(logging_level=logger.debug)
    async def _fill_run_metadata(
            self, run_metadata: dict, run_id: str, ai_function_name: str, ai_function_version: str
    ):
        """ Fill the metadata of a run
        :param run_metadata: Metadata of the run to fill
        :param run_id: ID of the run to fill
        :param ai_function_name: Name of the ai_function used
        :param ai_function_version: Version of the ai_function used
        """
        activity_template: ActivityTemplate = await self._get_activity_template(ai_function_name, ai_function_version)
        activity: Activity = await self._get_activity_from_template(activity_template, create_if_not_exists=False)
        activity_runs: List[Activity.Run] = await activity.get_runs()
        runs = [run for run in activity_runs if run['id'] == run_id]
        if len(runs) > 1:
            log_error(logger, f"More than one run with ID {run_id} found", ValueError)
        if len(runs) == 0:
            run_metadata['input'] = '# Run not found #'
            return
        run: Activity.Run = runs[0]
        input_settings = activity_template['inputSettings']
        args = {}
        files = {}
        await asyncio.gather(
            *[self._fill_input_for_run_metadata(k, v, args, files, input_settings, await self._app.get_files())
              for k, v in run['settings'].items()]
        )
        run_metadata['input']['args'] = args
        run_metadata['input']['files'] = files

    @async_auto_call_manager(execute=True)
    @logging_before_and_after(logging_level=logger.info)
    async def get_output_files_by_model(
            self, model_name: str, file_name: Optional[str] = None, get_objects: bool = False
    ):
        """ Get output files for the executions of ai_functions with a given model
        :param model_name: Name of the model to use
        :param file_name: Name of the file to get
        :param get_objects: Get the file objects instead of the file metadata
        :return: Dictionary of output files by the execution identifier
        """
        app_files: List[File] = await self._app.get_files()
        model_file: File = await check_and_get_model(self._app, model_name)
        model_metadata = get_model_metadata(model_file)

        files_by_run_id: List[dict] = []
        await asyncio.gather(*[
            self._check_and_store_output_file(
                file, files_by_run_id, model_metadata=model_metadata,
                file_name=file_name, get_objects=get_objects
            )
            for file in app_files
        ])
        return files_by_run_id

    @async_auto_call_manager(execute=True)
    @logging_before_and_after(logging_level=logger.info)
    async def get_output_files_by_ai_function(
            self, ai_function: str, version: Optional[str] = None,
            file_name: Optional[str] = None, get_objects: bool = False
    ):
        """ Get output files for a generic ai_function
        :param ai_function: Name of the ai_function to execute
        :param version: Version of the ai_function to execute
        :return: The output files if they exist
        :param file_name: Name of the file to get
        :param get_objects: Get the file objects instead of the file metadata
        """
        app_files: List[File] = await self._app.get_files()
        activity_template: ActivityTemplate = await self._get_activity_template(ai_function, version)

        files_by_run_id: List[dict] = []
        await asyncio.gather(*[
            self._check_and_store_output_file(
                file, files_by_run_id, activity_template=activity_template,
                file_name=file_name, get_objects=get_objects
            )
            for file in app_files
        ])
        return files_by_run_id

    @async_auto_call_manager(execute=True)
    @logging_before_and_after(logging_level=logger.info)
    async def get_output_file_objects(
            self, run_id: str, file_name: Optional[str] = None
    ) -> Union[tuple[bytes, dict], Dict[str, tuple[bytes, dict]]]:
        """ Get an output file object for a given ai_function and run id
        :param run_id: ID of the executed run
        :param file_name: Name of the file to get
        """
        app_files: List[File] = await self._app.get_files()
        files_by_run_id: List[dict] = []
        await asyncio.gather(*[
            self._check_and_store_output_file(file, files_by_run_id, run_id, file_name=file_name, get_objects=True)
            for file in app_files
        ])
        if len(files_by_run_id) == 0:
            log_error(logger, f"No output files found for run ({run_id})", AIFunctionError)

        output_files_by_name = files_by_run_id[0]['output_files']

        if file_name is None:
            return_dict = {}
            for file_name, file_dict in output_files_by_name.items():
                return_dict[file_name] = file_dict['object'], {k: v for k, v in file_dict.items() if k != 'object'}
            return return_dict

        if file_name not in output_files_by_name:
            log_error(logger, f'No output file ({file_name}) found for run ({run_id})', AIFunctionError)

        file_dict = output_files_by_name[file_name]
        return file_dict['object'], {k: v for k, v in file_dict.items() if k != 'object'}

    @logging_before_and_after(logging_level=logger.debug)
    async def _create_input_file(
            self, file_name: str, file: Union[Any, Tuple[Any, dict]], force_overwrite: bool = False
    ):
        """ Create an output file of an ai_function
        :param file_name: Name of the file to create
        :param file: File to be uploaded
        :param force_overwrite: Overwrite the file if it already exists
        """
        metadata = {}
        if isinstance(file, tuple):
            file, metadata = file

        complete_file_name = get_input_file_name(file_name)
        if not force_overwrite and await self._app.get_file(name=complete_file_name) is not None:
            log_error(
                logger,
                f'Input file ({file_name}) already exists, if you want to overwrite it, use force_overwrite=True',
                AIFunctionError
            )
        await self._app.create_file(
            name=complete_file_name, file_object=file,
            tags=['shimoku_generated', 'ai_input_file'],
            metadata={
                'file_name': file_name,
                **metadata
            },
        )
        logger.info(f'Created input file {file_name}')

    @logging_before_and_after(logging_level=logger.debug)
    async def _get_input_file(self, file_name: str) -> str:
        """ Get the ID of an input file
        :param file_name: Name of the file to get
        :return: ID of the file
        """
        file_name = get_input_file_name(file_name)
        input_file: Optional[File] = await self._app.get_file(name=file_name)

        if input_file is None:
            log_error(logger, f"Input file ({file_name}) not found", AIFunctionError)

        if input_file['tags'] != ['shimoku_generated', 'ai_input_file'] or 'file_name' not in input_file['metadata']:
            log_error(logger, f"File ({file_name}) is not an input file", AIFunctionError)

        return input_file['id']

    @async_auto_call_manager(execute=True)
    @logging_before_and_after(logging_level=logger.info)
    async def create_input_files(self, input_files: dict, force_overwrite: bool = False):
        """ Create input files for a ai_function
        :param input_files: Dictionary of input files to create
        :param force_overwrite: Force the overwrite of the files
        """
        check_app_is_set(self)
        await asyncio.gather(*[
            self._create_input_file(file_name, file, force_overwrite)
            for file_name, file in input_files.items()
        ])

    @logging_before_and_after(logging_level=logger.debug)
    async def _get_available_input_files(self) -> List[File]:
        """ Get available input files for a ai_function """
        app_files: List[File] = await self._app.get_files()
        input_files = [
            file for file in app_files if 'shimoku_generated' in file['tags'] and 'ai_input_file' in file['tags']
        ]
        return sorted(input_files, key=lambda x: x['metadata']['file_name'])

    @async_auto_call_manager(execute=True)
    @logging_before_and_after(logging_level=logger.info)
    async def get_available_input_files(self) -> List[dict]:
        """ Get available input files for a ai_function """
        check_app_is_set(self)
        return [file['metadata'] for file in await self._get_available_input_files()]

    @async_auto_call_manager(execute=True)
    @logging_before_and_after(logging_level=logger.info)
    async def delete_input_file(self, file_name: str):
        """ Delete an input file
        :param file_name: Name of the file to delete
        """
        check_app_is_set(self)
        file_id = await self._get_input_file(file_name)
        await self._app.delete_file(file_id)
        logger.info(f"Deleted input file {file_name}")

    @async_auto_call_manager(execute=True)
    @logging_before_and_after(logging_level=logger.info)
    async def show_available_input_files(self):
        """ Show the available input files """
        check_app_is_set(self)
        message = [
            "",
            "///////////////////////////////////////////////////",
            "///////////////// Available Files /////////////////",
        ]
        input_files = await self._get_available_input_files()
        for file in input_files:
            metadata = {k: v for k, v in file['metadata'].items() if k not in ['file_name']}
            message.extend([
                '',
                f" \033[1m- File name:\033[0m {file['metadata']['file_name']}",

            ])
            if metadata:
                message.extend([
                    f"   \033[1mMetadata:\033[0m",
                    *[f"     \033[1m- {k}:\033[0m {v}" for k, v in metadata.items()]
                ])

        message.extend(["", "///////////////////////////////////////////////////", ""])
        print('\n'.join(message))

    @logging_before_and_after(logging_level=logger.debug)
    async def _check_params(self, activity_template: ActivityTemplate, params: dict):
        """ Check the parameters passed to the ai_function, and create input files if necessary
        :param activity_template: Activity template of the ai_function
        :param params: Parameters to be passed to the ai_function
        """
        input_settings = activity_template['inputSettings']
        if any(param not in input_settings for param in params):
            log_error(
                logger,
                f"Unknown parameters for AI function ({activity_template['name']}): "
                f"{[param for param in params if param not in input_settings]} \n"
                f"The possible parameters are: {list(input_settings.keys())}",
                AIFunctionError
            )
        for param_name, definition in input_settings.items():
            if param_name not in params:
                if definition['mandatory']:
                    log_error(
                        logger,
                        f"Missing parameter ({param_name}) for AI function ({activity_template['name']}), "
                        f"the description of the missing parameter is: {definition['description']}",
                        AIFunctionError
                    )
                else:
                    continue
            param_value = params[param_name]
            param_definition_type = definition['datatype']
            if definition['datatype'] == 'file':
                if not isinstance(param_value, str):
                    log_error(
                        logger,
                        f'The parameter ({param_name}) is expected to be a reference name to an input file',
                        AIFunctionError
                    )
                params[param_name] = await self._get_input_file(param_value)
            elif definition['datatype'] == 'model':
                if not isinstance(param_value, str):
                    log_error(
                        logger,
                        f'The parameter ({param_name}) is expected to be a model name',
                        AIFunctionError
                    )
                if not await check_and_get_model(self._app, param_value):
                    log_error(
                        logger,
                        f'The model ({param_value}) does not exist',
                        AIFunctionError
                    )
            elif str(type(param_value)) != f"<class '{param_definition_type}'>":
                log_error(
                    logger,
                    f"Wrong type for parameter ({param_name}) for the AI function ({activity_template['name']})"
                    f"the description of the missing parameter is: {definition['description']}\n"
                    f"Expected type: {param_definition_type}\n"
                    f"Provided type: {str(type(param_value))[8:-2]}",
                    AIFunctionError
                )

    @async_auto_call_manager(execute=True)
    @logging_before_and_after(logging_level=logger.info)
    async def generic_execute(
            self, ai_function: str, version: Optional[str] = None,
            universe_api_key: Optional[str] = None, **params
    ):
        """ Execute a generic ai_function
        :param ai_function: Name of the ai_function to execute
        :param version: Version of the ai_function to execute
        :param universe_api_key: API key of the universe
        :param params: Parameters to be passed to the ai_function
        """
        activity_template: ActivityTemplate = await self._get_activity_template(ai_function, version)
        activity: Activity = await self._get_activity_from_template(activity_template, universe_api_key)
        await self._check_params(activity_template, params)
        run: Activity.Run = await activity.create_run(settings=params)
        logger.info(f'Response from execution trigger: {await run.trigger_webhook()}')
        return run['id']
