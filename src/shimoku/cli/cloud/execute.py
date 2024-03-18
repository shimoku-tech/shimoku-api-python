from typing import Optional
import threading

from shimoku.cli import CLIParser, CLIFuncParam
from shimoku.cli.cloud.cascade_get_resources import InitOptions, ResourceGetter
from shimoku.cli.utils import choose_from_menu

from shimoku.actions_execution.execute_action import execute_action_code

from shimoku.ai.ai_layer import get_activity_template, ActivityTemplate, AILayer
import logging

logger = logging.getLogger(__name__)


def add_execute_parser(parser: Optional[CLIParser] = None):
    """
    Function to add the get parser to a parser
    :param parser: Parser to add the get parser to
    :return: Get parser
    """
    params = {
        "name": "execute",
        "description": "Commands to execute activities",
    }
    if parser:
        execute_parser = parser.add_command(**params)
    else:
        execute_parser = CLIParser(**params)
    common_args = [
        CLIFuncParam(
            name="local-port",
            arg_type=int,
            arg_help="Local port to use",
            mandatory=False,
        ),
        CLIFuncParam(
            name="environment",
            arg_type=str,
            arg_help="Environment to use",
            mandatory=False,
        ),
        CLIFuncParam(
            name="access-token",
            arg_type=str,
            arg_help="Access token to use",
            mandatory=False,
        ),
        CLIFuncParam(
            name="universe-id",
            arg_type=str,
            arg_help="Universe ID to use",
            mandatory=False,
        ),
    ]

    module_functions = [action, ai_function]

    for func in module_functions:
        execute_parser.decor_add_command(common_args=common_args)(func)

    return execute_parser


async def ai_function(
    universe_api_key: Optional[str],
    workspace_id: Optional[str],
    menu_path: str = CLIFuncParam(prompt=True),
    ai_function: str = CLIFuncParam(prompt=True),
    version: str = CLIFuncParam(default=None, mandatory=False),
    **kwargs,
):
    """Execute any ai function
    :param universe_api_key: The universe api key that the ai funcion will use
    :param workspace_id: The workspace id
    :param menu_path: The id or name of the menu path
    :param ai_function: The name of the ai function
    :param version: The version of the ai function
    """

    async def get_params(_ai_layer: AILayer, _activity_template: ActivityTemplate):
        """Get the parameters interactively
        :param _ai_layer: AILayer
        :param _activity_template: ActivityTemplate
        """
        params = {}
        input_settings = _activity_template["inputSettings"]
        for param_name, definition in input_settings.items():
            param_value = None
            while param_value is None:
                input_str = (
                    f"Enter value for {param_name}\n"
                    f"  type: {definition['datatype']}\n"
                    f"  description: {definition['description']})\n"
                )
                if not definition["mandatory"]:
                    input_str = input_str[:-1] + "Press enter to skip\n"
                if definition["datatype"] == "file":
                    input_file_names = [
                        file["file_name"]
                        for file in await _ai_layer.get_available_input_files()
                    ] + [""]
                    param_value = choose_from_menu(input_file_names, input_str)
                elif definition["datatype"] == "model":
                    model_names = [
                        model["file_name"]
                        for model in await _ai_layer.get_available_models()
                    ] + [""]
                    param_value = choose_from_menu(model_names, input_str)
                else:
                    param_value = input(input_str)
                    if param_value and definition["datatype"] != "str":
                        try:
                            param_value = eval(
                                f"{definition['datatype']}({param_value})"
                            )
                        except ValueError:
                            logger.error(f"Invalid value for {param_name}")
                            param_value = None

                if not param_value:
                    if definition["mandatory"]:
                        param_value = None
                        print(f"{param_name} is mandatory")
                    else:
                        continue

                params[param_name] = param_value

        return params

    resource_getter = ResourceGetter(
        InitOptions(workspace_id=workspace_id, menu_path=menu_path, **kwargs)
    )
    universe = await resource_getter.get_universe()
    activity_template = await get_activity_template(universe, ai_function, version)
    ai_layer = await resource_getter.get_ai_layer()
    await ai_layer.generic_execute(
        ai_function=ai_function,
        version=version,
        universe_api_key=universe_api_key,
        **(await get_params(ai_layer, activity_template)),
    )


async def action(
    action: str = CLIFuncParam(prompt=True),
    **kwargs,
):
    """Execute an action
    :param action: The id or name of the action
    """
    resource_getter = ResourceGetter(InitOptions(action=action, **kwargs))
    actions_layer = await resource_getter.get_actions_layer()
    action = await resource_getter.get_action()
    action_code = await actions_layer.get_action_code(action["id"])
    thread = threading.Thread(target=execute_action_code, args=(action_code,))
    thread.start()
    thread.join()


if __name__ == "__main__":
    import asyncio

    asyncio.run(add_execute_parser().parse_args())
