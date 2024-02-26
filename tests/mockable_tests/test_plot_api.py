from os import getenv, path
from typing import Dict, List
from time import perf_counter
import unittest

import pandas as pd

from shimoku import Client
from utils import initiate_shimoku

from test_plot_api_functions.data.default import data
from test_plot_api_functions.data.zero_centered import zero_centered_data
from test_plot_api_functions.data.funnel import funnel_data
from test_plot_api_functions.data.heatmap import heatmap_data
from test_plot_api_functions.data.tree import tree_data
from test_plot_api_functions.data.noise import noise_data
from test_plot_api_functions.data.table import table_data
from test_plot_api_functions.data.horizontal_bar import horizontal_bar_data

from test_plot_api_functions.chart_and_indicators import chart_and_indicators
from test_plot_api_functions.infographics import infographics
from test_plot_api_functions.marked_line import marked_line_chart
from test_plot_api_functions.pie import pie
from test_plot_api_functions.radar import radar
from test_plot_api_functions.rose import rose
from test_plot_api_functions.scatter import scatter
from test_plot_api_functions.speed_gauge import speed_gauge
from test_plot_api_functions.stacked_area import stacked_area_chart
from test_plot_api_functions.stacked_bar import stacked_bar_chart
from test_plot_api_functions.summary_line import summary_line
from test_plot_api_functions.table import table
from test_plot_api_functions.tabs import tabs
from test_plot_api_functions.tree import tree
from test_plot_api_functions.treemap import treemap
from test_plot_api_functions.sankey import sankey
from test_plot_api_functions.heatmap import heatmap
from test_plot_api_functions.line import line
from test_plot_api_functions.area import area
from test_plot_api_functions.bar import bar
from test_plot_api_functions.horizontal_bar import horizontal_bar_chart
from test_plot_api_functions.zero_centered_bar import zero_centered_bar_chart
from test_plot_api_functions.funnel import funnel
from test_plot_api_functions.iframe import iframe
from test_plot_api_functions.bentobox import bentobox
from test_plot_api_functions.rainfall_area import rainfall_area
from test_plot_api_functions.rainfall_line import rainfall_line
from test_plot_api_functions.line_with_confidence_area import line_with_confidence_area
from test_plot_api_functions.scatter_with_effect import scatter_with_effect
from test_plot_api_functions.waterfall import waterfall
from test_plot_api_functions.bar_and_line_chart import bar_and_line_chart
from test_plot_api_functions.segmented_line_chart import segmented_line_chart
from test_plot_api_functions.segmented_area_chart import segmented_area_chart
from test_plot_api_functions.variants import variants
from test_plot_api_functions.annotation_chart import annotation_chart
from test_plot_api_functions.shimoku_gauges import shimoku_gauges
from test_plot_api_functions.gauge_indicator import gauge_indicators
from test_plot_api_functions.free_echarts import free_echarts
from test_plot_api_functions.input_form import input_form
from test_plot_api_functions.dynamic_conditional_and_auto_send_input_form import (
    dynamic_conditional_and_auto_send_input_form,
)
from test_plot_api_functions.get_input_forms import get_input_forms
from test_plot_api_functions.indicator import indicator
from test_plot_api_functions.indicator_color_by_value import indicator_color_by_value
from test_plot_api_functions.predictive_line import predictive_line
from test_plot_api_functions.html import html
from test_plot_api_functions.modal import modal
from test_plot_api_functions.doughnut import doughnut
from test_plot_api_functions.sunburst import sunburst
from test_plot_api_functions.table_with_lables import table_with_labels
from test_plot_api_functions.stacked_horizontal_bar import stacked_horizontal_bar_chart

data_path = path.join(
    path.dirname(path.abspath(__file__)), "test_plot_api_functions", "data"
)


class TestPlotApi(unittest.TestCase):
    def setUp(self):
        self.mock: bool = getenv("MOCK") == "TRUE"
        self.shimoku_client: Client = initiate_shimoku()
        self.shimoku_client.reuse_data_sets()
        self.workspace_id: str = getenv("BUSINESS_ID")
        self.shimoku_client.set_workspace(uuid=self.workspace_id)

    def test_delete_path(self):
        init_time = perf_counter()
        ini_calls = self.shimoku_client.get_api_calls_counter()
        menu_path: str = "test-path"
        sub_path: str = "line-test"
        sub_path_2: str = "line-test-2"
        sub_path_3: str = "line-test-3"

        self.shimoku_client.set_menu_path(menu_path)
        self.shimoku_client.plt.clear_menu_path()

        self.shimoku_client.set_menu_path(menu_path, sub_path)

        self.shimoku_client.plt.line(data=data, x="date", order=0)
        self.shimoku_client.plt.line(data=data, x="date", order=1)

        reports: List[Dict] = self.shimoku_client.menu_paths.get_menu_path_components(
            name=menu_path
        )
        assert len(reports) == 2

        self.shimoku_client.plt.clear_menu_path()

        assert (
            len(self.shimoku_client.menu_paths.get_menu_path_components(name=menu_path))
            == 0
        )
        for i in range(10):
            self.shimoku_client.plt.line(data=data, x="date", order=i)

        self.shimoku_client.set_menu_path(menu_path, sub_path_2)
        self.shimoku_client.plt.line(data=data, x="date", order=0)

        self.shimoku_client.set_menu_path(menu_path, sub_path_3)
        self.shimoku_client.plt.line(data=data, x="date", order=0)

        assert (
            len(self.shimoku_client.menu_paths.get_menu_path_components(name=menu_path))
            == 12
        )

        self.shimoku_client.set_menu_path(menu_path, sub_path)
        self.shimoku_client.plt.clear_menu_path()
        assert (
            len(self.shimoku_client.menu_paths.get_menu_path_components(name=menu_path))
            == 2
        )

        self.shimoku_client.set_menu_path(menu_path)
        self.shimoku_client.plt.clear_menu_path()
        assert (
            len(self.shimoku_client.menu_paths.get_menu_path_components(name=menu_path))
            == 0
        )

        self.shimoku_client.set_menu_path("test")
        self.shimoku_client.menu_paths.delete_menu_path(name=menu_path)

        print(f"Total elapsed time: {perf_counter() - init_time:.2f} s")
        print(
            f"Number of api calls {self.shimoku_client.get_api_calls_counter() - ini_calls}"
        )

    def test_delete(self):
        init_time = perf_counter()
        ini_calls = self.shimoku_client.get_api_calls_counter()
        self.shimoku_client.set_menu_path("test-delete", "line-test")
        self.shimoku_client.plt.line(data=data, x="date", order=0)
        assert self.shimoku_client.menu_paths.get_menu_path_components(
            name="test-delete"
        )
        self.shimoku_client.plt.delete_chart_by_order(order=0)
        assert not self.shimoku_client.menu_paths.get_menu_path_components(
            name="test-delete"
        )
        self.shimoku_client.set_menu_path("test")
        self.shimoku_client.menu_paths.delete_menu_path(name="test-delete")
        print(f"Total elapsed time: {perf_counter() - init_time:.2f} s")
        print(
            f"Number of api calls {self.shimoku_client.get_api_calls_counter() - ini_calls}"
        )

    def test_charts(self):
        init_time = perf_counter()
        ini_calls = self.shimoku_client.get_api_calls_counter()

        self.shimoku_client.set_menu_path("test")
        self.shimoku_client.plt.set_shared_data(
            dfs={
                "main data": data,
                "zero centered data": zero_centered_data,
                "funnel data": funnel_data,
                "heatmap data": heatmap_data,
            },
            custom_data={
                "tree_data": tree_data,
            },
        )
        indicator(self.shimoku_client)
        indicator_color_by_value(self.shimoku_client)
        speed_gauge(self.shimoku_client)
        line(self.shimoku_client)
        predictive_line(self.shimoku_client)
        bar(self.shimoku_client)
        scatter(self.shimoku_client)
        area(self.shimoku_client)
        horizontal_bar_chart(self.shimoku_client)
        zero_centered_bar_chart(self.shimoku_client)
        funnel(self.shimoku_client)
        iframe(self.shimoku_client)
        bentobox(self.shimoku_client)
        radar(self.shimoku_client)
        pie(self.shimoku_client)
        rose(self.shimoku_client)
        doughnut(self.shimoku_client)
        html(self.shimoku_client)
        tree(self.shimoku_client)
        sunburst(self.shimoku_client)
        treemap(self.shimoku_client)
        sankey(self.shimoku_client)
        heatmap(self.shimoku_client)
        table(self.shimoku_client)
        self.shimoku_client.update_data_sets()
        table_with_labels(self.shimoku_client)
        self.shimoku_client.reuse_data_sets()
        annotation_chart(self.shimoku_client)
        self.shimoku_client.run()
        print(f"Total elapsed time: {perf_counter() - init_time:.2f} s")
        print(
            f"Number of api calls {self.shimoku_client.get_api_calls_counter() - ini_calls}"
        )

    def test_free_echarts(self):
        init_time = perf_counter()
        ini_calls = self.shimoku_client.get_api_calls_counter()
        self.shimoku_client.set_menu_path("test-free-echarts")
        stacked_data = pd.read_csv(path.join(data_path, "test_stack_distribution.csv"))
        self.shimoku_client.plt.set_shared_data(
            {
                "stacked data": stacked_data,
                "noise": noise_data,
                "table": table_data,
                "horizontal bar": horizontal_bar_data,
            }
        )
        stacked_bar_chart(self.shimoku_client)
        stacked_horizontal_bar_chart(self.shimoku_client)
        stacked_area_chart(self.shimoku_client)
        shimoku_gauges(self.shimoku_client)
        gauge_indicators(self.shimoku_client)
        free_echarts(self.shimoku_client)
        rainfall_area(self.shimoku_client)
        rainfall_line(self.shimoku_client)
        line_with_confidence_area(self.shimoku_client)
        scatter_with_effect(self.shimoku_client)
        waterfall(self.shimoku_client)
        bar_and_line_chart(self.shimoku_client)
        segmented_line_chart(self.shimoku_client)
        segmented_area_chart(self.shimoku_client)
        marked_line_chart(self.shimoku_client)
        variants(self.shimoku_client)
        self.shimoku_client.run()
        print(f"Total elapsed time: {perf_counter() - init_time:.2f} s")
        print(
            f"Number of api calls {self.shimoku_client.get_api_calls_counter() - ini_calls}"
        )

    def test_bento_box(self):
        init_time = perf_counter()
        ini_calls = self.shimoku_client.get_api_calls_counter()
        infographics(self.shimoku_client)
        chart_and_indicators(self.shimoku_client)
        summary_line(self.shimoku_client)
        self.shimoku_client.run()
        print(f"Total elapsed time: {perf_counter() - init_time:.2f} s")
        print(
            f"Number of api calls {self.shimoku_client.get_api_calls_counter() - ini_calls}"
        )

    def test_filters(self):
        init_time = perf_counter()
        ini_calls = self.shimoku_client.get_api_calls_counter()
        self.shimoku_client.set_board("Test")
        self.shimoku_client.set_menu_path("test-filters")
        self.shimoku_client.plt.set_shared_data(
            dfs={
                "table": pd.DataFrame(table_data),
            }
        )
        self.shimoku_client.plt.filter(order=0, data="table", field="date")
        self.shimoku_client.plt.filter(order=1, data="table", field="x")
        self.shimoku_client.plt.filter(order=2, data="table", field="filtA")
        self.shimoku_client.plt.filter(
            order=3, data="table", field="filtB", multi_select=True, padding="0,0,0,8"
        )

        self.shimoku_client.plt.bar(
            data="table", order=4, cols_size=6, x="date", y=["x", "y"]
        )
        self.shimoku_client.plt.line(
            data="table", order=5, cols_size=6, x="date", y=["x", "y"]
        )
        self.shimoku_client.plt.stacked_bar(
            data="table", x="date", y=["x", "y"], order=6
        )
        self.shimoku_client.plt.table(
            data=table_data * 10,
            order=7,
            rows_size=3,
            title="Table test",
            categorical_columns=["filtA", "filtB"],
        )
        self.shimoku_client.run()
        print(f"Total elapsed time: {perf_counter() - init_time:.2f} s")
        print(
            f"Number of api calls {self.shimoku_client.get_api_calls_counter() - ini_calls}"
        )

    def test_tabs(self):
        init_time = perf_counter()
        ini_calls = self.shimoku_client.get_api_calls_counter()
        self.shimoku_client.set_board("Tabs dashboard")
        tabs(self.shimoku_client)
        self.shimoku_client.run()
        print(f"Total elapsed time: {perf_counter() - init_time:.2f} s")
        print(
            f"Number of api calls {self.shimoku_client.get_api_calls_counter() - ini_calls}"
        )

    def test_modals(self):
        init_time = perf_counter()
        ini_calls = self.shimoku_client.get_api_calls_counter()
        self.shimoku_client.set_board("Modals dashboard")
        modal(self.shimoku_client)
        self.shimoku_client.run()
        print(f"Total elapsed time: {perf_counter() - init_time:.2f} s")
        print(
            f"Number of api calls {self.shimoku_client.get_api_calls_counter() - ini_calls}"
        )

    def test_forms(self):
        init_time = perf_counter()
        ini_calls = self.shimoku_client.get_api_calls_counter()
        self.shimoku_client.set_board("Others")
        input_form(self.shimoku_client)
        dynamic_conditional_and_auto_send_input_form(self.shimoku_client)
        get_input_forms(self.shimoku_client)
        self.shimoku_client.run()
        print(f"Total elapsed time: {perf_counter() - init_time:.2f} s")
        print(
            f"Number of api calls {self.shimoku_client.get_api_calls_counter() - ini_calls}"
        )

    def test_menu_order(self):
        init_time = perf_counter()
        ini_calls = self.shimoku_client.get_api_calls_counter()
        self.shimoku_client.workspaces.change_boards_order(
            uuid=self.workspace_id,
            boards=[
                "Default Name",
                "Test",
                "Modals dashboard",
                "Tabs dashboard",
                "Others",
                "---",
            ],
        )
        self.shimoku_client.workspaces.change_menu_order(
            uuid=self.workspace_id,
            menu_order=[
                "---",
                (
                    "test",
                    [
                        "line-test",
                        "bar-test",
                        "pie-test",
                        "area-test",
                        "scatter-test",
                        "radar-test",
                    ],
                ),
                (
                    "test-bentobox",
                    [
                        "chart-and-indicators",
                        "Infographics",
                    ],
                ),
                "test-free-echarts",
            ],
        )
        print(f"Total elapsed time: {perf_counter() - init_time:.2f} s")
        print(
            f"Number of api calls {self.shimoku_client.get_api_calls_counter() - ini_calls}"
        )

    def test_same_position_charts(self):
        init_time = perf_counter()
        ini_calls = self.shimoku_client.get_api_calls_counter()
        self.shimoku_client.set_menu_path("test-same-position", "no conflict path 1")

        self.shimoku_client.activate_async_execution()

        self.shimoku_client.plt.clear_menu_path()
        self.shimoku_client.plt.gauge_indicator(
            order=0,
            value=83,
            description="Síntomas coincidientes | Mareo, Dolor cervical",
            title="Sobrecarga muscular en cervicales y espalda",
        )

        self.shimoku_client.set_menu_path("test-same-position", "no conflict path 2")
        self.shimoku_client.plt.gauge_indicator(
            order=1,
            value=31,
            color=2,
            description="Síntomas coincidientes | Dolor cervical",
            title="Bruxismo",
        )

        self.shimoku_client.set_menu_path("test-same-position", "no conflict tabs")
        self.shimoku_client.plt.set_tabs_index(tabs_index=("tabs", "1"), order=0)
        self.shimoku_client.plt.gauge_indicator(
            order=0,
            value=83,
            description="Síntomas coincidientes | Mareo, Dolor cervical",
            title="Sobrecarga muscular en cervicales y espalda",
        )

        self.shimoku_client.plt.change_current_tab("2")
        self.shimoku_client.plt.gauge_indicator(
            order=1,
            value=31,
            color=2,
            description="Síntomas coincidientes | Dolor cervical",
            title="Bruxismo",
        )

        self.shimoku_client.plt.pop_out_of_tabs_group()
        self.shimoku_client.run()

        with self.assertRaises(RuntimeError):
            self.shimoku_client.set_menu_path("test-same-position", "conflict")
            self.shimoku_client.plt.gauge_indicator(
                order=0,
                value=83,
                description="Síntomas coincidientes | Mareo, Dolor cervical",
                title="Sobrecarga muscular en cervicales y espalda",
            )

            self.shimoku_client.plt.gauge_indicator(
                order=1,
                value=31,
                color=2,
                description="Síntomas coincidientes | Dolor cervical",
                title="Bruxismo",
            )
            self.shimoku_client.run()

        self.shimoku_client._async_pool.in_async = False

        with self.assertRaises(RuntimeError):
            self.shimoku_client.set_menu_path("test-same-position", "conflict")
            self.shimoku_client.plt.set_tabs_index(
                tabs_index=("conflict", "conflict"), order=0
            )
            self.shimoku_client.plt.gauge_indicator(
                order=0,
                value=83,
                description="Síntomas coincidientes | Mareo, Dolor cervical",
                title="Sobrecarga muscular en cervicales y espalda",
            )

            self.shimoku_client.plt.gauge_indicator(
                order=1,
                value=31,
                color=2,
                description="Síntomas coincidientes | Dolor cervical",
                title="Bruxismo",
            )
            self.shimoku_client.run()

        self.shimoku_client._async_pool.in_async = False

        self.shimoku_client.set_menu_path("test-same-position")
        self.shimoku_client.plt.clear_menu_path()

        assert 0 == len(
            self.shimoku_client.menu_paths.get_menu_path_components(
                name="test-same-position"
            )
        )

        self.shimoku_client.set_menu_path("test")
        self.shimoku_client.menu_paths.delete_menu_path(name="test-same-position")

        print(f"Total elapsed time: {perf_counter() - init_time:.2f} s")
        print(
            f"Number of api calls {self.shimoku_client.get_api_calls_counter() - ini_calls}"
        )

    def test_no_re_append_app_to_dashboard(self):
        if self.mock:
            return
        init_time = perf_counter()
        ini_calls = self.shimoku_client.get_api_calls_counter()

        self.shimoku_client.set_board("Test")
        self.shimoku_client.set_menu_path("test-no-reappend")
        self.shimoku_client.pop_out_of_menu_path()
        how_many_apps = len(
            self.shimoku_client.boards.get_board_menu_path_ids(name="Test")
        )
        self.shimoku_client.set_menu_path("test-no-reappend")
        self.shimoku_client.pop_out_of_menu_path()
        assert how_many_apps == len(
            self.shimoku_client.boards.get_board_menu_path_ids(name="Test")
        )

        s2 = initiate_shimoku()
        s2.set_workspace(self.workspace_id)
        s2.set_board("Test")
        s2.set_menu_path("test-no-reappend")
        s2.pop_out_of_menu_path()
        assert how_many_apps == len(s2.boards.get_board_menu_path_ids(name="Test"))

        self.shimoku_client.menu_paths.delete_menu_path(name="test-no-reappend")

        print(f"Total elapsed time: {perf_counter() - init_time:.2f} s")
        print(
            f"Number of api calls {self.shimoku_client.get_api_calls_counter() - ini_calls}"
        )

    def test_un_cached_modal(self):
        self.shimoku_client.disable_caching()
        self.shimoku_client.set_workspace(uuid=self.workspace_id)
        self.shimoku_client.set_menu_path("Un-cached modal test path")
        self.shimoku_client.plt.clear_menu_path()

        self.shimoku_client.plt.set_modal("Un-cached Modal")
        self.shimoku_client.plt.html(html="<h1>test</h1>", order=0)

        self.shimoku_client.run()

        res_html = self.shimoku_client.plt.get_component_by_order(0)
        assert res_html is not None
        assert res_html["chartData"][0]["value"] == "<h1>test</h1>"
        assert res_html["order"] == 0
        self.shimoku_client.plt.pop_out_of_modal()

        html_id = res_html["id"]
        modal_obj = self.shimoku_client.plt.get_modal("Un-cached Modal")
        assert html_id in modal_obj["properties"]["reportIds"]

        res_html = self.shimoku_client.plt.get_component_by_order(0)
        assert not res_html

        self.shimoku_client.enable_caching()


def main():
    # profiler = cProfile.Profile()
    # profiler.enable()
    my_test_plot_api = TestPlotApi()
    my_test_plot_api.setUp()
    for test in TestPlotApi.__dict__:
        if test.startswith("test_"):
            getattr(my_test_plot_api, test)()
    # profiler.disable()
    # stats = pstats.Stats(profiler)
    # stats.dump_stats('profile_output.prof')


if __name__ == "__main__":
    main()
