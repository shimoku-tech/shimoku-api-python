from typing import Tuple, Dict, List, Optional, Union
import pandas as pd
import numpy as np
import datetime as dt
import json

import logging
from shimoku_api_python.execution_logger import logging_before_and_after
logger = logging.getLogger(__name__)


def create_normalized_name(name: str) -> str:
    """Having a name create a normalizedName

    Example
    ----------------------
    # "name": "   Test Borrar_grafico    "
    # "normalizedName": "test-borrar-grafico"
    """
    # remove empty spaces at the beginning and end
    name: str = name.strip()
    # replace "_" for www protocol it is not good
    name = name.replace('_', '-')

    return '-'.join(name.split(' ')).lower()


def clean_menu_path(menu_path: str) -> Tuple[str, str]:
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
def _calculate_percentages_from_list(numbers, round_digits_min):
    """Calculate the proportion of each number in a list
    :param numbers: list of numbers
    :param round_digits_min: minimum number of digits to round
    :return: list of percentages
    """
    def max_precision():
        max_p = 0
        for n in numbers:
            str_n = str(n)
            if '.' in str_n:
                n_precision = len(str_n.split('.')[1])
                max_p = n_precision if n_precision > max_p else max_p
        return max(max_p, round_digits_min)

    if isinstance(numbers, list):
        numbers = np.array(numbers)

    perc = np.round(100 * numbers / np.sum(numbers), max_precision())
    round_max = 99.9
    while np.sum(perc) > 99.99:
        perc = np.round(round_max * numbers / np.sum(numbers), max_precision())
        round_max -= 0.1
    return perc
