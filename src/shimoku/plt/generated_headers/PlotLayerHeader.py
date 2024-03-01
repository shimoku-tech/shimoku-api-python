# This file was generated automatically by scripts/user_classes_header_generator.py do not modify it!
# If the user access files are modified, this file has to be regenerated with the script.
from typing import Optional, Union
from pandas import DataFrame


class PlotLayerHeader:
    """
    This class is a high level abstraction of the API, it is used to create components and data sets easily.
    """

    def activity_button(
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
        pass

    def annotated_chart(
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
        pass

    def area(
        self,
        data: Union[str, DataFrame, list[dict]],
        order: int,
        x: str,
        y: Union[list[str], str, None] = None,
        rows_size: Optional[int] = None,
        cols_size: Optional[int] = None,
        padding: Optional[str] = None,
        title: Optional[str] = None,
        x_axis_name: Optional[str] = None,
        y_axis_name: Optional[str] = None,
        show_values: Union[list[str], str, None] = None,
        option_modifications: Optional[dict] = None,
        variant: Optional[str] = None,
    ):
        """Create an area chart"""
        pass

    def bar(
        self,
        data: Union[str, DataFrame, list[dict]],
        order: int,
        x: str,
        y: Union[list[str], str, None] = None,
        rows_size: Optional[int] = None,
        cols_size: Optional[int] = None,
        padding: Optional[str] = None,
        title: Optional[str] = None,
        x_axis_name: Optional[str] = None,
        y_axis_name: Optional[str] = None,
        show_values: Union[list[str], str, None] = None,
        option_modifications: Optional[dict] = None,
        variant: Optional[str] = None,
    ):
        """Create a bar chart"""
        pass

    def button(
        self,
        label: str,
        order: int,
        rows_size: Optional[int] = 1,
        cols_size: int = 2,
        align: Optional[str] = "stretch",
        padding: Optional[str] = None,
        on_click_events: Union[list[dict], dict, None] = None,
    ):
        """Create a button in the dashboard."""
        pass

    def change_current_tab(
        self,
        tab: str,
    ):
        """
        Change the current tab.
        :param tab: the name of the tab
        """
        pass

    def change_path(
        self,
        path: str,
    ):
        """Change the current path"""
        pass

    def chart_and_indicators(
        self,
        order: int,
        chart_parameters: dict,
        indicators_groups: list,
        indicators_parameters: Optional[dict] = None,
        chart_rows_size: int = 3,
        cols_size: int = 12,
        chart_function: Optional[callable] = None,
    ) -> int:
        """None"""
        pass

    def chart_and_modal_button(
        self,
        order: int,
        chart_parameters: dict,
        button_modal: str,
        rows_size: int = 3,
        cols_size: int = 12,
        chart_function: Optional[callable] = None,
        button_label: str = "Read more",
        button_side_text: str = "Click on the button to read more about this topic.",
    ):
        """None"""
        pass

    def clear_context(
        self,
    ):
        """None"""
        pass

    def clear_menu_path(
        self,
    ):
        """
        Clear the current path or a subpath
        """
        pass

    def delete_chart_by_order(
        self,
        order: int,
    ):
        """
        Delete a report by order and context
        """
        pass

    def delete_modal(
        self,
        name: str,
    ):
        """Delete a modal"""
        pass

    def delete_tabs_group(
        self,
        name: str,
    ):
        """Delete a tabs group"""
        pass

    def doughnut(
        self,
        order: int,
        names: str,
        values: str,
        data: Union[str, DataFrame, list[dict]],
        title: Optional[str] = None,
        rows_size: Optional[int] = 2,
        cols_size: Optional[int] = 3,
        padding: Optional[str] = None,
        option_modifications: Optional[dict] = None,
    ):
        """Create a doughnut chart"""
        pass

    def filter(
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
        pass

    def free_echarts(
        self,
        data: Union[str, DataFrame, list[dict], None] = None,
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
        pass

    def funnel(
        self,
        order: int,
        names: str,
        values: str,
        data: Union[str, DataFrame, list[dict]],
        title: Optional[str] = None,
        rows_size: Optional[int] = None,
        cols_size: Optional[int] = None,
        padding: Optional[str] = None,
        option_modifications: Optional[dict] = None,
    ):
        """Create a scatter chart"""
        pass

    def gauge_indicator(
        self,
        order: int,
        value: int,
        title: Optional[str] = "",
        description: Optional[str] = "",
        cols_size: Optional[int] = 6,
        rows_size: Optional[int] = 1,
        color: Union[str, int] = 1,
    ):
        """Create a gauge indicator"""
        pass

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
        pass

    def get_component_by_order(
        self,
        order: int,
    ) -> Optional[dict]:
        """Get the component by order.
        :param order: the order of the component
        """
        pass

    def get_input_forms(
        self,
    ) -> list:
        """Get all the input forms in the current menu_path."""
        pass

    def get_modal(
        self,
        modal_name: str,
    ) -> Optional[dict]:
        """Get the modal.
        :param modal_name: the name of the modal
        """
        pass

    def get_shared_data_names(
        self,
    ) -> list:
        """Get the names of the shared data"""
        pass

    def get_tabs_group(
        self,
        tabs_index: tuple,
    ) -> Optional[dict]:
        """Get the tabs group.
        :param tabs_index: the index of the tabs group
        """
        pass

    def heatmap(
        self,
        order: int,
        x: str,
        y: str,
        values: str,
        data: Union[list[dict], DataFrame, str],
        color_range: Optional[tuple[int, int]] = None,
        x_axis_name: Optional[str] = None,
        y_axis_name: Optional[str] = None,
        title: Optional[str] = None,
        padding: Optional[str] = None,
        rows_size: Optional[int] = None,
        cols_size: Optional[int] = None,
        calculate_color_range: Optional[bool] = False,
        continuous: Optional[bool] = False,
        option_modifications: Optional[dict] = None,
        variant: Optional[str] = None,
    ):
        """Create a heatmap chart"""
        pass

    def horizontal_bar(
        self,
        data: Union[str, DataFrame, list[dict]],
        order: int,
        x: str,
        y: Union[list[str], str, None] = None,
        rows_size: Optional[int] = None,
        cols_size: Optional[int] = None,
        padding: Optional[str] = None,
        title: Optional[str] = None,
        x_axis_name: Optional[str] = None,
        y_axis_name: Optional[str] = None,
        show_values: Union[list[str], str, None] = None,
        option_modifications: Optional[dict] = None,
        variant: Optional[str] = None,
    ):
        """Create a horizontal bar chart"""
        pass

    def html(
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
        pass

    def iframe(
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
        pass

    def indicator(
        self,
        data: Union[str, DataFrame, list[dict], dict],
        order: int,
        vertical: Union[bool, str] = False,
        color_by_value: bool = False,
        cols_size: int = 12,
        rows_size: int = 1,
        padding: Optional[str] = None,
        **kwargs,
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
        pass

    def indicators_with_header(
        self,
        order: int,
        indicators_groups: list,
        title: str,
        indicators_parameters: Optional[dict] = None,
        subtitle: str = "",
        background_color: str = "var(--color-primary)",
        text_color: str = "var(--background-paper)",
        cols_size: int = 12,
        icon_url: str = "https://uploads-ssl.webflow.com/619f9fe98661d321dc3beec7/63e3615716d4435d29e0b82c_Acurracy.svg",
    ) -> int:
        """None"""
        pass

    def infographics_text_bubble(
        self,
        title: str,
        text: str,
        order: int,
        chart_parameters: dict,
        rows_size: int = 3,
        cols_size: int = 12,
        chart_function: Optional[callable] = None,
        background_url: Optional[str] = None,
        background_color: str = "var(--background-default)",
        bubble_location: str = "top",
        image_url: Optional[str] = None,
        image_size: int = 100,
    ):
        """None"""
        pass

    def input_form(
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
        pass

    def line(
        self,
        data: Union[str, DataFrame, list[dict]],
        order: int,
        x: str,
        y: Union[list[str], str, None] = None,
        rows_size: Optional[int] = None,
        cols_size: Optional[int] = None,
        padding: Optional[str] = None,
        title: Optional[str] = None,
        x_axis_name: Optional[str] = None,
        y_axis_name: Optional[str] = None,
        show_values: Union[list[str], str, None] = None,
        option_modifications: Optional[dict] = None,
        variant: Optional[str] = None,
    ):
        """Create a line chart"""
        pass

    def line_and_bar_charts(
        self,
        order: int,
        x: str,
        data: Union[str, DataFrame, list[dict], None],
        bar_names: Optional[list[str]] = None,
        line_names: Optional[list[str]] = None,
        x_axis_name: Optional[str] = None,
        bar_axis_name: Optional[str] = None,
        bar_suffix: Optional[str] = None,
        line_axis_name: Optional[str] = None,
        line_suffix: Optional[str] = None,
        title: Optional[str] = None,
        rows_size: Optional[int] = None,
        cols_size: Optional[int] = None,
        padding: Optional[str] = None,
        option_modifications: Optional[dict] = None,
        variant: Optional[str] = None,
    ):
        """Create a chart with bars and lines."""
        pass

    def line_with_confidence_area(
        self,
        data: Union[str, DataFrame, list[dict]],
        order: int,
        x: str,
        lower: str,
        y: str,
        upper: str,
        rows_size: Optional[int] = None,
        cols_size: Optional[int] = None,
        padding: Optional[str] = None,
        title: Optional[str] = None,
        x_axis_name: Optional[str] = None,
        y_axis_name: Optional[str] = None,
        percentages: bool = False,
        option_modifications: Optional[dict] = None,
        variant: Optional[str] = None,
    ):
        """None"""
        pass

    def line_with_summary(
        self,
        order: int,
        data: Union[str, DataFrame, list[dict]],
        title: str,
        x: str,
        y: Union[str, list[str], None] = None,
        description: str = "",
        value: Union[str, float, int] = "",
        rows_size: int = 2,
        cols_size: int = 2,
    ):
        """None"""
        pass

    def marked_line(
        self,
        data: Union[str, DataFrame, list[dict]],
        order: int,
        x: str,
        marks: list,
        y: Union[list[str], str, None] = None,
        color_mark: str = "rgba(255, 173, 177, 0.4)",
        x_axis_name: Optional[str] = None,
        y_axis_name: Optional[str] = None,
        title: Optional[str] = None,
        rows_size: Optional[int] = None,
        cols_size: Optional[int] = None,
        padding: Optional[str] = None,
        show_values: Union[list[str], str, None] = None,
        option_modifications: Optional[dict] = None,
        variant: Optional[str] = None,
    ):
        """Create a predictive line chart"""
        pass

    def modal_button(
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
        pass

    def pie(
        self,
        order: int,
        names: str,
        values: str,
        data: Union[str, DataFrame, list[dict]],
        title: Optional[str] = None,
        rows_size: Optional[int] = 2,
        cols_size: Optional[int] = 3,
        padding: Optional[str] = None,
        option_modifications: Optional[dict] = None,
    ):
        """Create a pie chart"""
        pass

    def pop_out_of_bentobox(
        self,
    ):
        """Stop using a bentobox"""
        pass

    def pop_out_of_modal(
        self,
    ):
        """Pop the current modal."""
        pass

    def pop_out_of_tabs_group(
        self,
    ):
        """
        Pop the current tabs index.
        """
        pass

    def predictive_line(
        self,
        data: Union[str, DataFrame, list[dict]],
        order: int,
        x: str,
        y: Union[list[str], str, None] = None,
        min_value_mark: Union[str, int, None] = None,
        max_value_mark: Union[str, int, None] = None,
        color_mark: str = "rgba(255, 173, 177, 0.4)",
        x_axis_name: Optional[str] = None,
        y_axis_name: Optional[str] = None,
        title: Optional[str] = None,
        rows_size: Optional[int] = None,
        cols_size: Optional[int] = None,
        padding: Optional[str] = None,
        show_values: Union[list[str], str, None] = None,
        option_modifications: Optional[dict] = None,
        variant: Optional[str] = None,
    ):
        """Create a predictive line chart"""
        pass

    def radar(
        self,
        order: int,
        names: str,
        data: Union[str, DataFrame, list[dict]],
        values: Optional[list[str]] = None,
        max_field: Optional[str] = None,
        fill_area: bool = False,
        title: Optional[str] = None,
        rows_size: Optional[int] = None,
        cols_size: Optional[int] = None,
        padding: Optional[str] = None,
        option_modifications: Optional[dict] = None,
    ):
        """Create a radar chart"""
        pass

    def raise_if_cant_change_path(
        self,
    ):
        """Raise an error if a tabs group or a modal is already open."""
        pass

    def rose(
        self,
        order: int,
        names: str,
        values: str,
        data: Union[str, DataFrame, list[dict]],
        title: Optional[str] = None,
        rows_size: Optional[int] = 2,
        cols_size: Optional[int] = 3,
        padding: Optional[str] = None,
        option_modifications: Optional[dict] = None,
    ):
        """Create a rose chart"""
        pass

    def sankey(
        self,
        order: int,
        sources: str,
        targets: str,
        values: str,
        data: list,
        option_modifications: Optional[dict] = None,
        title: Optional[str] = None,
        padding: Optional[str] = None,
        rows_size: Optional[int] = None,
        cols_size: Optional[int] = None,
    ):
        """Create a sankey chart"""
        pass

    def scatter(
        self,
        order: int,
        point_fields: Union[list[tuple[str, str]], tuple[str, str]],
        data: Union[str, DataFrame, list[dict]],
        x_axis_name: Optional[str] = None,
        y_axis_name: Optional[str] = None,
        title: Optional[str] = None,
        rows_size: Optional[int] = None,
        cols_size: Optional[int] = None,
        padding: Optional[str] = None,
        show_values: Union[list[str], str, None] = None,
        option_modifications: Optional[dict] = None,
        variant: Optional[str] = None,
    ):
        """Create a scatter chart"""
        pass

    def scatter_with_effect(
        self,
        order: int,
        x: str,
        y: str,
        data: Union[list[str], DataFrame, list[dict], None],
        x_axis_name: Optional[str] = None,
        y_axis_name: Optional[str] = None,
        title: Optional[str] = None,
        rows_size: Optional[int] = None,
        cols_size: Optional[int] = None,
        padding: Optional[str] = None,
        effect_points: Optional[list] = None,
        option_modifications: Optional[dict] = None,
    ):
        """Create a scatter chart"""
        pass

    def segmented_area(
        self,
        data: Union[str, DataFrame, list[dict]],
        order: int,
        x: str,
        y: str,
        segments: Optional[list] = None,
        x_axis_name: Optional[str] = None,
        y_axis_name: Optional[str] = None,
        default_color: tuple = (255, 0, 0),
        title: Optional[str] = None,
        rows_size: Optional[int] = None,
        cols_size: Optional[int] = None,
        padding: Optional[str] = None,
        show_values: Union[list[str], str, None] = None,
        option_modifications: Optional[dict] = None,
        variant: Optional[str] = None,
        top_area: bool = False,
        threshold: Optional[float] = None,
        labels: Optional[list[str]] = None,
    ):
        """Create a segmented area chart"""
        pass

    def segmented_line(
        self,
        order: int,
        x: str,
        y: Union[str, list[str]],
        data: Union[str, DataFrame, list[dict], None],
        x_axis_name: Optional[str] = None,
        y_axis_name: Optional[str] = None,
        rows_size: Optional[int] = None,
        cols_size: Optional[int] = None,
        padding: Optional[str] = None,
        title: Optional[str] = None,
        marking_lines: Optional[list[int]] = None,
        range_colors: Optional[list[str]] = None,
        option_modifications: Optional[dict] = None,
        variant: Optional[str] = None,
    ):
        """Create a chart with bars and lines."""
        pass

    def set_bentobox(
        self,
        cols_size: int,
        rows_size: int,
    ):
        """Start using a bentobox, the id and the order will be set when the bentobox is used for the first time
        :param cols_size: the number of columns in the bentobox
        :param rows_size: the number of rows in the bentobox"""
        pass

    def set_modal(
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
        pass

    def set_shared_data(
        self,
        dfs: dict = None,
        custom_data: dict = None,
    ):
        """
        Set shared data for the s.plt to use.
        :param dfs: the data frames
        :param custom_data: the custom data
        """
        pass

    def set_tabs_index(
        self,
        tabs_index: tuple,
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
        pass

    def shimoku_gauge(
        self,
        order: int,
        value: Union[int, float],
        name: str = "",
        color: Union[str, int, None] = 1,
        title: Optional[str] = None,
        rows_size: Optional[int] = 1,
        cols_size: Optional[int] = 3,
        padding: Optional[str] = None,
        is_percentage: bool = False,
        option_modifications: Optional[dict] = None,
    ):
        """Create a pie chart"""
        pass

    def shimoku_gauges_group(
        self,
        gauges_data: Union[DataFrame, list[dict]],
        order: int,
        rows_size: Optional[int] = None,
        cols_size: Optional[int] = 12,
        gauges_padding: Optional[str] = "3, 1, 1, 1",
        gauges_rows_size: Optional[int] = 9,
        gauges_cols_size: Optional[int] = 4,
        calculate_percentages: Optional[bool] = False,
    ):
        """None"""
        pass

    def single_indicator(
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
        pass

    def speed_gauge(
        self,
        order: int,
        name: str,
        value: int,
        min_value: int,
        max_value: int,
        title: Optional[str] = None,
        rows_size: Optional[int] = 2,
        cols_size: Optional[int] = 3,
        padding: Optional[str] = None,
        option_modifications: Optional[dict] = None,
    ):
        """Create a speed gauge chart"""
        pass

    def stacked_area(
        self,
        data: Union[str, DataFrame, list[dict]],
        order: int,
        x: str,
        y: Union[list[str], str, None] = None,
        rows_size: Optional[int] = None,
        cols_size: Optional[int] = None,
        padding: Optional[str] = None,
        title: Optional[str] = None,
        x_axis_name: Optional[str] = None,
        y_axis_name: Optional[str] = None,
        show_values: Union[list[str], str, None] = None,
        option_modifications: Optional[dict] = None,
        variant: Optional[str] = None,
    ):
        """Create a stacked area chart"""
        pass

    def stacked_bar(
        self,
        data: Union[str, DataFrame, list[dict]],
        order: int,
        x: str,
        y: Union[list[str], str, None] = None,
        rows_size: Optional[int] = None,
        cols_size: Optional[int] = None,
        padding: Optional[str] = None,
        title: Optional[str] = None,
        x_axis_name: Optional[str] = None,
        y_axis_name: Optional[str] = None,
        show_values: Union[list[str], str, None] = None,
        option_modifications: Optional[dict] = None,
        variant: Optional[str] = None,
    ):
        """Create a stacked bar chart"""
        pass

    def stacked_horizontal_bar(
        self,
        data: Union[str, DataFrame, list[dict]],
        order: int,
        x: str,
        y: Union[list[str], str, None] = None,
        rows_size: Optional[int] = None,
        cols_size: Optional[int] = None,
        padding: Optional[str] = None,
        title: Optional[str] = None,
        x_axis_name: Optional[str] = None,
        y_axis_name: Optional[str] = None,
        show_values: Union[list[str], str, None] = None,
        option_modifications: Optional[dict] = None,
        variant: Optional[str] = None,
    ):
        """Create a stacked horizontal bar chart"""
        pass

    def sunburst(
        self,
        order: int,
        data: Union[str, dict, list],
        title: Optional[str] = None,
        padding: Optional[str] = None,
        rows_size: Optional[int] = None,
        cols_size: Optional[int] = None,
        option_modifications: Optional[dict] = None,
    ):
        """Create a sunburst chart"""
        pass

    def table(
        self,
        order: int,
        data: Union[str, DataFrame, list[dict], dict],
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
        pass

    def top_bottom_area(
        self,
        data: Union[str, DataFrame, list[dict]],
        order: Optional[int] = None,
        x: str = "x",
        top_names: Optional[list[str]] = None,
        bottom_names: Optional[list[str]] = None,
        rows_size: Optional[int] = None,
        cols_size: Optional[int] = None,
        padding: Optional[str] = None,
        title: Optional[str] = None,
        x_axis_name: Optional[str] = None,
        top_axis_name: Optional[str] = None,
        bottom_axis_name: Optional[str] = None,
        option_modifications: Optional[dict] = None,
        variant: Optional[str] = None,
    ):
        """None"""
        pass

    def top_bottom_line(
        self,
        data: Union[str, DataFrame, list[dict]],
        order: int,
        x: str,
        top_names: Optional[list[str]] = None,
        bottom_names: Optional[list[str]] = None,
        rows_size: int = 4,
        cols_size: Optional[int] = None,
        padding: Optional[str] = None,
        title: Optional[str] = None,
        x_axis_name: Optional[str] = None,
        top_axis_name: Optional[str] = None,
        bottom_axis_name: Optional[str] = None,
        option_modifications: Optional[dict] = None,
    ):
        """None"""
        pass

    def tree(
        self,
        order: int,
        data: Union[str, dict, list[dict]],
        radial: bool = False,
        vertical: bool = False,
        title: Optional[str] = None,
        padding: Optional[str] = None,
        rows_size: Optional[int] = None,
        cols_size: Optional[int] = None,
        option_modifications: Optional[dict] = None,
    ):
        """Create a tree chart"""
        pass

    def treemap(
        self,
        order: int,
        data: Union[dict, list, None] = None,
        title: Optional[str] = None,
        padding: Optional[str] = None,
        rows_size: Optional[int] = None,
        cols_size: Optional[int] = None,
        option_modifications: Optional[dict] = None,
    ):
        """Create a treemap chart"""
        pass

    def waterfall(
        self,
        data: Union[str, DataFrame, list[dict]],
        order: int,
        x: str,
        positive: str,
        negative: str,
        rows_size: Optional[int] = None,
        cols_size: Optional[int] = None,
        padding: Optional[str] = None,
        title: Optional[str] = None,
        x_axis_name: Optional[str] = None,
        y_axis_name: Optional[str] = None,
        show_balance: bool = False,
        variant: Optional[str] = None,
        option_modifications: Optional[dict] = None,
    ):
        """None"""
        pass

    def zero_centered_bar(
        self,
        data: Union[str, DataFrame, list[dict]],
        order: int,
        x: str,
        y: Union[list[str], str, None] = None,
        rows_size: Optional[int] = None,
        cols_size: Optional[int] = None,
        padding: Optional[str] = None,
        title: Optional[str] = None,
        x_axis_name: Optional[str] = None,
        y_axis_name: Optional[str] = None,
        show_values: Union[list[str], str, None] = None,
        option_modifications: Optional[dict] = None,
        variant: Optional[str] = None,
    ):
        """Create a zero centered bar chart"""
        pass
