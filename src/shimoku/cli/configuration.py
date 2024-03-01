import json
from shimoku.cli import CLIParser, CLIFuncParam
from shimoku.cli.utils import (
    CONFIG_PATH,
    get_profile_config,
    environment_v,
    access_token_v,
    universe_id_v,
    workspace_id_v,
    get_config_profiles,
    get_current_profile,
    get_all_configs,
)
from shimoku.exceptions import APIError
from shimoku.cli.cloud.cascade_get_resources import InitOptions, ResourceGetter
from typing import Optional
from rich.console import Console
from rich.table import Table


def add_configuration_parser(parser: Optional[CLIParser] = None):
    """
    Function to add the configuration parser to a parser
    :param parser: Parser to add the configuration parser to
    """

    params = {
        "name": "config",
        "description": "Commands to configure the SDK access",
    }

    if parser:
        configuration_parser = parser.add_command(**params)
    else:
        configuration_parser = CLIParser(**params)

    module_functions = [
        switch_profile,
        set,
        get,
        clear,
        list_profiles,
        delete_profile,
    ]

    for func in module_functions:
        configuration_parser.decor_add_command()(func)

    return configuration_parser


def switch_profile(profile: str = CLIFuncParam(prompt=True)):
    """
    Switch the current profile
    :param profile: Profile to switch to
    """
    configs = get_all_configs()
    if profile not in configs["profiles"]:
        print(f"The profile {profile} does not exist.")
        return
    with open(CONFIG_PATH, "w") as f:
        configs["current_profile"] = profile
        json.dump(configs, f)
    print(f"The current profile has been switched to {profile}.")


async def set(
    access_token: Optional[str] = CLIFuncParam(prompt=True),
    universe_id: Optional[str] = CLIFuncParam(prompt=True),
    workspace_id: Optional[str] = CLIFuncParam(prompt=True),
    environment: str = CLIFuncParam(default="production", mandatory=False),
    profile: str = CLIFuncParam(default="default", mandatory=False),
):
    """
    Set the configuration variables for the SDK access
    :param environment: Environment to use
    :param access_token: Access token to use
    :param universe_id: Universe id to use
    :param workspace_id: Workspace id to use
    :param profile: Profile to use
    """
    try:
        await ResourceGetter(
            InitOptions(
                environment=environment,
                access_token=access_token,
                universe_id=universe_id,
                workspace_id=workspace_id,
            )
        ).get_business()
    except APIError:
        print(
            "The configuration parameters are not valid, please check them and try again."
        )
        return

    print("The configuration parameters are valid, saving them...")
    configs = get_all_configs()
    current_profile = get_current_profile()
    profile = profile or current_profile
    config = configs.get(profile, {})
    with open(CONFIG_PATH, "w") as f:
        config[environment_v] = (
            environment if environment else config.get(environment_v, "production")
        )
        config[access_token_v] = (
            access_token if access_token else config.get(access_token_v, None)
        )
        config[universe_id_v] = (
            universe_id if universe_id else config.get(universe_id_v, "local")
        )
        config[workspace_id_v] = (
            workspace_id if workspace_id else config.get(workspace_id_v, "local")
        )

        if "profiles" not in configs:
            configs["profiles"] = {}
        configs["profiles"][profile] = config
        configs["current_profile"] = profile

        if "default" not in configs["profiles"]:
            configs["profiles"]["default"] = config

        json.dump(configs, f)


def get(profile: Optional[str]):
    """
    Get the configuration variables for the SDK access
    :param profile: Profile to use
    """
    if not profile:
        profile = get_current_profile()
    config = get_profile_config(profile)
    table = Table(
        title=f"{profile[0].upper()+profile[1:].lower()} Configuration Variables"
    )

    for key in config.keys():
        table.add_column(key)
    table_row = [config_value for config_value in config.values()]
    table.add_row(*table_row)
    console = Console()
    console.print(table)


def clear(profile: Optional[str]):
    """
    Clear the configuration variables for the SDK access
    :param profile: Profile to clear
    """
    configs = get_all_configs()
    current_profile = get_current_profile()
    with open(CONFIG_PATH, "w") as f:
        profile = profile or current_profile
        if profile not in configs["profiles"]:
            print(f"The profile {profile} does not exist.")
            return
        configs["profiles"][profile] = {
            environment_v: "production",
            access_token_v: "local",
            universe_id_v: "local",
            workspace_id_v: "local",
        }
        json.dump(configs, f)
    print("The configuration parameters have been cleared.")


def delete_profile(profile: str = CLIFuncParam(prompt=True)):
    """
    Delete a profile
    :param profile: Profile to delete
    """
    if profile == "default":
        print("The default profile cannot be deleted.")
        return
    configs = get_all_configs()
    current_profile = get_current_profile()
    configs["profiles"].pop(profile)
    if current_profile == profile:
        configs["current_profile"] = "default"
        print("The current profile has been switched to default.")
    with open(CONFIG_PATH, "w") as f:
        json.dump(configs, f)
    print(f"The profile {profile} has been deleted.")


def list_profiles():
    """
    List the profiles
    """
    profiles = get_config_profiles()
    table = Table(title="Profiles")
    table.add_column("Profile")
    table.add_column("Current")
    for profile in profiles:
        table.add_row(profile, "X" if profile == get_current_profile() else "")
    console = Console()
    console.print(table)
