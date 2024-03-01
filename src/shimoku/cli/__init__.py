import argparse
import subprocess
from abc import ABC
from typing import Optional
import inspect
import asyncio

from aiohttp.client_exceptions import ClientConnectorError

from prompt_toolkit import PromptSession
from prompt_toolkit.completion import Completer, Completion

from prompt_toolkit.history import FileHistory

from shimoku.utils import get_args_with_defaults

from shimoku.execution_logger import configure_logging
from shimoku.cli.utils import (
    INTERACTIVE_HISTORY_PATH,
    get_current_profile,
    chose_from_available_paths,
    tab_main_navigation_key_binding,
)

from typing import Iterable
import shlex

import logging

logger = logging.getLogger(__name__)


class CLICustomCompleter(Completer):
    USEFUL_VARIABLES = [
        "environment",
        "access_token",
        "universe_id",
        "workspace_id",
        "local_port",
        "menu_path",
        "board",
        "activity",
    ]

    def __init__(self, parser_dict: dict, variables: dict):
        # parser_dict = {
        #     'name': '',
        #     'commands': [
        #         {...},
        #         ...
        #     ],
        #     'args': [
        #         '--arg_name',
        #         ...
        #     ]
        # }
        self.parser_dict = parser_dict
        self.variables = variables

    def get_completions(self, document, complete_event) -> Iterable[Completion]:
        text = document.text_before_cursor
        if text.startswith("$ "):
            used_vars = [
                var
                for var in self.USEFUL_VARIABLES
                if var.startswith(text[2:]) and var not in self.variables
            ]
            for var in used_vars:
                yield Completion(var, start_position=-len(text[2:]))
            return

        last_char_is_space = text[-1] == " " if text else False
        if "  " in text:
            return []
        words = text.split(" ")

        completion_scope = self.parser_dict
        used_args = []
        next_word_is_arg_value = False
        last_word = "" if not words else words[-1]

        for word in words:
            if next_word_is_arg_value:
                if word in completion_scope["args"]:
                    return []
                if last_word == word:
                    break
                next_word_is_arg_value = False
            elif word in [command["name"] for command in completion_scope["commands"]]:
                completion_scope = [
                    command
                    for command in completion_scope["commands"]
                    if command["name"] == word
                ][0]
                used_args = []
            elif word in completion_scope["args"]:
                next_word_is_arg_value = True
                used_args.append(word)
            elif word and last_char_is_space:
                return []

        if next_word_is_arg_value:
            for var in self.variables:
                if var.startswith(last_word):
                    yield Completion(var, start_position=-len(last_word))
            return []

        for command in completion_scope["commands"]:
            if last_char_is_space or command["name"].startswith(last_word):
                yield Completion(command["name"], start_position=-len(last_word))
        for arg in completion_scope["args"]:
            if arg not in used_args and (
                last_char_is_space or arg.startswith(last_word)
            ):
                yield Completion(arg, start_position=-len(last_word))


class CLIFuncParam:
    def __init__(
        self,
        name: Optional[str] = None,
        arg_type: Optional[type] = None,
        arg_help: Optional[str] = None,
        mandatory: bool = True,
        default: Optional = None,
        prompt: bool = False,
        choices: Optional[list] = None,
        real_name: Optional[str] = None,
        action: Optional[str] = None,
        group: Optional[str] = None,
        alt_name: Optional[str] = None,
        is_path: bool = False,
    ):
        self.name = name
        self.arg_type = arg_type
        self.arg_help = arg_help
        self.mandatory = mandatory
        self.default = default
        self.prompt = prompt
        self.choices = choices
        self.real_name = real_name
        self.action = action
        self.group = group
        self.alt_name = alt_name
        self.is_path = is_path

        if default is not None:
            self.mandatory = False
            if arg_type and not isinstance(default, arg_type):
                raise TypeError(
                    f"The default value {default} is not of type {arg_type}"
                )
            if choices and default not in choices:
                raise ValueError(
                    f"The default value {default} is not in the choices {choices}"
                )

        if prompt or group:
            self.mandatory = False
            if default is not None:
                raise ValueError(
                    "Do not set the default value of the CliFuncParam when prompt or group is set to True"
                )


def normalize_name_for_cli(name: str):
    return name.replace("_", "-").lower()


class CLIParser(ABC):
    def __init__(
        self,
        name: str = "shimoku",
        description: str = "This is the Shimoku cli, it is used to interact with the Shimoku services",
        func: callable = None,
        parent: Optional["CLIParser"] = None,
        arguments: Optional[list[CLIFuncParam]] = None,
    ):
        self.name = name
        self.description = description

        self.command_names: list[str] = []
        self.commands: dict[str, CLIParser] = {}
        self.arguments: list[CLIFuncParam] = []
        self.argument_groups = {}
        self.argument_groups_var_names = {}
        self.shell_commands_enabled = False

        if not parent:
            self.parser = argparse.ArgumentParser(
                self.name, description=self.description
            )
        else:
            parent.commands[name] = self
            self.parser = parent.subparsers.add_parser(
                self.name, description=self.description, help=self.description
            )

        self.subparsers = self.parser.add_subparsers(
            dest="command", help="Available commands"
        )

        if arguments:
            for argument in arguments:
                self.add_argument(argument)
        if func:
            self.parser.set_defaults(func=self._decorator_for_self_func(func))
        else:
            self.parser.set_defaults(func=self._default_func)

    def _default_func(self):
        self.parser.print_help()

    def _decorator_for_self_func(self, func: callable):
        def prompt_arg(argument: CLIFuncParam, kwargs: dict):
            if argument.group:
                for arg_name in self.argument_groups_var_names[argument.group]:
                    if kwargs[arg_name] is not None:
                        raise ValueError(
                            f"You can not use the argument {argument.name} with the argument {arg_name}"
                        )
            arg_type = (
                argument.arg_type
                if "Optional" not in str(argument.arg_type)
                else argument.arg_type.__args__[0]
            )
            input_name = argument.real_name if argument.real_name else argument.name
            if not argument.is_path:
                arg_inp = input(f"{input_name}: ")
            else:
                print(f"Select the path for the argument {input_name}:")
                arg_inp = chose_from_available_paths()

            kwargs[argument.name] = arg_type(arg_inp) if arg_inp else None

            if argument.choices and kwargs[argument.name] not in argument.choices:
                raise ValueError(
                    f"The value {kwargs[argument.name]} is not in the choices {argument.choices}"
                )

        def wrapper(**kwargs):
            for argument in self.arguments:
                if argument.prompt and kwargs.get(argument.real_name) is None:
                    prompt_arg(argument, kwargs)
                if argument.real_name and argument.name in kwargs:
                    kwargs[argument.real_name] = kwargs.pop(argument.name)

            return func(**kwargs)

        return wrapper

    def decor_add_command(
        self, name: Optional[str] = None, common_args: list[CLIFuncParam] = None
    ):
        common_args = common_args or []

        def decorator(func: callable):
            func_params = list(inspect.signature(func).parameters.keys())
            func_type_params = {
                param.name: param.annotation
                for param in inspect.signature(func).parameters.values()
            }
            for func_param in func_params:
                if func_param not in func_type_params:
                    func_type_params[func_param] = str
            comment = str(func.__doc__)
            c_help = "\n".join(
                [line for line in comment.split("\n") if ":param" not in line]
            ).strip()
            params_helps = [line for line in comment.split("\n") if ":param" in line]
            params_helps = [line.split(":param ")[1] for line in params_helps]
            params_helps = {
                line.split(":")[0].strip(): line.split(":")[1].strip()
                for line in params_helps
            }
            default_args = get_args_with_defaults(func)
            func_args = []
            for func_param in func_params:
                if func_param not in params_helps:
                    continue
                dafault_value = default_args.get(func_param)
                if isinstance(dafault_value, CLIFuncParam):
                    func_param_obj = dafault_value
                    if func_param_obj.name is None:
                        func_param_obj.name = normalize_name_for_cli(func_param)
                    if (
                        func_param_obj.arg_type is None
                        and func_param_obj.action is None
                    ):
                        func_param_obj.arg_type = func_type_params[func_param]
                    if func_param_obj.arg_help is None:
                        func_param_obj.arg_help = params_helps[func_param]
                    if func_param_obj.real_name is None:
                        func_param_obj.real_name = func_param
                    else:
                        raise ValueError(
                            "Do not set the real_name of the CliFuncParam, it is set automatically"
                        )
                else:
                    arg_type = func_type_params[func_param]
                    mandatory = True
                    if "Optional" in str(arg_type):
                        arg_type = arg_type.__args__[0]
                        mandatory = False

                    func_param_obj = CLIFuncParam(
                        name=normalize_name_for_cli(func_param),
                        arg_type=arg_type,
                        arg_help=params_helps[func_param],
                        mandatory=mandatory,
                        default=dafault_value,
                    )
                if func_param_obj.name in func_args:
                    raise ValueError(
                        f"The argument {func_param_obj.name} is already registered"
                    )
                func_args.append(func_param_obj)

            self.add_command(
                name=normalize_name_for_cli(name if name else func.__name__),
                description=c_help,
                func=func,
                arguments=func_args + common_args,
            )
            return func

        return decorator

    def add_command(
        self,
        name: str = None,
        description: str = None,
        func: callable = None,
        arguments: Optional[list[CLIFuncParam]] = None,
    ) -> "CLIParser":
        command = CLIParser(
            name=name,
            description=description,
            func=func,
            parent=self,
            arguments=arguments,
        )
        if command.name in self.command_names:
            raise ValueError(f"The command {command.name} is already registered")
        self.command_names.append(command.name)
        return command

    def add_argument(self, argument: CLIFuncParam):
        def add_prefix(name: str):
            return ("-" if len(name) == 1 else "--") + name

        if argument.name in self.arguments:
            raise ValueError(f"The argument {argument.name} is already registered")
        params = {
            k: v
            for k, v in dict(
                action=argument.action,
                type=argument.arg_type,
                help=argument.arg_help,
                required=argument.mandatory,
                default=argument.default,
                choices=argument.choices,
            ).items()
            if v is not None
        }
        argument_names = [add_prefix(argument.name)]
        if argument.alt_name:
            argument_names.append(add_prefix(argument.alt_name))

        if argument.group:
            if argument.group not in self.argument_groups:
                self.argument_groups[
                    argument.group
                ] = self.parser.add_mutually_exclusive_group()
                self.argument_groups_var_names[argument.group] = []
            self.argument_groups[argument.group].add_argument(*argument_names, **params)
            self.argument_groups_var_names[argument.group].append(argument.name)
        else:
            self.parser.add_argument(*argument_names, **params)
        self.arguments.append(argument)

    @staticmethod
    async def execute_args(args, user_vars: Optional[dict] = None):
        args_ = vars(args).copy()
        args_.pop("interactive", None)
        args_.pop("shell_commands_enabled", None)
        args_.pop("command", None)
        args_.pop("func", None)

        if user_vars:
            user_vars = {
                k.replace("$", "").replace("-", "_"): v for k, v in user_vars.items()
            }
            for func_param in args_.keys():
                if args_[func_param] is None and func_param in user_vars:
                    args_[func_param] = user_vars.get(func_param)
                    logger.info(
                        f"Using saved value for unspecified argument {func_param}"
                    )

        result = args.func(**args_)
        if inspect.isawaitable(result):
            await result

    async def parse_args(self):
        # argcomplete.autocomplete(self.parser)
        try:
            args = self.parser.parse_args()
        except SystemExit:
            return
        if hasattr(args, "interactive") and args.interactive:
            self.shell_commands_enabled = args.shell_commands_enabled
            await self.parse_args_interactive()
            return
        await self.execute_args(args)

    def gather_commands_and_options(self):
        commands_and_options = {"name": self.name, "commands": [], "args": []}
        for command in self.commands.values():
            commands_and_options["commands"].append(
                command.gather_commands_and_options()
            )
        for argument in self.arguments:
            if argument.name in ["interactive", "shell-commands-enabled"]:
                continue
            commands_and_options["args"].append("--" + argument.name)
        commands_and_options["args"].extend(["--help", "-h"])
        return commands_and_options

    async def parse_args_interactive(self):
        # Dictionary to store user-defined variables
        variables = {}

        # Gather possible commands and options
        commands_and_options = self.gather_commands_and_options()
        completer = CLICustomCompleter(commands_and_options, variables)

        # Trim the history file to 1000 lines
        with open(INTERACTIVE_HISTORY_PATH, "r+") as file:
            lines = file.readlines()
            trimmed_lines = lines[-1000:]
            file.seek(0)
            file.truncate()
            file.writelines(trimmed_lines)

        session = PromptSession(
            completer=completer,
            key_bindings=tab_main_navigation_key_binding(add_space=True),
            history=FileHistory(INTERACTIVE_HISTORY_PATH),
        )
        configure_logging("INFO")

        while True:
            try:
                text = await session.prompt_async(
                    f"S-{get_current_profile().upper()}> "
                )
                if not text:
                    continue

                # Check for variable assignment
                if text.startswith("$"):
                    try:
                        print()
                        # Splitting the input while respecting quoted sections
                        parts = shlex.split(text)
                        for i in range(1, len(parts), 2):
                            var_name, var_value = parts[i], parts[i + 1]
                            variables["$" + var_name] = var_value
                            print(f"Variable {var_name} set to {var_value}")
                            print()
                    except Exception as e:
                        if isinstance(e, (ValueError, IndexError)):
                            print("Invalid variable assignment syntax.")
                            print()
                        else:
                            raise e
                    continue
                if text.startswith("unset$"):
                    _, *var_names = text.split(" ")
                    for var_name in var_names:
                        if "$" + var_name not in variables:
                            print(f"Variable {var_name} not set")
                            print()
                            continue
                        variables.pop("$" + var_name)
                        print(f"Variable {var_name} unset")
                        print()
                    continue

                # Replace variables in user input
                for var_name, var_value in variables.items():
                    text = text.replace(var_name, var_value)

                if "$" in text:
                    print(
                        "Warning: It's possible that not all variables were replaced, please check your input."
                    )
                    print()
                if text in ["exit", "esc"]:
                    break
            except asyncio.CancelledError:
                continue
            except KeyboardInterrupt:
                break
            except EOFError:
                break

            if text.startswith("show "):
                text = text.replace("show ", "")
                print(text)
                print()
                continue
            try:
                args = self.parser.parse_args(text.rstrip().split(" "))
                await self.execute_args(args, variables)
            except SystemExit as e:
                if not self.shell_commands_enabled or e.code == 0:
                    continue
                print()
                confirmation = input(
                    f'The command: "{text}" \n'
                    f"could not be interpreted by the Shimoku parser\n"
                    "do you want to execute it as a shell command? (y/n): "
                )
                if confirmation.lower() == "y":
                    print()
                    try:
                        subprocess.run(text.split(), check=True)
                    except FileNotFoundError:
                        print(f"Command not found: {text}")
                    except subprocess.CalledProcessError:
                        print(f"Command failed: {text}")
            except Exception as e:
                if isinstance(
                    e,
                    (
                        ValueError,
                        TypeError,
                        KeyError,
                        AttributeError,
                        RuntimeError,
                        IndexError,
                        ClientConnectorError,
                    ),
                ):
                    logger.error(e)
