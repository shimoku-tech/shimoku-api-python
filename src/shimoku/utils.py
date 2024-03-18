from enum import Enum
import inspect
import unicodedata
from typing import Optional
from shimoku.execution_logger import log_error
import sys

import logging

logger = logging.getLogger(__name__)

IN_BROWSER = "_pyodide_core" in sys.modules
ACTIONS_TEST = False


class EventType(Enum):
    NO_EVENT = "NO_EVENT"
    EVENT = "EVENT"
    REPORT_UPDATED = "REPORT_UPDATED"
    REPORT_CREATED = "REPORT_CREATED"
    REPORT_DELETED = "REPORT_DELETED"
    APP_UPDATED = "APP_UPDATED"
    APP_CREATED = "APP_CREATED"
    APP_DELETED = "APP_DELETED"
    DASHBOARD_UPDATED = "DASHBOARD_UPDATED"
    DASHBOARD_CREATED = "DASHBOARD_CREATED"
    DASHBOARD_DELETED = "DASHBOARD_DELETED"
    BUSINESS_CONTENTS_UPDATED = "BUSINESS_CONTENTS_UPDATED"


def get_arg_names(func):
    signature = inspect.signature(func)
    return [k for k, v in signature.parameters.items()]


def get_default_args(func):
    signature = inspect.signature(func)
    return {
        k: v.default if v.default is not inspect.Parameter.empty else None
        for k, v in signature.parameters.items()
    }


def get_args_with_defaults(func):
    signature = inspect.signature(func)
    return {
        k: v.default
        for k, v in signature.parameters.items()
        if v.default is not inspect.Parameter.empty
    }


def create_function_name(name: Optional[str]) -> str:
    """Create a valid function name from a string
    :param name: string to create function name from
    :return: valid function name
    """

    def check_correct_character(character: str) -> bool:
        """Check if a character is valid for a function name
        :param character: character to check
        :return: True if character is valid, False otherwise
        """
        return character.isalnum() or character in ["_", "-", " "]

    if name is None:
        return "no_path"

    # Normalize to ASCII
    normalized_name = (
        unicodedata.normalize("NFKD", name).encode("ascii", "ignore").decode("ascii")
    )

    # Change Uppercase to '_' + lowercase if previous character is in abecedary
    normalized_name = "".join(
        [
            "_" + c.lower()
            if c.isupper() and i > 0 and normalized_name[i - 1].isalpha()
            else c
            for i, c in enumerate(normalized_name)
            if check_correct_character(c)
        ]
    )

    return create_normalized_name(normalized_name).replace("-", "_")


def create_normalized_name(name: str) -> str:
    """Having a name create a normalizedName

    Example
    ----------------------
    # "name": "   Test Borrar_grafico    "
    # "normalizedName": "test-borrar-grafico"
    """
    if any(
        [
            c
            not in "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789._- &$"
            for c in name.encode("ascii", "ignore").decode()
        ]
    ):
        log_error(
            logger,
            f'You can only use letters, numbers, spaces, "-" and "_" in your name | '
            f"you introduced {name}",
            ValueError,
        )
    # remove empty spaces at the beginning and end
    name: str = name.strip()
    # replace "_" for www protocol it is not good
    name = name.replace("_", "-")

    return "-".join(name.split(" ")).lower()


def clean_menu_path(menu_path: str) -> tuple[str, str]:
    """
    Break the menu path in the apptype or app normalizedName
    and the path normalizedName if any
    :param menu_path: the menu path
    """
    # remove empty spaces
    menu_path: str = menu_path.strip()
    # replace "_" for www protocol it is not good
    menu_path = menu_path.replace("_", "-")

    try:
        assert len(menu_path.split("/")) <= 2  # we allow only one level of path
    except AssertionError:
        raise ValueError(
            f"We only allow one subpath in your request | "
            f"you introduced {menu_path} it should be maximum "
            f'{"/".join(menu_path.split("/")[:1])}'
        )

    # Split AppType or App Normalized Name
    normalized_name: str = menu_path.split("/")[0]
    name: str = " ".join(normalized_name.split("-"))

    try:
        path_normalized_name: str = menu_path.split("/")[1]
        path_name: str = " ".join(path_normalized_name.split("-"))
    except IndexError:
        path_name = None

    return name, path_name
