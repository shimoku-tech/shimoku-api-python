import pandas as pd
import asyncio
import numpy as np

from copy import deepcopy

from pandas import DataFrame
from math import ceil
from shimoku.async_execution_pool import (
    AutoAsyncExecutionPool,
    add_to_general_async_group,
)

from typing import Optional, Union

from shimoku.utils import EventType

from shimoku.api.resources.app import App
from shimoku.api.resources.business import Business
from shimoku.api.resources.report import Report
from shimoku.api.resources.data_set import (
    DataSet,
    Mapping,
    convert_input_data_to_db_items,
    convert_data_and_get_series_name,
)
from shimoku.api.resources.reports.filter_data_set import FilterDataSet
from shimoku.api.resources.reports.tabs_group import TabsGroup
from shimoku.api.resources.reports.modal import Modal
from shimoku.api.resources.reports.charts.indicator import Indicator
from shimoku.api.resources.reports.charts.echart import EChart
from shimoku.api.resources.reports.charts.table import Table, interpret_label_info
from shimoku.api.resources.reports.charts.annotated_chart import AnnotatedEChart
from shimoku.api.resources.reports.charts.html import HTML
from shimoku.api.resources.reports.charts.button import Button
from shimoku.api.resources.reports.charts.input_form import InputForm
from shimoku.api.resources.reports.charts.iframe import IFrame
from shimoku.plt.EChart_definitions.line import (
    line_chart,
    area_chart,
    stacked_area_chart,
    predictive_line_chart,
    marked_line_chart,
    segmented_area_chart,
    line_with_confidence_area_chart,
    segmented_line_chart,
)
from shimoku.plt.EChart_definitions.bar import (
    bar_chart,
    stacked_bar_chart,
    horizontal_bar_chart,
    stacked_horizontal_bar_chart,
    zero_centered_bar_chart,
)
from shimoku.plt.EChart_definitions.scatter import (
    scatter_chart,
    scatter_with_effect_chart,
)
from shimoku.plt.EChart_definitions.funnel import funnel_chart
from shimoku.plt.EChart_definitions.tree import tree_chart
from shimoku.plt.EChart_definitions.radar import radar_chart
from shimoku.plt.EChart_definitions.pie import pie_chart, doughnut_chart, rose_chart
from shimoku.plt.EChart_definitions.gauge import speed_gauge_chart
from shimoku.plt.EChart_definitions.shimoku_gauge import (
    shimoku_gauge_chart,
    shimoku_gauges_group,
)
from shimoku.plt.EChart_definitions.sunburst import sunburst_chart
from shimoku.plt.EChart_definitions.treemap import treemap_chart
from shimoku.plt.EChart_definitions.sankey import sankey_chart
from shimoku.plt.EChart_definitions.heatmap import heatmap_chart
from shimoku.plt.EChart_definitions.gauge_indicator import gauge_indicator
from shimoku.plt.EChart_definitions.top_bottom import (
    top_bottom_area_charts,
    top_bottom_line_charts,
)
from shimoku.plt.EChart_definitions.waterfall import waterfall_chart
from shimoku.plt.EChart_definitions.line_and_bar import line_and_bar_charts
from shimoku.plt.bentobox_charts import (
    chart_and_modal_button,
    infographics_text_bubble,
    indicators_with_header,
    chart_and_indicators,
    line_with_summary,
)

from shimoku.exceptions import TabsError, ModalError, DataError, BentoboxError
from shimoku.plt.utils import (
    deep_update,
    get_uuids_from_dict,
    get_data_references_from_dict,
    validate_data_is_pandarable,
    add_sorting_to_df,
    transform_dict_js_to_py,
    retrieve_data_from_options,
    validate_input_form_data,
    create_normalized_name,
)

import logging
from shimoku.execution_logger import log_error, ClassWithLogging

logger = logging.getLogger(__name__)


class PlotLayer(ClassWithLogging):
    """
    This class is a high level abstraction of the API, it is used to create components and data sets easily.
    """

    _module_logger = logger
    _use_info_logging = True

    def __init__(
        self,
        async_pool: AutoAsyncExecutionPool,
        app: Optional[App],
        reuse_data_sets: bool = False,
    ):
        self._app = app
        self._business: Business = app.parent if app else None
        self._current_path: Optional[str] = None
        self._current_tabs_group: Optional[TabsGroup] = None
        self._current_tab: Optional[str] = None
        self._current_modal: Optional[Modal] = None
        self._bentobox_data: dict = {}
        self.reuse_data_sets: bool = reuse_data_sets
        self._delete_data_set_lock = None
        self._shared_data_map: dict[str, dict[str, tuple[Mapping, DataSet, dict]]] = {}
        self._shared_data: dict[str, any] = {}
        self._execution_path_orders: list[str] = []
        self._async_pool = async_pool

    async def _create_event(
        self, event_type: EventType, content: dict, resource_id: Optional[str] = None
    ):
        """Create an event.
        :param event_type: the type of the event
        :param content: the content of the event
        """
        if self._app.api_client.playground:
            await self._business.create_event(event_type, content, resource_id)

    def clear_context(self):
        if self._bentobox_data:
            self._bentobox_data = {}
            logger.info("Popped out of bentobox")
        if self._current_tabs_group:
            self._current_tabs_group = None
            self._current_tab = None
            logger.info("Popped out of tabs group")
        if self._current_modal:
            self._current_modal = None
            logger.info("Popped out of modal")

    def _check_for_conflicts(self, async_pool: AutoAsyncExecutionPool, order: int):
        """
        Check if there are charts with the same order.
        :param order: the order of the chart
        """
        r_hash = self._get_chart_hash(order)
        free_context: dict = async_pool.free_context
        if "list_for_conflicts" not in free_context:
            free_context["list_for_conflicts"] = []

        if r_hash in free_context["list_for_conflicts"]:
            async_pool.clear()
            self.clear_context()
            log_error(
                logger,
                "Chart order collision, two charts with the same order can not be executed "
                "at the same time",
                RuntimeError,
            )

        free_context["list_for_conflicts"].append(r_hash)

    def _check_before_async_execution(
        self, async_pool: AutoAsyncExecutionPool, func: callable, *args, **kwargs
    ):
        """Check everything is correct before executing the task pool"""
        if "order" in kwargs:
            self._check_for_conflicts(async_pool, kwargs["order"])

    def raise_if_cant_change_path(self):
        """Raise an error if a tabs group or a modal is already open."""
        if self._current_tabs_group:
            log_error(
                logger, "Cannot change path while a tabs group is open", TabsError
            )
        if self._current_modal:
            log_error(logger, "Cannot change path while a modal is open", ModalError)
        if self._bentobox_data:
            log_error(
                logger, "Cannot change path while a bentobox is open", BentoboxError
            )

    def get_shared_data_names(self) -> list[str]:
        """Get the names of the shared data"""
        return list(self._shared_data_map.keys())

    def change_path(self, path: str):
        """Change the current path"""
        self.raise_if_cant_change_path()
        self._current_path = path
        if path and path not in self._execution_path_orders:
            self._execution_path_orders.append(path)

    def _get_hash_for_container(self, name: str):
        """Get the hash for a container"""
        return (f"{self._current_path}_" if self._current_path else "") + name

    async def clear_menu_path(self):
        """
        Clear the current path or a subpath
        """
        reports = await self._app.get_reports()
        touched_data_set_ids = []
        if self._current_path is not None:
            path = create_normalized_name(self._current_path)
            reports = [
                report
                for report in reports
                if report["path"] and create_normalized_name(report["path"]) == path
            ]
        else:
            touched_data_set_ids = [ds["id"] for ds in await self._app.get_data_sets()]

        containers: list = [
            report for report in reports if report.report_type in ["TABS", "MODAL"]
        ]

        for container in containers:
            container.clear_content()
            if not self._app.api_client.cache_enabled:
                await container.update()

        rds = await asyncio.gather(
            *[report.get_report_data_sets() for report in reports]
        )
        touched_data_set_ids.extend([rd["dataSetId"] for rds in rds for rd in rds])

        await asyncio.gather(
            *[self._app.delete_report(report["id"]) for report in reports]
        )
        logger.info(f"Deleted {len(reports)} components")
        await self._app.delete_unused_data_sets(
            log=True, data_set_ids=touched_data_set_ids
        )

    async def delete_chart_by_order(self, order: int):
        """
        Delete a report by order and context
        """
        r_hash, report = await self._get_chart_report(
            order, Table, create_if_not_exists=False
        )
        if not report:
            log_error(logger, f"No chart found with order {order}", RuntimeError)
        await self._app.delete_report(r_hash=r_hash)

    async def delete_tabs_group(self, name: str):
        """Delete a tabs group"""
        r_hash = self._get_hash_for_container(name)
        tabs_group = await self._app.get_report(r_hash=r_hash)
        if not tabs_group:
            log_error(logger, f"No tabs group found with name {name}", TabsError)
        await self._app.delete_report(r_hash=r_hash)

    async def delete_modal(self, name: str):
        """Delete a modal"""
        r_hash = self._get_hash_for_container(name)
        modal = await self._app.get_report(r_hash=r_hash)
        if not modal:
            log_error(logger, f"No modal found with name {name}", ModalError)
        await self._app.delete_report(r_hash=r_hash)

    def set_bentobox(self, cols_size: int, rows_size: int):
        """Start using a bentobox, the id and the order will be set when the bentobox is used for the first time
        :param cols_size: the number of columns in the bentobox
        :param rows_size: the number of rows in the bentobox"""
        self._bentobox_data: dict = {
            "bentoboxId": None,
            "bentoboxOrder": None,
            "bentoboxSizeColumns": cols_size,
            "bentoboxSizeRows": rows_size,
        }

    def pop_out_of_bentobox(self):
        """Stop using a bentobox"""
        self._bentobox_data = {}

    def _get_bentobox_data(self, order: int) -> dict:
        """Get the bentobox data"""
        if not self._bentobox_data:
            return {}
        if not self._bentobox_data["bentoboxId"]:
            if not self._bentobox_data["bentoboxId"]:
                self._bentobox_data.update(
                    {
                        "bentoboxId": "_" + str(order),
                        "bentoboxOrder": order,
                    }
                )
        return self._bentobox_data

    async def _update_containers(self):
        """Update the reports that act as containers"""
        reports = await self._app.get_reports()
        containers: list[Report] = [
            report for report in reports if report.report_type in ["TABS", "MODAL"]
        ]
        await asyncio.gather(*[container.update() for container in containers])
        logger.info("Updated tab groups and modals")

    async def set_tabs_index(
        self,
        tabs_index: tuple[str, str],
        order: Optional[int] = None,
        parent_tabs_index: Optional[tuple[str, str]] = None,
        padding: Optional[str] = None,
        cols_size: Optional[int] = None,
        rows_size: Optional[int] = None,
        just_labels: Optional[bool] = None,
        sticky: Optional[bool] = None,
    ):
        """Set the current tabs index.
        :param tabs_index: the index of the tabs group
        :param order: the order of the tabs group in the dashboard
        :param parent_tabs_index: the index of the parent tabs group
        :param cols_size: the size of the columns in the tabs group
        :param padding: the padding of the tabs group
        :param rows_size: the size of the rows in the tabs group
        :param just_labels: whether to show just the labels in the tabs group
        :param sticky: whether to make the tabs group sticky
        """
        r_hash = self._get_hash_for_container(tabs_index[0])
        tabs_group: Optional[TabsGroup] = await self._app.get_report(r_hash=r_hash)
        params = {"properties": {}}
        if cols_size:
            params["sizeColumns"] = cols_size
        if padding:
            params["sizePadding"] = padding
        if rows_size:
            params["sizeRows"] = rows_size
        if isinstance(just_labels, bool):
            params["properties"]["variant"] = (
                "solidRounded" if just_labels else "enclosedSolidRounded"
            )
        if isinstance(sticky, bool):
            params["properties"]["sticky"] = sticky
        bentobox_data = self._get_bentobox_data(order)
        if bentobox_data:
            params["bentobox"] = bentobox_data
        if self._current_path:
            params["path"] = self._current_path

        if not tabs_group:
            if not isinstance(order, int):
                log_error(
                    logger,
                    f"Cannot create tabs group {tabs_index[0]} without order",
                    TabsError,
                )
            tabs_group: TabsGroup = await self._app.create_report(
                TabsGroup, r_hash=r_hash, order=order, **params
            )
            logger.info(
                f'Created tabs group {tabs_index[0]} with id {tabs_group["id"]}'
            )
        elif order:
            await self._app.update_report(r_hash=r_hash, order=order, **params)

        if parent_tabs_index:
            p_hash = self._get_hash_for_container(parent_tabs_index[0])
            parent_tabs_group: Optional[TabsGroup] = await self._app.get_report(
                r_hash=p_hash
            )
            if not parent_tabs_group:
                log_error(
                    logger,
                    f"No tabs group found with name {parent_tabs_index[0]}",
                    TabsError,
                )
            if parent_tabs_group["id"] == tabs_group["id"]:
                log_error(logger, "Cannot include tabs group in itself", TabsError)
            if self._current_modal:
                log_error(
                    logger,
                    "Cannot include a tabs group in a modal and in another tabs group",
                    TabsError,
                )
            if not parent_tabs_group.has_report(tabs_group):
                parent_tabs_group.add_report(
                    tab=parent_tabs_index[1], report=tabs_group
                )
                logger.info(
                    f"Included tabs group {tabs_index[0]} in tabs group {parent_tabs_index[0]}"
                )

        elif self._current_modal and not self._current_modal.has_report(tabs_group):
            (await self._get_current_modal()).add_report(tabs_group)
            logger.info(
                f"Included tabs group {tabs_index[0]} in modal {str(self._current_modal)}"
            )

        self._current_tabs_group = tabs_group
        tabs_group.add_tab(tabs_index[1])
        self._current_tab = tabs_index[1]

        if "update_containers" not in self._async_pool.ending_tasks:
            self._async_pool.ending_tasks[
                "update_containers"
            ] = self._update_containers()

    def pop_out_of_tabs_group(self):
        """
        Pop the current tabs index.
        """
        if not self._current_tabs_group:
            log_error(logger, "No tabs group to pop out of", TabsError)

        self._current_tabs_group = None
        self._current_tab = None

    def change_current_tab(self, tab: str):
        """
        Change the current tab.
        :param tab: the name of the tab
        """
        if not self._current_tabs_group:
            log_error(logger, "No tabs group to change tab", TabsError)

        self._current_tabs_group.add_tab(tab)
        self._current_tab = tab

        if "update_containers" not in self._async_pool.ending_tasks:
            self._async_pool.ending_tasks[
                "update_containers"
            ] = self._update_containers()

    async def _get_modal(
        self,
        modal_name: str,
        width: Optional[int] = None,
        height: Optional[int] = None,
        open_by_default: Optional[bool] = None,
    ) -> Modal:
        r_hash = self._get_hash_for_container(modal_name)
        modal: Optional[Modal] = await self._app.get_report(r_hash=r_hash)
        if not modal:
            modal: Report = await self._app.create_report(
                Modal,
                r_hash=r_hash,
                path=self._current_path,
                properties={"width": width, "height": height, "open": open_by_default},
            )
            logger.info(f'Created modal {modal_name} with id {modal["id"]}')
            return modal
        properties = {}
        if width:
            properties["width"] = width
        if height:
            properties["height"] = height
        if open_by_default:
            properties["open"] = open_by_default
        if properties:
            await self._app.update_report(
                r_hash=r_hash, properties=properties, path=self._current_path
            )
            logger.info(f'Updated modal {modal_name} with id {modal["id"]}')
        return modal

    async def set_modal(
        self,
        modal_name: str,
        width: Optional[int] = None,
        height: Optional[int] = None,
        open_by_default: Optional[bool] = None,
    ) -> None:
        """Set the current modal.
        :param modal_name: the name of the modal
        :param width: the width of the modal
        :param height: the height of the modal
        :param open_by_default: whether the modal is open by default
        """
        if self._current_tabs_group:
            log_error(
                logger,
                "Cannot set a modal in a tabs group, pop out of the tabs group first",
                ModalError,
            )

        modal = await self._get_modal(modal_name, width, height, open_by_default)
        self._current_modal = modal

        if "update_containers" not in self._async_pool.ending_tasks:
            self._async_pool.ending_tasks[
                "update_containers"
            ] = self._update_containers()

    def pop_out_of_modal(self):
        """Pop the current modal."""
        if not self._current_modal:
            log_error(logger, "No modal to pop out of", ModalError)

        if self._current_tabs_group:
            log_error(
                logger,
                "Cannot pop out of a modal when in a tabs group, pop out of the tabs group first",
                ModalError,
            )
        if self._bentobox_data:
            log_error(
                logger,
                "Cannot pop out of a modal when in a bentobox, close the bentobox first",
                ModalError,
            )

        self._current_modal = None

    async def _get_current_modal(self) -> Modal:
        """Get the current modal."""
        if not self._current_modal:
            log_error(logger, "No modal set", ModalError)
        if self._app.api_client.cache_enabled:
            return self._current_modal
        last_modal = self._current_modal
        self._current_modal = await self._app.get_report(
            r_hash=self._current_modal["properties"]["hash"]
        )
        if self._current_modal is None:
            log_error(
                logger,
                f'No modal found with name {last_modal["properties"]["name"]}',
                ModalError,
            )
        return self._current_modal

    async def _get_current_tabs_group(self) -> TabsGroup:
        """Get the current tabs group."""
        if not self._current_tabs_group:
            log_error(logger, "No tabs group get", TabsError)
        if self._app.api_client.cache_enabled:
            return self._current_tabs_group
        last_tabs_group = self._current_tabs_group
        self._current_tabs_group = await self._app.get_report(
            r_hash=self._current_tabs_group["properties"]["hash"]
        )
        if self._current_tabs_group is None:
            log_error(
                logger,
                f'No tabs group found with name {last_tabs_group["properties"]["name"]}',
                TabsError,
            )
        return self._current_tabs_group

    def _get_chart_hash(self, order: int) -> str:
        r_hash = f"{order}"
        if self._current_tabs_group:
            r_hash = f'{self._current_tabs_group["properties"]["hash"]}_{self._current_tab}_{order}'
        elif self._current_modal:
            r_hash = f'{self._current_modal["properties"]["hash"]}_{order}'
        elif self._current_path:
            r_hash = f"{self._current_path}_{order}"
        return r_hash

    async def _get_chart_report(
        self, order: int, chart_class: type[Report], create_if_not_exists: bool = True
    ) -> tuple[str, Optional[Report]]:
        """Get the chart report.
        :param order: the order of the chart
        :param chart_class: the chart class
        :param create_if_not_exists: whether to create the chart if it doesn't exist
        """
        r_hash = self._get_chart_hash(order)
        report = await self._app.get_report(r_hash=r_hash)

        if not report:
            if create_if_not_exists:
                report = await self._app.create_report(
                    chart_class, r_hash=r_hash, order=order
                )
                logger.info(f'Created {chart_class.__name__} with id {report["id"]}')
        elif report.report_type != chart_class.report_type:
            await report.change_report_type(chart_class)

        return r_hash, report

    async def get_component_by_order(self, order: int) -> Optional[dict]:
        """Get the component by order.
        :param order: the order of the component
        """
        r_hash = self._get_chart_hash(order)
        report = await self._app.get_report(r_hash=r_hash)
        if not report:
            return None
        return report.cascade_to_dict()

    async def get_modal(self, modal_name: str) -> Optional[dict]:
        """Get the modal.
        :param modal_name: the name of the modal
        """
        r_hash = self._get_hash_for_container(modal_name)
        modal = await self._app.get_report(r_hash=r_hash)
        if not modal:
            return None
        return modal.cascade_to_dict()

    async def get_tabs_group(self, tabs_index: tuple[str, str]) -> Optional[dict]:
        """Get the tabs group.
        :param tabs_index: the index of the tabs group
        """
        r_hash = self._get_hash_for_container(tabs_index[0])
        tabs_group = await self._app.get_report(r_hash=r_hash)
        if not tabs_group:
            return None
        return tabs_group.cascade_to_dict()

    async def _try_to_reuse_data(
        self, data_set: DataSet, data: Union[list, pd.DataFrame]
    ) -> dict[str, tuple[Mapping, DataSet, dict]]:
        """Try to reuse the data set.
        :param data_set: the data set
        :param data: the data
        """
        df = validate_data_is_pandarable(data)
        aux_data_point = await data_set.get_one_data_point()
        if not aux_data_point:
            log_error(
                logger,
                f"Cannot reuse data set {str(data_set)} because the data set is empty",
                DataError,
            )

        mappings = [col for col in aux_data_point if aux_data_point[col] is not None]
        df, sort = add_sorting_to_df(df) if "orderField1" in mappings else (df, None)

        converted_data_points = convert_input_data_to_db_items(df, sort=sort)
        for mapping, v in converted_data_points[0].items():
            if mapping not in mappings:
                log_error(
                    logger,
                    f"Cannot reuse data set {str(data_set)} because the data provided "
                    f"is not consistent with the data set",
                    DataError,
                )

        first_df_item = df.iloc[0].to_dict()
        return {
            col: (mapping, data_set, sort)
            for col, mapping in zip(
                first_df_item.keys(), converted_data_points[0].keys()
            )
            if col != "sort_values"
        }

    async def _delete_data_set_if_exists(self, data_set_name: str) -> None:
        """Delete the data set if it exists.
        :param data_set_name: the name of the data set
        """
        if await self._app.force_delete_data_set(name=data_set_name):
            logger.info(f"Deleted data set with name {data_set_name}")

    async def _create_data_set_from_df(
        self, data_set_name: str, df: pd.DataFrame, sort: Optional[dict] = None
    ) -> dict[str, tuple[Mapping, DataSet, dict]]:
        """Get the data mapping to tuple.
        :param df: the data frame
        :return: the data mapping to tuple
        """
        df, sort = add_sorting_to_df(df, sort)
        columns = df.columns.tolist()
        data_mapping_to_tuple = {}
        (mapping, data_set, res_sort) = await self._app.append_data_to_data_set(
            name=data_set_name, data=df, sort=sort
        )
        logger.info(
            f'Created data set with id {data_set["id"]} and name {data_set_name}'
        )
        for col, map_val in zip(columns, mapping):
            data_mapping_to_tuple[col] = (map_val, data_set, res_sort)
        return data_mapping_to_tuple

    async def _create_dumped_data_set(
        self, data_set_name: str, data: list[dict]
    ) -> dict:
        """Get the mapping from a dict.
        :param data: the data
        :return: the mapping tuple
        """
        mapping, data_set, sort = await self._app.append_data_to_data_set(
            name=data_set_name, data=data, dump_whole=True
        )
        logger.info(
            f'Created data set with id {data_set["id"]} and name {data_set_name}'
        )
        assert mapping[0] == "customField1"
        return {"data": ("customField1", data_set, sort)}

    async def _create_data_set(
        self,
        name: str,
        data: Union[list[dict], pd.DataFrame, dict, str],
        dump_whole: bool = False,
    ) -> dict[str, tuple[Mapping, DataSet, dict]]:
        """Set a shared data entry.
        :param name: the key of the shared data entry
        :param data: the value of the shared data entry
        :param dump_whole: whether to dump the whole data set
        """
        if self.reuse_data_sets:
            data_set = await self._app.get_data_set(
                name=name, create_if_not_exists=False
            )
            if data_set:
                return (
                    await self._try_to_reuse_data(data_set, data)
                    if not dump_whole
                    else {"data": ("customField1", data_set, {})}
                )

        await self._delete_data_set_if_exists(data_set_name=name)

        if dump_whole:
            return await self._create_dumped_data_set(name, data)

        return await self._create_data_set_from_df(name, DataFrame(data))

    async def _set_shared_data_entry(
        self,
        name: str,
        data: Union[list[dict], pd.DataFrame, dict, str],
        dump_whole: bool = False,
    ):
        """
        Set a shared data entry.
        :param name: the key of the shared data entry
        :param data: the value of the shared data entry
        :param dump_whole: whether to dump the whole data set
        """
        if name in self._shared_data_map:
            log_error(
                logger,
                f"Cannot set shared data entry {name} because it already exists",
                DataError,
            )

        self._shared_data_map[name] = await self._create_data_set(
            name, data, dump_whole
        )
        self._shared_data[name] = data

    async def set_shared_data(
        self,
        dfs: dict[str, Union[list[dict], pd.DataFrame]] = None,
        custom_data: dict[str, any] = None,
    ):
        """
        Set shared data for the s.plt to use.
        :param dfs: the data frames
        :param custom_data: the custom data
        """
        tasks = []
        for k, df in (dfs if dfs else {}).items():
            tasks.append(self._set_shared_data_entry(k, df))
        for k, v in (custom_data if custom_data else {}).items():
            tasks.append(self._set_shared_data_entry(k, v, dump_whole=True))
        if tasks:
            await asyncio.gather(*tasks)
        else:
            log_error(logger, "No data provided", DataError)

    async def _choose_data(
        self,
        order: int,
        data: Union[list[dict], pd.DataFrame, dict, str],
        chart_class: type[Report] = EChart,
        dump_whole: bool = False,
    ) -> dict[str, tuple[Mapping, DataSet, dict]]:
        """Get the data mappings of the data. If the data is a string, it is assumed to be a shared data entry.
        :param order: the order of the chart
        :param data: the data
        :param dump_whole: whether to dump the whole data set
        :return: the data mappings
        """
        if isinstance(data, str):
            if data not in self._shared_data_map:
                log_error(logger, f"No shared data with name {data} found", DataError)
            return self._shared_data_map[data]

        _, report = await self._get_chart_report(order, chart_class)
        name = report["id"]

        return await self._create_data_set(name, data, dump_whole)

    async def _check_previous_paths(self):
        """Check if there are paths that have not been executed yet."""
        paths_in_order = await self._app.get_paths_in_order()
        not_executed_paths = [
            p for p in paths_in_order if p not in self._execution_path_orders
        ]
        if len(not_executed_paths) > 0:
            not_uploaded_paths = [
                p for p in self._execution_path_orders if p not in paths_in_order
            ]
            self._execution_path_orders.clear()
            for p in paths_in_order + not_uploaded_paths:
                self._execution_path_orders.append(p)

    async def _create_chart(
        self, chart_class: type[Report], order: int, **params
    ) -> Report:
        """Create a chart and add it to the current tabs group or modal.
        :param chart_class: the class of the chart
        :param order: the order of the chart in the dashboard
        :param params: the arguments of the chart
        """
        if "logging_func_name" in params:
            del params["logging_func_name"]

        if not params.get("title"):
            params["title"] = ""
        if not params.get("sizeRows"):
            params["sizeRows"] = 3
        if not params.get("sizeColumns"):
            params["sizeColumns"] = 12
        if not params.get("sizePadding"):
            params["sizePadding"] = "0,0,0,0"

        params["bentobox"] = self._get_bentobox_data(order=order)
        params["path"] = self._current_path

        if hasattr(self, "code_generation_metadata"):
            if "properties" not in params:
                params["properties"] = {}
            params["properties"]["code_generation_metadata"] = getattr(
                self, "code_generation_metadata"
            )

        event_type: EventType = EventType.REPORT_UPDATED
        r_hash, chart = await self._get_chart_report(
            order, chart_class, create_if_not_exists=False
        )
        if chart:
            params["pathOrder"] = chart["pathOrder"]
            if self._current_path and params["pathOrder"] is None:
                await self._check_previous_paths()
                params["pathOrder"] = self._execution_path_orders.index(
                    self._current_path
                )
            if chart != self._app.mock_create_report(
                chart_class, r_hash=r_hash, order=order, **params
            ):
                await self._app.update_report(r_hash=r_hash, **params)
                logger.info(f"Updated {chart_class.__name__} at {str(chart)}")
            else:
                logger.info(
                    f"No changes needed for {chart_class.__name__} at {str(chart)}"
                )
                return chart
        else:
            event_type: EventType = EventType.REPORT_CREATED
            await self._check_previous_paths()
            params["pathOrder"] = (
                self._execution_path_orders.index(self._current_path)
                if self._current_path
                else None
            )
            params["order"] = order
            chart: Report = await self._app.create_report(
                chart_class, r_hash=r_hash, **params
            )
            logger.info(
                f'Created {chart_class.__name__} at {str(chart)} with id {chart["id"]}'
            )

        added_to_container = False
        if self._current_tabs_group:
            if not self._current_tabs_group.has_report(chart):
                (await self._get_current_tabs_group()).add_report(
                    tab=self._current_tab, report=chart
                )
                logger.info(
                    f"Included chart {str(chart)} in tabs group {str(self._current_tabs_group)}"
                )
                added_to_container = True
        elif self._current_modal and not self._current_modal.has_report(chart):
            (await self._get_current_modal()).add_report(chart)
            logger.info(
                f"Included chart {str(chart)} in modal {str(self._current_modal)}"
            )
            added_to_container = True

        if (
            added_to_container
            and "update_containers" not in self._async_pool.ending_tasks
        ):
            self._async_pool.ending_tasks[
                "update_containers"
            ] = self._update_containers()

        await self._create_event(event_type, {}, chart["id"])

        return chart

    def _get_field_mapping(
        self, field: Union[str, tuple, list, dict], data_mapping_to_tuple: dict
    ) -> Union[str, list, dict]:
        """Get the mapping of a field."""
        if isinstance(field, str):
            return data_mapping_to_tuple[field][0]
        elif isinstance(field, (tuple, list)):
            return [data_mapping_to_tuple[f][0] for f in field]
        elif isinstance(field, dict):
            return {k: data_mapping_to_tuple[v][0] for k, v in field.items()}

    def _check_mapping_in_report_data_set(
        self, report_data_set: Report.ReportDataSet, mapping: Mapping
    ) -> bool:
        """Check if the mapping is correct in the report data set.
        :param report_data_set: the report data set
        :param mapping: the mapping
        :return: True if the mapping is consistent, False otherwise
        """
        report_data_set_mapping = report_data_set["properties"]["mapping"]
        if report_data_set_mapping != mapping:
            logger.warning(
                f"Mapping inconsistent in component data set link {str(report_data_set)}"
            )
        return report_data_set_mapping == mapping

    @staticmethod
    def _get_filter_properties(
        series_name: str, converted_data: pd.DataFrame, multi_select: bool
    ) -> tuple[Optional[list[str]], Optional[list[str]], FilterDataSet.InputType]:
        if series_name.startswith("date"):
            return None, ["contains"], FilterDataSet.InputType.DATERANGE
        elif series_name.startswith("int"):
            return None, None, FilterDataSet.InputType.NUMERIC
        elif series_name.startswith("string"):
            return (
                converted_data[series_name].unique().tolist(),
                ["eq"],
                FilterDataSet.InputType.CATEGORICAL_SINGLE
                if not multi_select
                else FilterDataSet.InputType.CATEGORICAL_MULTI,
            )
        log_error(
            logger, f"Field type {series_name} is not supported", NotImplementedError
        )

    @add_to_general_async_group
    async def filter(
        self,
        order: int,
        data: str,
        field: str,
        multi_select: bool = False,
        cols_size: int = 4,
        rows_size: int = 1,
        padding: Optional[str] = None,
    ):
        """
        Filter the data set.
        :param order: the order of the chart
        :param data: the data
        :param field: the field to filter
        :param multi_select: whether to allow multi select
        :param cols_size: the size of the columns
        :param rows_size: the size of the rows
        :param padding: the padding
        """

        if not isinstance(data, str):
            log_error(
                logger,
                "To filter a data set, the data must be a shared data entry",
                DataError,
            )

        if data not in self._shared_data_map:
            log_error(logger, f"No shared data with name {data} found", DataError)

        _, data_set, _ = self._shared_data_map[data][field]
        data = self._shared_data[data]

        converted_data, series_name = convert_data_and_get_series_name(data, field)
        options, operations, input_type = self._get_filter_properties(
            series_name, converted_data, multi_select
        )

        properties = {
            "filter": [
                {
                    "field": field,
                    "inputType": input_type.value,
                }
            ],
            "mapping": [{field: series_name, "id": data_set["id"]}],
        }

        if operations:
            properties["filter"][0]["operations"] = operations
        if options:
            properties["filter"][0]["options"] = options

        await self._create_chart(
            chart_class=FilterDataSet,
            order=order,
            title="",
            sizeRows=rows_size,
            sizeColumns=cols_size,
            sizePadding=padding,
            properties=properties,
        )

    @add_to_general_async_group
    async def iframe(
        self,
        url: str,
        order: int,
        height: int = 640,
        cols_size: Optional[int] = None,
        padding: Optional[str] = None,
    ):
        """Create an iframe report in the dashboard.
        :param url: the url of the iframe
        :param order: the order of the iframe
        :param height: the height of the iframe
        :param cols_size: the columns that the iframe occupies
        :param padding: padding
        """
        await self._create_chart(
            chart_class=IFrame,
            order=order,
            dataFields=dict(
                url=url,
                height=height,
            ),
            sizePadding=padding,
            sizeColumns=cols_size,
            sizeRows=ceil(height / 240),
        )

    async def _html(
        self,
        html: str,
        order: int,
        cols_size: Optional[int] = None,
        rows_size: Optional[int] = None,
        padding: Optional[str] = None,
    ):
        """html for internal use"""
        await self._create_chart(
            chart_class=HTML,
            order=order,
            chartData=[{"value": html}],
            sizePadding=padding,
            sizeColumns=cols_size,
            sizeRows=rows_size,
        )

    @add_to_general_async_group
    async def html(
        self,
        html: str,
        order: int,
        cols_size: Optional[int] = None,
        rows_size: Optional[int] = None,
        padding: Optional[str] = None,
    ):
        """
        Create an html report in the dashboard.
        :param html: the html code
        :param order: the order of the html
        :cols_size: the columns that the html occupies
        :rows_size: the rows that the html occupies
        :padding: padding
        """
        await self._html(html, order, cols_size, rows_size, padding)

    @add_to_general_async_group
    async def single_indicator(
        self,
        data: dict,
        order: int,
        cols_size: Optional[int] = None,
        rows_size: Optional[int] = None,
        padding: Optional[str] = None,
    ):
        """
        Create an indicator report in the dashboard.
        :param data: the data of the indicator
        :param order: the order of the indicator
        :cols_size: the columns that the indicator occupies
        :rows_size: the rows that the indicator occupies
        :padding: padding
        """
        await self._create_chart(
            chart_class=Indicator,
            path=self._current_path,
            order=order,
            sizePadding=padding,
            sizeRows=rows_size,
            sizeColumns=cols_size,
            properties=data,
        )

    def indicator(
        self,
        data: Union[str, pd.DataFrame, list[dict], dict],
        order: int,
        vertical: Union[bool, str] = False,
        color_by_value: bool = False,
        cols_size: int = 12,
        rows_size: int = 1,
        padding: Optional[str] = None,
        **kwargs,  # makes backwards compatibility easier
    ):
        """
        Create an indicator report in the dashboard.
        :param data: the data of the indicator
        :param order: the order of the indicator
        :param vertical: whether the indicator is vertical
        :param color_by_value: whether to color the indicator by value
        :cols_size: the columns that the indicator occupies
        :rows_size: the rows that the indicator occupies
        :padding: padding
        :title: the title of the indicator
        """
        df = pd.DataFrame(data if isinstance(data, list) else [data])
        keep_columns = [
            k for k in df.columns if k in list(Indicator.default_properties.keys())
        ]
        df = df[keep_columns]

        original_padding = padding

        len_df = len(df)
        if vertical and (len_df > 1 or isinstance(vertical, str)):
            if self._bentobox_data:
                log_error(
                    logger,
                    "Cannot create vertical indicators in a bentobox",
                    RuntimeError,
                )

            self.set_bentobox(cols_size=cols_size, rows_size=rows_size * len_df)

            # fixexd cols_size for bentobox and variable rows size
            cols_size = 22
            rows_size = rows_size * 10 - 2

            padding = "1,1,0,1"
            if isinstance(vertical, str):
                html = f"<h5 style='font-family: Rubik'>{vertical}</h5>"
                self.html(
                    html=html,
                    order=order,
                    rows_size=2,
                    cols_size=cols_size,
                    padding=padding,
                )
                order += 1
        else:
            bentobox_data = self._bentobox_data
            if padding is None:
                padding = "0,0,0,0"

            padding = padding.replace(" ", "")

            remaining_cols = cols_size % len_df

            extra_padding = remaining_cols // 2
            padding_left_int = int(padding[6]) + extra_padding
            padding_right_int = int(padding[2]) + extra_padding + remaining_cols % 2

            padding_left = f"{padding[0]},0,{padding[4]},{padding_left_int}"
            padding_right = f"{padding[0]},{padding_right_int},{padding[4]},{int(bool(bentobox_data))}"
            padding_else = f"{padding[0]},0,{padding[4]},{int(bool(bentobox_data))}"

            cols_size = cols_size // len_df - int(bool(bentobox_data))
            if cols_size < 2:
                log_error(
                    logger,
                    f"The calculation of the individual cols_size for each indicator "
                    f"is too small (cols_size/len(df)): {cols_size}",
                    ValueError,
                )

        last_index = df.index[-1]
        first_index = df.index[0]

        for index, df_row in df.iterrows():
            if not vertical:
                if index == first_index and index == last_index:
                    padding = original_padding
                elif index == first_index:
                    padding = padding_left
                elif index == last_index:
                    padding = padding_right
                else:
                    padding = padding_else
            elif (
                index == last_index
                and vertical
                and (len_df > 1 or isinstance(vertical, str))
            ):
                padding = "1,1,1,1"

            if color_by_value and "color" not in df_row and "icon" not in df_row:
                df_row["color"] = (
                    "success"
                    if df_row["value"] > 0
                    else "error"
                    if df_row["value"] < 0
                    else "neutral"
                )
                df_row["icon"] = (
                    "Line/arrow-up"
                    if df_row["value"] > 0
                    else "Line/arrow-down"
                    if df_row["value"] < 0
                    else "none"
                )

            self.single_indicator(
                data=df_row.dropna().to_dict(),
                order=order,
                cols_size=cols_size,
                rows_size=rows_size,
                padding=padding,
            )

            if isinstance(order, int):
                order += 1

        if vertical:
            self.pop_out_of_bentobox()

        return order

    async def _button(
        self,
        label: str,
        order: int,
        rows_size: Optional[int] = None,
        cols_size: Optional[int] = None,
        align: Optional[str] = "stretch",
        padding: Optional[str] = None,
        on_click_events: Optional[Union[list[dict], dict]] = None,
    ):
        """Create a button in the dashboard."""
        if not on_click_events:
            on_click_events = []
        elif isinstance(on_click_events, dict):
            on_click_events = [on_click_events]

        await self._create_chart(
            chart_class=Button,
            order=order,
            sizePadding=padding,
            sizeRows=rows_size,
            sizeColumns=cols_size,
            properties=dict(
                text=label, align=align, events=dict(onClick=on_click_events)
            ),
        )

    @add_to_general_async_group
    async def button(
        self,
        label: str,
        order: int,
        rows_size: Optional[int] = 1,
        cols_size: int = 2,
        align: Optional[str] = "stretch",
        padding: Optional[str] = None,
        on_click_events: Optional[Union[list[dict], dict]] = None,
    ):
        """Create a button in the dashboard."""
        await self._button(
            label=label,
            order=order,
            rows_size=rows_size,
            cols_size=cols_size,
            align=align,
            padding=padding,
            on_click_events=on_click_events,
        )

    @add_to_general_async_group
    async def modal_button(
        self,
        label: str,
        order: int,
        modal: str,
        rows_size: Optional[int] = 1,
        cols_size: int = 2,
        align: Optional[str] = "stretch",
        padding: Optional[str] = None,
    ):
        """
        Create a button in the dashboard that opens a modal.
        :param label: the label of the button
        :param order: the order of the button
        :param modal: the name of the modal
        :param rows_size: the size of the rows in the button
        :param cols_size: the size of the columns in the button
        :param align: the alignment of the button
        :param padding: the padding of the button
        """
        modal_id = (await self._get_modal(modal))["id"]

        await self._button(
            label=label,
            order=order,
            padding=padding,
            rows_size=rows_size,
            cols_size=cols_size,
            align=align,
            on_click_events=[
                dict(
                    action="openModal",
                    params=dict(
                        modalId=modal_id,
                    ),
                )
            ],
        )

    @add_to_general_async_group
    async def activity_button(
        self,
        label: str,
        order: int,
        rows_size: Optional[int] = 1,
        cols_size: int = 2,
        align: Optional[str] = "stretch",
        padding: Optional[str] = None,
        activity_id: Optional[str] = None,
        activity_name: Optional[str] = None,
    ):
        """
        Create a button in the dashboard that executes an activity.
        :param label: the label of the button
        :param order: the order of the button
        :param rows_size: the size of the rows in the button
        :param cols_size: the size of the columns in the button
        :param align: the alignment of the button
        :param padding: the padding of the button
        :param activity_id: the id of the activity
        :param activity_name: the name of the activity
        """
        activity_id = (await self._app.get_activity(activity_id, activity_name))["id"]

        await self._button(
            label=label,
            order=order,
            padding=padding,
            rows_size=rows_size,
            cols_size=cols_size,
            align=align,
            on_click_events=[
                dict(
                    action="runActivity",
                    params=dict(
                        activityId=activity_id,
                    ),
                )
            ],
        )

    @add_to_general_async_group
    async def table(
        self,
        order: int,
        data: Union[str, pd.DataFrame, list[dict], dict],
        columns: Optional[list[str]] = None,
        columns_button: bool = True,
        filters: bool = True,
        export_to_csv: bool = True,
        search: bool = True,
        page_size: int = 10,
        page_size_options: Optional[list[int]] = None,
        initial_sort_column: Optional[str] = None,
        sort_descending: bool = False,
        columns_options: Optional[dict] = None,
        categorical_columns: Optional[list[str]] = None,
        label_columns: Optional[dict] = None,
        web_link_column: Optional[str] = None,
        open_link_in_new_tab: bool = False,
        title: Optional[str] = None,
        padding: Optional[str] = None,
        rows_size: Optional[int] = None,
        cols_size: Optional[int] = None,
    ):
        """Create a table report in the dashboard.
        :param order: the order of the table
        :param data: the data of the table
        :param columns: the columns of the table
        :param columns_button: whether to show the columns button
        :param filters: whether to show the filters button
        :param export_to_csv: whether to show the export to csv button
        :param search: whether to show the search bar
        :param page_size: the number of rows per page
        :param page_size_options: the options for the number of rows per page
        :param initial_sort_column: the initial sorting column
        :param sort_descending: whether to sort descending by the initial sorting column
        :param columns_options: the options for the columns
        :param categorical_columns: the categorical columns
        :param label_columns: the label columns
        :param report_params: additional report parameters as key-value pairs
        :param web_link_column: the column to use as web link
        :param open_link_in_new_tab: whether to open the web link in a new tab
        :param title: the title of the table
        :param padding: the padding of the table
        :param rows_size: the rows size of the table
        :param cols_size: the columns size of the table
        """

        data_mappings_to_tuples = await self._choose_data(order, data, Table)
        if isinstance(data, str):
            data = self._shared_data[data]

        df = validate_data_is_pandarable(data)

        if not columns:
            columns = list(data_mappings_to_tuples.keys())
        if not columns_options:
            columns_options = {}
        if not categorical_columns:
            categorical_columns = []
        if not label_columns:
            label_columns = {}
        else:
            aux_label_columns = label_columns
            label_columns = {}
            for has_to_be_tuple in aux_label_columns:
                v = aux_label_columns[has_to_be_tuple]
                if isinstance(has_to_be_tuple, str):
                    label_columns[(has_to_be_tuple, "filled")] = v
                elif isinstance(has_to_be_tuple, tuple):
                    label_columns[has_to_be_tuple] = v
                else:
                    log_error(
                        logger,
                        f"Invalid label_columns key: {has_to_be_tuple}",
                        ValueError,
                    )
        label_just_columns = [x[0] for x in label_columns.keys()]

        _, data_set, _ = data_mappings_to_tuples[columns[0]]
        columns_dicts = []
        rows_dict = {"mapping": {}}
        for i, name in enumerate(columns):
            column_options = {"field": name, "headerName": name, "order": i}

            if name in columns_options:
                column_options.update(columns_options[name])

            if name in categorical_columns:
                if name in label_columns:
                    log_error(
                        logger,
                        f"Columns cannot be both included in categorical_columns and label_columns: {name}",
                        ValueError,
                    )
                column_options["type"] = "singleSelect"
                column_options["options"] = df[name].unique().tolist()

            if name in label_just_columns:
                index = label_just_columns.index(name)
                (_, variant), label_options = list(label_columns.items())[index]
                column_options["chips"] = {}
                column_options["chips"]["variant"] = variant
                column_options["chips"]["options"] = interpret_label_info(
                    df, name, label_options, variant
                )

            if name == web_link_column:
                column_options["link"] = {
                    "url": "webLink",
                    "openNewTab": open_link_in_new_tab,
                }

            columns_dicts.append(column_options)
            rows_dict["mapping"][name] = data_mappings_to_tuples[name][0]

        if web_link_column:
            rows_dict["mapping"]["web"] = data_mappings_to_tuples[web_link_column][0]
            rows_dict["mapping"]["webLink"] = data_mappings_to_tuples[web_link_column][
                0
            ]

        _, report = await self._get_chart_report(order, Table)

        rds = await report.get_report_data_sets()

        if (
            self.reuse_data_sets
            and report["properties"].get("columns")
            and report["properties"]["columns"] != columns_dicts
        ):
            log_error(
                logger,
                "Columns options do not match the previous columns, most likely data has changed,"
                " don't use the reuse_data_sets option in this case",
                DataError,
            )

        if rds and (
            not self.reuse_data_sets
            or any(rd["dataSetId"] != data_set["id"] for rd in rds)
        ):
            await report.delete_report_data_sets(log=True)
            rds = []

        if not rds:
            await report.create_report_data_set((None, data_set, None))

        pagination = {"pageSize": page_size}
        if page_size_options:
            pagination["pageSizeOptions"] = page_size_options

        sort = {}
        if initial_sort_column:
            sort["field"] = data_mappings_to_tuples[initial_sort_column][0]
            sort["direction"] = "asc" if not sort_descending else "desc"

        await self._create_chart(
            chart_class=Table,
            order=order,
            sizePadding=padding,
            sizeRows=rows_size,
            sizeColumns=cols_size,
            title=title,
            properties=dict(
                columns=columns_dicts,
                rows=rows_dict,
                columnsButton=columns_button,
                filtersButton=filters,
                exportButton=export_to_csv,
                search=search,
                pagination=pagination,
                sort=sort,
            ),
        )

    @add_to_general_async_group
    async def input_form(
        self,
        options: dict,
        order: int,
        padding: Optional[str] = None,
        rows_size: Optional[int] = None,
        cols_size: Optional[int] = None,
        modal: Optional[str] = None,
        activity_id: Optional[str] = None,
        activity_name: Optional[str] = None,
        on_submit_events: Optional[list[dict]] = None,
    ):
        """Creates an input form.
        :param options: the options for the input form
        :param order: the order of the input form
        :param padding: the padding of the input form
        :param rows_size: the rows size of the input form
        :param cols_size: the columns size of the input form
        :param modal: the modal to open after submitting the form
        :param activity_id: the activity id to run after submitting the form
        :param activity_name: the activity name to run after submitting the form
        :param on_submit_events: the events to run after submitting the form
        """
        validate_input_form_data(self, options)

        if on_submit_events is None:
            on_submit_events = []

        if modal:
            modal_id = (await self._get_modal(modal))["id"]
            on_submit_events.append(
                {"action": "openModal", "params": {"modalId": modal_id}}
            )

        if activity_id or activity_name:
            activity_id = (await self._app.get_activity(activity_id, activity_name))[
                "id"
            ]

            on_submit_events.append(
                {
                    "action": "runActivity",
                    "params": {
                        "activityId": activity_id,
                    },
                }
            )

        initial_data: dict = {}
        for fields in options["fields"]:
            for field in fields["fields"]:
                field_name: str = field["fieldName"]
                input_type: Optional[str] = field.get("inputType")
                if input_type == "color":
                    initial_data[field_name] = "#000000"
                elif input_type == "number":
                    initial_data[field_name] = 0
                else:
                    initial_data[field_name] = ""

        r_hash, report = await self._get_chart_report(order, InputForm)
        _, data_set, _ = list(
            (
                await self._create_data_set(report["id"], initial_data, dump_whole=True)
            ).values()
        )[0]

        rds = await report.get_report_data_sets()
        if len(rds) > 1:
            log_error(
                logger,
                "Input form can only have one component data set link, "
                "this is an SDK bug please report it and "
                "delete the form to solve the issue",
                DataError,
            )

        if rds and (
            not self.reuse_data_sets
            or rds[0]["dataSetId"] != data_set["id"]
            or rds[0]["properties"]["fields"] != options["fields"]
        ):
            await report.delete_report_data_sets(log=True)
            rds = []

        if not rds:
            await report.create_report_data_set(
                ("customField1", data_set, None), properties=options
            )
            logger.info(f"Created 1 component data set link for input form at {r_hash}")

        await self._create_chart(
            chart_class=InputForm,
            order=order,
            sizePadding=padding,
            sizeRows=rows_size,
            sizeColumns=cols_size,
            properties={"events": {"onSubmit": on_submit_events}},
        )

    def generate_input_form_groups(
        self,
        order: int,
        form_groups: dict,
        dynamic_sequential_show: Optional[bool] = False,
        auto_send: Optional[bool] = False,
        next_group_label: Optional[str] = "Next",
        rows_size: Optional[int] = 3,
        cols_size: int = 12,
        padding: Optional[str] = None,
        modal: Optional[str] = None,
        activity_id: Optional[str] = None,
        activity_name: Optional[str] = None,
        on_submit_events: Optional[list[dict]] = None,
    ):
        """Easier way to create an input form.
        :param menu_path: the menu path of the input form
        :param order: the order of the input form
        :param form_groups: the form groups of the input form
        :param dynamic_sequential_show: whether to show the next group after submitting the current group
        :param auto_send: whether to automatically send the form after the last group
        :param next_group_label: the label of the next group button
        :param rows_size: the rows size of the input form
        :param cols_size: the columns size of the input form
        :param padding: the padding of the input form
        :param modal: the modal to open after submitting the form
        :param activity_id: the activity id to run after submitting the form
        :param activity_name: the activity name to run after submitting the form
        :param on_submit_events: the events to run after submitting the form
        """
        report_data_set_properties = {"fields": []}
        if auto_send:
            report_data_set_properties["variant"] = "autoSend"

        r_hash = self._get_chart_hash(order)

        next_id = f"{r_hash}_0" if dynamic_sequential_show else None

        next_group_index = 1
        for form_group_name, form_group in form_groups.items():
            form_group_json = {"title": form_group_name, "fields": form_group}
            if next_id:
                form_group_json["id"] = next_id
                next_id = f"{r_hash}_{next_group_index}"
                form_group_json["nextFormGroup"] = {
                    "id": next_id,
                    "label": next_group_label,
                }
                next_group_index += 1
            report_data_set_properties["fields"] += [form_group_json]

        if next_id:
            del report_data_set_properties["fields"][-1]["nextFormGroup"]

        self.input_form(
            options=report_data_set_properties,
            order=order,
            rows_size=rows_size,
            cols_size=cols_size,
            padding=padding,
            modal=modal,
            activity_id=activity_id,
            activity_name=activity_name,
            on_submit_events=on_submit_events,
        )

    async def _get_input_form_data(self, input_form: InputForm) -> dict:
        """Get the input form data."""
        report_data_set = (await input_form.get_report_data_sets())[0]
        data_set = await self._app.get_data_set(report_data_set["dataSetId"])
        data_point = await data_set.get_one_data_point()
        logger.info(f"Got input form data for {str(input_form)}")
        return {
            "reportId": input_form["id"],
            "order": input_form["order"],
            "data": data_point["customField1"] if data_point else None,
        }

    async def get_input_forms(self) -> list[dict]:
        """Get all the input forms in the current menu_path."""
        reports: list = [
            report
            for report in await self._app.get_reports()
            if report["reportType"] == "FORM"
            and (report["path"] == self._current_path or not self._current_path)
        ]
        return list(
            await asyncio.gather(
                *[self._get_input_form_data(report) for report in reports]
            )
        )

    @add_to_general_async_group
    async def annotated_chart(
        self,
        data: Union[list[DataFrame], list[list[dict]]],
        order: int,
        x: str,
        y: Union[str, list[str]],
        annotations: str = "annotation",
        rows_size: Optional[int] = None,
        cols_size: Optional[int] = None,
        padding: Optional[str] = None,
        title: Optional[str] = None,
        y_axis_name: Optional[str] = None,
        slider_config: Optional[dict] = None,
        slider_marks: Optional[list[tuple]] = None,
    ):
        """
        Create an annotated chart in the menu path.
        :param data: the data of the chart
        :param order: the order of the chart
        :param x: the x axis
        :param y: the y axis
        :param annotations: the annotations
        :param rows_size: the rows size of the chart
        :param cols_size: the columns size of the chart
        :param padding: the padding of the chart
        :param title: the title of the chart
        :param y_axis_name: the name of the y axis
        :param slider_config: the slider config
        :param slider_marks: the slider marks
        """
        if isinstance(data, str):
            log_error(
                logger,
                "Annotated chart does not support the use of shared data",
                DataError,
            )

        if slider_config is None:
            slider_config = {}

        if slider_marks:
            slider_config["marks"] = [
                {"label": mark[0], "value": mark[1]} for mark in slider_marks
            ]

        if isinstance(y, str):
            y = [y]

        if not len(y) == len(data):
            log_error(
                logger,
                f"Number of y values ({len(y)}) does not match number of dataframes ({len(data)})",
                DataError,
            )

        _, report = await self._get_chart_report(order, AnnotatedEChart)

        dfs = [validate_data_is_pandarable(df) for df in data]
        data_set_tasks = []
        for df, y_val in zip(dfs, y):
            df[x] = pd.to_datetime(df[x])
            if annotations in df:
                df[annotations] = (
                    df[annotations].replace(np.nan, "", regex=True).astype(str)
                )
            data_set_tasks.append(
                self._create_data_set(name=f"{report['id']}_{y_val}", data=df)
            )

        data_set_dicts = await asyncio.gather(*data_set_tasks)
        data_sets = [ds[y_val][1] for ds, y_val in zip(data_set_dicts, y)]

        rd_ids = None
        if self.reuse_data_sets:
            rd_ids = get_uuids_from_dict(report["properties"]["option"])
            if len(rd_ids) == len(y):
                rep_ds: list[Report.ReportDataSet] = await report.get_report_data_sets()
                rep_ds = [
                    next((rd for rd in rep_ds if rd["id"] == rd_id), None)
                    for rd_id in rd_ids
                ]
                if any(
                    rd["dataSetId"] != ds["id"]
                    or rd["properties"]["mapping"]
                    != {"values": ["dateField1", "intField1"], "label": "stringField1"}
                    for rd, ds in zip(rep_ds, data_sets)
                ):
                    rd_ids = None

        if not rd_ids:
            await report.delete_report_data_sets(log=True)
            mapping: Mapping = {
                "values": ["dateField1", "intField1"],
                "label": "stringField1",
            }
            report_data_sets = await asyncio.gather(
                *[
                    report.create_report_data_set((mapping, data_set, None))
                    for data_set in data_sets
                ]
            )
            rd_ids = [rd["id"] for rd in report_data_sets]

        chart_options = {
            "yAxis": {
                "name": y_axis_name or "",
                "font" "type": "value",
                "nameLocation": "middle",
                "nameGap": 30,
            },
            "xAxis": {
                "type": "time",
                "nameLocation": "middle",
                "nameGap": 30,
            },
            "series": [
                {
                    "data": "#{" + rd_id + "}",
                    "type": "line",
                    "name": y_name,
                    "itemStyle": {
                        "borderRadius": [9, 9, 0, 0],
                    },
                }
                for y_name, rd_id in zip(y, rd_ids)
            ],
        }
        await self._create_chart(
            chart_class=AnnotatedEChart,
            order=order,
            sizePadding=padding,
            sizeRows=rows_size,
            sizeColumns=cols_size,
            title=title,
            properties=dict(
                slider=slider_config,
                option=chart_options,
            ),
        )

    async def _get_report_data_sets_per_mapping(
        self,
        report: Report,
        data_mapping_to_tuple: dict,
        fields: list[Union[tuple, dict]],
    ) -> list[Report.ReportDataSet]:
        """Create a data_set per field of a dataframe.
        :param report: the report
        :param data_mapping_to_tuple: the mapping of the data
        :param fields: the fields of the data to be used
        :return: the list of data sets partitioned by axis and fields
        """
        tasks = []
        fields = fields if fields else []
        for i, f in enumerate(fields):
            mapping = []
            data_set = None
            res_sort = None
            if isinstance(f, str):
                if f not in data_mapping_to_tuple:
                    log_error(logger, f"Field {f} not found in data", DataError)
                mapping, data_set, res_sort = data_mapping_to_tuple[f]
            elif isinstance(f, (tuple, list)):
                for f_ in f:
                    if f_ not in data_mapping_to_tuple:
                        log_error(logger, f"Field {f_} not found in data", DataError)
                    mapping_, data_set_, res_sort_ = data_mapping_to_tuple[f_]
                    mapping.append(mapping_)
                    data_set = data_set if data_set else data_set_
                    res_sort = res_sort if res_sort else res_sort_
                    assert data_set == data_set_
                    assert res_sort == res_sort_
            elif isinstance(f, dict):
                mapping = {k: [] for k in f.keys()}
                for k, f_ in f.items():
                    if f_ not in data_mapping_to_tuple:
                        log_error(logger, f"Field {f_} not found in data", DataError)
                    mapping_, data_set_, res_sort_ = data_mapping_to_tuple[f_]
                    mapping[k] = mapping_
                    data_set = data_set if data_set else data_set_
                    res_sort = res_sort if res_sort else res_sort_
                    assert data_set == data_set_
                    assert res_sort == res_sort_
            else:
                log_error(
                    logger, f"Field {f} is not a string, tuple, list or dict", DataError
                )
            tasks.append(
                report.create_report_data_set(
                    mapping_data_set_sort=(mapping, data_set, res_sort)
                )
            )

        report_data_sets = await asyncio.gather(*tasks)
        logger.info(
            f"Created {len(report_data_sets)} component data set links for component {str(report)}"
        )
        return report_data_sets

    def _update_options(self, options: dict, option_modifications: Optional[dict]):
        """Update the options of an echart.
        :param options: the options of the echart
        :param option_modifications: the modifications to apply to the options
        """
        if not option_modifications:
            return
        for k, v in option_modifications.items():
            if k == "series":
                log_error(logger, "Series cannot be modified", DataError)
            if k == "xAxis" or k == "yAxis":
                if isinstance(v, dict):
                    v = [v]
                if len(v) != len(options[k]):
                    log_error(logger, f"The number of {k} must be {len(v)}", DataError)
                for i, v_ in enumerate(v):
                    options[k][i].update(v_)
            else:
                options[k] = v

    async def _create_echart(
        self,
        options: dict,
        order: int,
        fields: list[Union[str, tuple, dict]],
        data_mapping_to_tuples: Optional[dict] = None,
        data: Optional[Union[str, pd.DataFrame]] = None,
        dump_whole: bool = False,
        option_modifications: Optional[dict] = None,
        title: Optional[str] = None,
        rows_size: Optional[int] = None,
        cols_size: Optional[int] = None,
        padding: Optional[str] = None,
    ):
        """
        Create an echart in the dashboard, fill in the data referenced in the echart_options and create or
        update the chart and data set links.
        :param options: the options of the echart
        :param data_mapping_to_tuples: the mapping of the data to the tuples
        :param data: the data of the echart
        :param dump_whole: whether to dump the whole data
        :param option_modifications: the modifications to apply to the options
        :param title: the title of the echart
        :param rows_size: the rows size of the echart
        :param cols_size: the columns size of the echart
        :param padding: the padding of the echart
        """

        if data is not None:
            data_mapping_to_tuples = await self._choose_data(
                order, data, dump_whole=dump_whole
            )

        data_key_entries = get_data_references_from_dict(options)
        _, report = await self._get_chart_report(order, EChart)

        rd_ids = None
        if self.reuse_data_sets:
            rd_ids = get_uuids_from_dict(report["properties"]["option"])
            if len(rd_ids) == len(fields):
                rep_ds: list[Report.ReportDataSet] = await report.get_report_data_sets()
                mapped_f = [
                    self._get_field_mapping(field, data_mapping_to_tuples)
                    for field in fields
                ]
                for i, rd_id in enumerate(rd_ids):
                    report_data_set = next(
                        (rd for rd in rep_ds if rd["id"] == rd_id), None
                    )
                    if (
                        not report_data_set
                        or not self._check_mapping_in_report_data_set(
                            report_data_set, mapped_f[i]
                        )
                    ):
                        rd_ids = None
                        break
            else:
                rd_ids = None

        if not rd_ids:
            await report.delete_report_data_sets(log=True)
            report_data_sets = await self._get_report_data_sets_per_mapping(
                report, data_mapping_to_tuples, fields
            )
            rd_ids = [rd["id"] for rd in report_data_sets]

        self._update_options(options, option_modifications)

        if len(rd_ids) != len(data_key_entries):
            log_error(
                logger,
                f"The number of data references and fields must be equal, "
                f"they are {len(data_key_entries)} and {len(rd_ids)} respectively.",
                DataError,
            )

        for i, data_key_entry in enumerate(data_key_entries):
            data = options
            for key in data_key_entry[:-1]:
                data = data[key]
            data[data_key_entry[-1]] = "#{" + rd_ids[i] + "}"

        await self._create_chart(
            chart_class=EChart,
            properties={"option": options},
            order=order,
            title=title,
            sizePadding=padding,
            sizeRows=rows_size,
            sizeColumns=cols_size,
        )

    @staticmethod
    def _apply_variant(echart_options: dict, variant: Optional[str]):
        if variant == "clean":
            echart_options.update(
                {"toolbox": {"show": False}, "legend": {"show": False}, "grid": {}}
            )
            for axislist in [echart_options["xAxis"], echart_options["yAxis"]]:
                for axis in axislist:
                    axis.update(
                        {"axisLine": {"show": False}, "axisTick": {"show": False}}
                    )
        elif variant == "minimal":
            echart_options.update(
                {
                    "toolbox": {"show": False},
                    "legend": {"show": False},
                    "grid": {"left": "1%", "right": "1%", "top": "1%", "bottom": "1%"},
                    "tooltip": {"show": False},
                }
            )
            for axislist in [echart_options["xAxis"], echart_options["yAxis"]]:
                for axis in axislist:
                    axis.update(
                        {
                            "axisLine": {"show": False},
                            "axisTick": {"show": False},
                            "splitLine": {"show": False},
                            "axisLabel": {"show": False},
                        }
                    )

    async def _create_trend_chart(
        self,
        axes: Union[list[str], str],
        order: int,
        data_mapping_to_tuples: Optional[dict],
        echart_options: dict,
        series_options: Union[dict, list[dict]],
        values: Optional[Union[list[Union[str, tuple]], str, tuple]] = None,
        x_axis_names: Optional[Union[str, list[str]]] = None,
        y_axis_names: Optional[Union[str, list[str]]] = None,
        show_values: Optional[Union[list[str], str]] = None,
        variant: Optional[str] = None,
        **report_params,
    ):
        """
        Create a line chart in the dashboard.
        :param data: the data of the chart
        :param axes: the names of the columns to be used as axis
        :param values: the names of the columns to be used as values
        :param x_axis_names: the name of the x axes
        :param y_axis_names: the name of the y axes
        :param echart_options: the options of the chart
        :param series_options: the options of the series of the chart
        :param bottom_toolbox: whether to show the toolbox on top of the chart
        :param order: the order of the chart in the dashboard
        :param report_params: additional report parameters as key-value pairs
        """
        self._apply_variant(echart_options, variant)
        if isinstance(axes, str):
            axes = [axes]
        if isinstance(values, str) or isinstance(values, tuple):
            values = [values]
        if show_values is None:
            show_values = []

        if "x_axis_name" in report_params:
            x_axis_names = [report_params["x_axis_name"]]
        elif isinstance(x_axis_names, str):
            x_axis_names = [x_axis_names]
        else:
            x_axis_names = []

        if "y_axis_name" in report_params:
            y_axis_names = [report_params["y_axis_name"]]
        elif isinstance(y_axis_names, str):
            y_axis_names = [y_axis_names]
        else:
            y_axis_names = []

        values = (
            [v for v in data_mapping_to_tuples.keys() if v not in axes]
            if values is None
            else values
        )
        if isinstance(series_options, dict):
            series_options = [series_options] * len(values)
        elif len(series_options) < len(values):
            series_options = series_options + [series_options[-1]] * (
                len(values) - len(series_options)
            )
        elif len(series_options) > len(values):
            series_options = series_options[: len(values)]

        echart_options["series"] = [
            deep_update(
                {
                    "name": name if isinstance(name, str) else " × ".join(name),
                    "label": {"show": show_values == "all" or name in show_values},
                },
                series_options[i],
            )
            for i, name in enumerate(values)
        ]

        for i, axis_options in enumerate(echart_options["xAxis"]):
            axis_options["name"] = x_axis_names[i] if i < len(x_axis_names) else None
            if axis_options["name"] and "nameGap" not in axis_options:
                axis_options["nameGap"] = 32

        for i, axis_options in enumerate(echart_options["yAxis"]):
            axis_options["name"] = y_axis_names[i] if i < len(y_axis_names) else None
            if axis_options["name"] and "nameGap" not in axis_options:
                axis_options["nameGap"] = -24
                axis_options["offset"] = 36
                echart_options["grid"]["left"] = "4%"
                axis_options["axisTick"] = {"show": False}
                axis_options["axisLine"] = {"show": False}

        await self._create_echart(
            order=order,
            options=echart_options,
            data_mapping_to_tuples=data_mapping_to_tuples,
            fields=axes + values,
            **report_params,
        )

    @add_to_general_async_group
    async def free_echarts(
        self,
        data: Optional[Union[str, DataFrame, list[dict]]] = None,
        options: Optional[dict] = None,
        raw_options: Optional[str] = None,
        order: Optional[int] = None,
        title: Optional[str] = None,
        rows_size: Optional[int] = None,
        cols_size: Optional[int] = None,
        padding: Optional[str] = None,
        fields: Optional[list] = None,
        data_is_not_df: bool = False,
    ):
        """
        Create an echarts chart with custom options.
        :param data: the data of the chart
        :param options: the options of the chart
        :param raw_options: the raw options of the chart
        :param order: the order of the chart in the dashboard
        :param title: the title of the chart
        :param rows_size: the rows size of the chart
        :param cols_size: the columns size of the chart
        :param padding: the padding of the chart
        :param fields: the fields of the chart
        :param data_is_not_df: whether the data is not a dataframe
        """
        if not options and not raw_options:
            log_error(
                logger, "Either options or raw_options must be provided", ValueError
            )
        if options and not isinstance(data, DataFrame) and data is None:
            log_error(
                logger, "data must be provided when options is provided", DataError
            )
        if options and raw_options:
            log_error(
                logger,
                "Only one of options and raw_options can be provided",
                ValueError,
            )

        if raw_options:
            options = transform_dict_js_to_py(raw_options)
            data = retrieve_data_from_options(options)
            options["dataset"] = {"source": "#set_data#"}
            fields = [list(data[0].keys())]
        else:
            options = deepcopy(options)

        await self._create_echart(
            order=order,
            data_mapping_to_tuples=await self._choose_data(
                order, data, dump_whole=data_is_not_df
            ),
            fields=fields,
            options=options,
            title=title,
            rows_size=rows_size,
            cols_size=cols_size,
            padding=padding,
        )

    # ECharts
    line = add_to_general_async_group(line_chart)
    bar = add_to_general_async_group(bar_chart)
    stacked_bar = add_to_general_async_group(stacked_bar_chart)
    area = add_to_general_async_group(area_chart)
    stacked_area = add_to_general_async_group(stacked_area_chart)
    scatter = add_to_general_async_group(scatter_chart)
    horizontal_bar = add_to_general_async_group(horizontal_bar_chart)
    stacked_horizontal_bar = add_to_general_async_group(stacked_horizontal_bar_chart)
    zero_centered_bar = add_to_general_async_group(zero_centered_bar_chart)
    funnel = add_to_general_async_group(funnel_chart)
    tree = add_to_general_async_group(tree_chart)
    radar = add_to_general_async_group(radar_chart)
    pie = add_to_general_async_group(pie_chart)
    doughnut = add_to_general_async_group(doughnut_chart)
    rose = add_to_general_async_group(rose_chart)
    sunburst = add_to_general_async_group(sunburst_chart)
    treemap = add_to_general_async_group(treemap_chart)
    sankey = add_to_general_async_group(sankey_chart)
    heatmap = add_to_general_async_group(heatmap_chart)
    predictive_line = add_to_general_async_group(predictive_line_chart)
    speed_gauge = add_to_general_async_group(speed_gauge_chart)
    shimoku_gauge = add_to_general_async_group(shimoku_gauge_chart)
    shimoku_gauges_group = add_to_general_async_group(shimoku_gauges_group)
    gauge_indicator = add_to_general_async_group(gauge_indicator)
    top_bottom_area = add_to_general_async_group(top_bottom_area_charts)
    top_bottom_line = add_to_general_async_group(top_bottom_line_charts)
    line_with_confidence_area = add_to_general_async_group(
        line_with_confidence_area_chart
    )
    scatter_with_effect = add_to_general_async_group(scatter_with_effect_chart)
    waterfall = add_to_general_async_group(waterfall_chart)
    line_and_bar_charts = add_to_general_async_group(line_and_bar_charts)
    segmented_line = add_to_general_async_group(segmented_line_chart)
    marked_line = add_to_general_async_group(marked_line_chart)
    segmented_area = add_to_general_async_group(segmented_area_chart)

    # Bentobox charts defined in the bentobox_charts.py file
    infographics_text_bubble = add_to_general_async_group(infographics_text_bubble)
    chart_and_modal_button = add_to_general_async_group(chart_and_modal_button)
    chart_and_indicators = add_to_general_async_group(chart_and_indicators)
    indicators_with_header = add_to_general_async_group(indicators_with_header)
    line_with_summary = add_to_general_async_group(line_with_summary)
