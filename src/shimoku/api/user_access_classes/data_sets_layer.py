""""""
import pandas as pd
from pandas import DataFrame

from typing import Optional, Union

from shimoku.api.utils import validate_data_is_pandarable
from shimoku.api.resources.app import App
from shimoku.api.resources.data_set import convert_input_data_to_db_items
from shimoku.exceptions import DataError

import logging
from shimoku.execution_logger import log_error, ClassWithLogging

logger = logging.getLogger(__name__)


class DataSetsLayer(ClassWithLogging):
    """
    This class is used to interact with the API at the data set level.
    """

    _module_logger = logger
    _use_info_logging = True

    def __init__(self, app: Optional[App]):
        self._app = app

    async def append_to_data_set(
        self,
        data: Union[list[dict], DataFrame],
        uuid: Optional[str] = None,
        name: Optional[str] = None,
    ) -> str:
        """
        Appends data to a dataset, if the dataset does not exist it will be created.
        :param name: name of the dataset
        :param uuid: uuid of the dataset
        :param data: data to be stored in the dataset
        :return: dataset id
        """

        df = validate_data_is_pandarable(data)
        df["sort_values"] = range(len(df))

        data_set = await self._app.get_data_set(uuid=uuid, name=name)
        data_point = await data_set.get_one_data_point()

        if data_point:
            converted_data = convert_input_data_to_db_items(df, sort={"field": "sort_values"})
            data_point_keys = [col for col in data_point if data_point[col] is not None]
            db_items_keys = set(converted_data[0].keys())
            if [key for key in db_items_keys if key not in data_point_keys]:
                log_error(
                    logger,
                    "The input data has different fields than the existing data set.",
                    DataError,
                )

        await self._app.append_data_to_data_set(
            df, uuid=uuid, name=name, sort={"field": "sort_values"}
        )

        return data_set["id"]

    async def delete_data_set(
        self, uuid: Optional[str] = None, name: Optional[str] = None
    ):
        """
        Delete a dataset in the menu path
        :param name: name of the dataset
        :param uuid: uuid of the dataset
        """
        await self._app.delete_data_set(uuid=uuid, name=name)

    async def delete_data_from_data_set(
        self, uuid: Optional[str] = None, name: Optional[str] = None
    ):
        """
        Delete all data from a dataset in the menu path
        :param name: name of the dataset
        :param uuid: uuid of the dataset
        """
        data_set = await self._app.get_data_set(uuid=uuid, name=name)
        await data_set.delete_data_points()

    async def replace_data_from_data_set(
        self,
        data: Union[list[dict], DataFrame],
        uuid: Optional[str] = None,
        name: Optional[str] = None,
    ):
        """Replace the data in a dataset in the menu path
        :param name: name of the dataset
        :param uuid: uuid of the dataset
        :param data: data to be stored in the dataset
        """
        df = validate_data_is_pandarable(data)
        df["sort_values"] = range(len(df))

        data_set = await self._app.get_data_set(uuid=uuid, name=name)
        await data_set.delete_data_points()

        await self._app.append_data_to_data_set(
            df, uuid=uuid, name=name, sort={"field": "sort_values"}
        )

    async def delete_data_point_from_data_set(
        self,
        data_point_id: str,
        uuid: Optional[str] = None,
        name: Optional[str] = None,
    ):
        """Delete a data point from a dataset in the menu path
        :param data_point_id: id of the data point
        :param name: name of the dataset
        :param uuid: uuid of the dataset
        """
        data_set = await self._app.get_data_set(uuid=uuid, name=name)
        await data_set.delete_data_point(data_point_id)

    @staticmethod
    async def get_columns_mapping_from_data_point(data: dict) -> dict:
        """Get the columns mapping from a data point in the menu path,
        assuming that the null values are empty strings.

        :param data: data to be stored in the dataset
        :return: columns mapping
        """
        data = {k: v if v is not None else ""
                for k, v in data.items()}
        converted_data_point = convert_input_data_to_db_items(pd.DataFrame([data]))[0]
        return {column: mapping for column, mapping in zip(data.keys(), converted_data_point.keys())}

    async def update_data_point_from_data_set(
        self,
        data_point_id: str,
        data: dict,
        uuid: Optional[str] = None,
        name: Optional[str] = None,
    ):
        """Update a data point from a dataset in the menu path,
        data has to follow the schema of the dataset!

        e.g. if your dataset has columns 'id', 'name' and 'age',
        the format to update a data point should be:
        {'stringField2': 'new_name', 'intField1': 25}
             ^ because 'id' is the first string column and you wouldn't want to update it

        suggestion: use get_columns_mapping_from_data_point
        to get the columns mapping from a data point

        :param data_point_id: id of the data point
        :param data: data to be stored in the dataset
        :param name: name of the dataset
        :param uuid: uuid of the dataset
        """
        data_set = await self._app.get_data_set(uuid=uuid, name=name)
        await data_set.update_data_point(
            data_point_id,
            data={k: v for k, v in data.items() if v is not None}
        )

    async def linear_update_data_from_data_set(
        self,
        data: Union[list[dict], DataFrame],
        uuid: Optional[str] = None,
        name: Optional[str] = None,
    ):
        """
        Update the data in the dataset following a linear update strategy,
        creates the new data points if they do not exist, deletes the old ones if they do not exist in the new data,
        and linearly checks if the data points have changed and updates them.
        This makes this function more efficient for small changes than replace_data_from_data_set.
        But if the changes are linear in proportion to the size of the dataset, this function can be
        slower than replace_data_from_data_set.

        :param data: data to be stored in the dataset
        :param name: name of the dataset
        :param uuid: uuid of the dataset
        """
        df = validate_data_is_pandarable(data)
        df["sort_values"] = range(len(df))
        data_set = await self._app.get_data_set(uuid=uuid, name=name)
        data_points = convert_input_data_to_db_items(df, sort={"field": "sort_values"})
        await data_set.linear_update_data_points(data_points)

    async def get_data_from_data_set(
        self,
        uuid: Optional[str] = None,
        name: Optional[str] = None,
        limit: Optional[int] = None,
    ) -> list[dict]:
        """Get the data in a dataset in the menu path
        :param name: name of the dataset
        :param uuid: uuid of the dataset
        :param limit: limit of the data points to be returned
        :return: data in the dataset
        """
        data_set = await self._app.get_data_set(
            uuid=uuid, name=name, create_if_not_exists=False
        )
        if not data_set:
            logger.warning(f"Data set {name if name else uuid} does not exist.")
            return []
        return [
            {k: v for k, v in dp.cascade_to_dict().items() if v is not None}
            for dp in await data_set.get_data_points(limit)
        ]

    async def get_data_set_metadata(
        self,
        uuid: Optional[str] = None,
        name: Optional[str] = None,
    ):
        """Get the metadata of a dataset in the menu path
        :param name: name of the dataset
        :param uuid: uuid of the dataset
        :return: metadata of the dataset
        """
        data_set = await self._app.get_data_set(uuid=uuid, name=name)
        return data_set.cascade_to_dict()
