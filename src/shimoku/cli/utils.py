import os
import json
from os import getenv
from typing import Optional
from rich.console import Console
from rich.table import Table
from rich import print
import prompt_toolkit
from shimoku import Client

import logging

home_directory = os.path.expanduser('~')
SHIMOKU_PATH = os.path.join(home_directory, '.shimoku')
if not os.path.exists(SHIMOKU_PATH):
    os.makedirs(SHIMOKU_PATH)

CONFIG_PATH = os.path.join(SHIMOKU_PATH, 'config.json')
if not os.path.exists(CONFIG_PATH):
    with open(CONFIG_PATH, 'w') as f:
        f.write('')

INTERACTIVE_HISTORY_PATH = os.path.join(SHIMOKU_PATH, 'interactive_history.txt')
if not os.path.exists(INTERACTIVE_HISTORY_PATH):
    with open(INTERACTIVE_HISTORY_PATH, 'w') as f:
        f.write('')


environment_v = 'ENVIRONMENT'
access_token_v = 'ACCESS_TOKEN'
universe_id_v = 'UNIVERSE_ID'
workspace_id_v = 'WORKSPACE_ID'


def get_config_profiles() -> list[str]:
    """ Function to get the configuration profiles
    :return: List of configuration profiles
    """
    config_file = open(CONFIG_PATH, 'r')
    try:
        all_configs = json.loads(config_file.read()).get('profiles', {})
        profiles = list(all_configs.keys())
    except json.decoder.JSONDecodeError:
        profiles = []
    config_file.close()
    return profiles


def get_current_profile() -> str:
    """ Function to get the current configuration profile
    :return: Current configuration profile
    """
    config_file = open(CONFIG_PATH, 'r')
    try:
        all_configs = json.loads(config_file.read())
        current_profile = all_configs.get('current_profile', 'default')
    except json.decoder.JSONDecodeError:
        current_profile = 'default'
    config_file.close()
    return current_profile


def get_profile_config(profile: Optional[str] = None) -> dict:
    """ Function to get the configuration from the config file
    :return: Configuration dictionary
    """
    config_file = open(CONFIG_PATH, 'r')
    try:
        all_configs = json.loads(config_file.read())
        current_profile = profile or all_configs.get('current_profile', 'default')
        if 'profiles' not in all_configs:
            raise json.decoder.JSONDecodeError
        for config in all_configs['profiles'].values():
            if any(key not in config for key in [environment_v, access_token_v, universe_id_v, workspace_id_v]):
                raise json.decoder.JSONDecodeError
        config = all_configs['profiles'][current_profile]
    except json.decoder.JSONDecodeError:
        config = {
            environment_v: 'production',
            access_token_v: 'local',
            universe_id_v: 'local',
            workspace_id_v: 'local',
        }
    config_file.close()
    return config


def get_all_configs() -> dict:
    """ Function to get all the configurations from the config file
    :return: Configuration dictionary
    """
    config_file = open(CONFIG_PATH, 'r')
    try:
        all_configs = json.loads(config_file.read())
    except json.decoder.JSONDecodeError:
        all_configs = {}
    config_file.close()
    return all_configs


def filter_dict_list(
        l: list[dict], field: str,
        prefix: Optional[str] = None,
        contains: Optional[str] = None,
        case_sensitive: Optional[bool] = False,
        sort_field: Optional[str] = None,
        equal_to: Optional[str] = None,
        not_equal_to: Optional[str] = None,
) -> list[dict]:
    """ Function to filter a list of dictionaries
    :param l: List of dictionaries
    :param field: Field to filter
    :param prefix: Prefix to filter
    :param contains: String to filter
    :param case_sensitive: Flag to set the case sensitivity of the contains filter
    :param sort_field: Field to sort the list
    :param equal_to: String to match the items
    :param not_equal_to: String to not match the items
    :return: Filtered list of dictionaries
    """
    if not sort_field:
        sort_field = field
    if not case_sensitive:
        prefix = prefix.lower() if prefix else None
        contains = contains.lower() if contains else None
    filtered_list = []
    for element in l:
        if not isinstance(element[field], dict) and not isinstance(element[field], list):
            value = str(element[field])
        else:
            value = json.dumps(element[field], indent=2)
        if equal_to and value != equal_to:
            continue
        if not_equal_to and value == not_equal_to:
            continue
        value = value if case_sensitive else value.lower()
        if prefix and not value.startswith(prefix):
            continue
        if contains and contains not in value:
            continue
        filtered_list.append(element)

    try:
        non_none_items = [x[sort_field] for x in filtered_list if x[sort_field] is not None]
        if len(non_none_items) == 0:
            print(f"Can't sort the list by {sort_field} because all the items are None")
            return filtered_list
        list_type = type(non_none_items[0])
        for item in filtered_list:
            if item[sort_field] is None:
                item[sort_field] = list_type()
        return sorted(
            filtered_list,
            key=lambda x: x[sort_field]
            if not isinstance(x[sort_field], dict) else str(x[sort_field])
        )
    except TypeError:
        print(f"Error sorting the list by {sort_field}")
        return filtered_list


def display_dict_list(
        items: list[dict], title: str,
        fields: Optional[list[str]] = None,
        table_lines: bool = False,
):
    """ Function to display a list of dictionaries
    :param items: List of dictionaries
    :param title: Title of the table
    :param fields: Fields to display
    :param table_lines: Flag to set the table lines
    """
    if fields is None:
        fields = list(items[0].keys())
    table = Table(title=title, show_lines=table_lines)
    for field in fields:
        table.add_column(field)
    for item in items:
        row = []
        for field in fields:
            if not isinstance(item[field], dict) and not isinstance(item[field], list):
                row.append(str(item[field]))
            else:
                row.append(json.dumps(item[field], indent=2))
        table.add_row(*row)

    console = Console()
    print()
    console.print(table)
    print()


def list_filtering_and_display(
        items: list[dict],
        table_title: str,
        fields: Optional[list[str]] = None,
        table_lines: bool = True,
        **kwargs,
):
    """ Function to filter and display a list of items
    :param items: List of items to filter and display
    :param table_title: Title of the table
    :param fields: Fields to display
    :param table_lines: Flag to set the table lines
    """
    if not items:
        print("\nNo items to list\n")
        return

    if fields is None:
        fields = list(items[0].keys())
    else:
        fields = [field for field in fields if field in items[0].keys()]

    if not fields:
        print("\nNo fields to display\n")
        return

    if not kwargs['filter_field']:
        kwargs['filter_field'] = fields[0]
    if not kwargs['sort_field']:
        kwargs['sort_field'] = kwargs['filter_field']

    items = filter_dict_list(
        items,
        field=kwargs['filter_field'],
        prefix=kwargs['prefix'],
        contains=kwargs['contains'],
        case_sensitive=kwargs['case_sensitive'],
        sort_field=kwargs['sort_field'],
        equal_to=kwargs['equal_to'],
        not_equal_to=kwargs['not_equal_to'],
    )

    if kwargs['count']:
        print(f"# of {table_title}: {len(items)}")
        return
    else:
        display_dict_list(
            items,
            title=table_title,
            fields=fields,
            table_lines=table_lines,
        )


def display_dict(
        item: dict,
        fields: list[str]
):
    """ Function to display a dictionary
    :param item: Dictionary to display
    :param fields: Fields to display
    """
    resource_dict = {k: v for k, v in item.items() if k in fields}
    print(json.dumps(resource_dict, indent=4))


def display_list(
    title: str,
    items: list[str],
):
    """ Function to display a list
    :param title: Title of the list
    :param items: List to display
    """
    if not items:
        print("\nNo items to list\n")
        return
    print(f"\n{title}:")
    for item in items:
        print('  · ' + item)
    print()


def choose_from_menu(options: list[str], title: str = 'Choose an option: ') -> str:
    """
    Function to choose from a list of options
    :param options: List of options to choose from
    :param title: Title of the menu
    """
    completer = prompt_toolkit.completion.WordCompleter(options)
    selected = prompt_toolkit.prompt(title, completer=completer)
    while selected not in options:
        print("Invalid option, use the TAB key to see the available options")
        selected = prompt_toolkit.prompt(title, completer=completer)
    return selected


def input_list() -> list[str]:
    """ Function to input a list of strings
    :return: List of strings
    """
    print("Enter the list of strings, one per line, press Enter twice to finish")
    items = []
    while True:
        item = input()
        if item:
            items.append(item)
        else:
            break
    return items


def input_dict() -> dict[str, str]:
    """ Function to input a dictionary of strings
    :return: Dictionary of strings
    """
    print("Enter the dictionary of strings, first the key and then the value, press Enter in the key step to finish")
    items = {}
    while True:
        key = input("Key: ")
        if key:
            value = input("Value: ")
            items[key] = value
        else:
            break
    return items


def save_as_file(
    logger: logging.Logger,
    file_path: str,
    file_obj: bytes,
    file_name: str = 'output.txt',
):
    """ Function to save content to a file
    :param logger: Logger to use
    :param file_path: Path to save the file
    :param file_obj: File object to save
    :param file_name: Name of the file to save
    """
    if len(file_name.split('.')) == 1:
        file_name += '.txt'
    try:
        if not os.path.exists(file_path):
            os.makedirs(file_path)
        file_path = os.path.join(file_path, file_name)
        with open(file_path, 'wb') as write_file:
            write_file.write(file_obj)
            logger.info(f'File saved to {file_path}')
    except Exception as e:
        logger.error(f'Error saving file to {file_path}: {e}')
        return
