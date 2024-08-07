from typing import Union, Optional, TYPE_CHECKING

import pandas as pd

from shimoku.exceptions import BentoboxError
from shimoku.plt.utils import create_normalized_name, ShimokuPalette
from shimoku_components_catalog.html_components import create_h1_title_with_modal

if TYPE_CHECKING:
    from shimoku.plt.plt_layer import PlotLayer

import logging
from shimoku.execution_logger import log_error

logger = logging.getLogger(__name__)


def check_for_bentobox(self: "PlotLayer"):
    if self._bentobox_data:
        log_error(
            logger,
            "This function groups a chart and a group of indicators with a bentobox,"
            " so it cannot be used inside another bentobox. Please"
            " pop out of the current bentobox before using this function.",
            BentoboxError,
        )


def _call_inner_chart_function_with_parameters(
    self: "PlotLayer",
    order: int,
    default_rows_size: int,
    default_cols_size: int,
    chart_parameters: dict,
    chart_function: Optional[callable] = None,
) -> any:
    if not chart_parameters or not isinstance(chart_parameters, dict):
        chart_parameters = {}

    restricted_parameters = ["order"]

    for parameter in restricted_parameters:
        if parameter in chart_parameters:
            log_error(
                logger,
                f"Parameter {parameter} cannot be used in the inner chart",
                ValueError,
            )

    chart_parameters.update(
        dict(
            order=order,
            padding="1,0,0,1"
            if "padding" not in chart_parameters
            else chart_parameters["padding"],
            rows_size=default_rows_size
            if "rows_size" not in chart_parameters
            else chart_parameters["rows_size"],
            cols_size=default_cols_size
            if "cols_size" not in chart_parameters
            else chart_parameters["cols_size"],
        )
    )

    if chart_function is None:
        chart_function = self.bar

    return chart_function(**chart_parameters)


def infographics_text_bubble(
    self: "PlotLayer",
    title: str,
    text: str,
    order: int,
    chart_parameters: dict,
    rows_size: int = 3,
    cols_size: int = 12,
    chart_function: Optional[callable] = None,
    background_url: Optional[str] = None,
    background_color: str = ShimokuPalette.BACKGROUND.value,
    bubble_location: str = "top",
    image_url: Optional[str] = None,
    image_size: int = 100,
):
    if bubble_location not in ["top", "bottom", "left", "right"]:
        log_error(logger, f"Invalid location value '{bubble_location}'.", ValueError)

    chart_first = bubble_location in ["bottom", "right"]
    vertical = bubble_location in ["top", "bottom"]

    if image_url and vertical:
        log_error(logger, "The image cannot be displayed vertically.", ValueError)

    default_rows_size = (
        int(10 * rows_size * (2 / 3)) - 2 * int(bubble_location == "bottom")
        if vertical
        else 10 * rows_size
    )
    default_cols_size = 23 if vertical else 15

    if image_url == "default":
        image_url = "https://uploads-ssl.webflow.com/619f9fe98661d321dc3beec7/63332131120af18c03d2b69a_APAME-about.svg"

    check_for_bentobox(self)
    self.set_bentobox(cols_size, rows_size)

    _call_inner_chart_function_with_parameters(
        self=self,
        order=order + int(not chart_first),
        default_rows_size=default_rows_size,
        default_cols_size=default_cols_size,
        chart_function=chart_function,
        chart_parameters=chart_parameters,
    )

    chart_padding = chart_parameters["padding"].replace(" ", "").split(",")
    sides_padding = int(chart_padding[1]) + int(chart_padding[3])
    vertical_padding = int(chart_padding[0]) + int(chart_padding[2])

    html_cols_size = 22 - int(not vertical) * (
        chart_parameters["cols_size"] + sides_padding
    )
    html_rows_size = 10 * rows_size - int(vertical) * (
        chart_parameters["rows_size"] + vertical_padding
    )

    r_hash = create_normalized_name(self._get_component_hash(order))

    html = (
        "<head>"
        f"<style>.block-text-{r_hash}{{padding:24px; "
        f"color: {ShimokuPalette.BLACK.value}; font-size: 16px;"
        + (f"background-color: {background_color}; " if background_url is None else "")
        + f"background-size:cover; background-repeat: no-repeat;background-image: url('{background_url}');"
        "background-position: center; border-radius:var(--border-radius-m);}</style>"
        "</head>"
        f"<div class='block-text-{r_hash}'>"
        + (f"<img src={image_url} width='{image_size}%'>" if image_url else "")
        + f"<h1>{title}</h1>"
        f"<p>{text}</p>"
        "</div>"
    )
    self.html(
        html=html,
        order=order + int(chart_first),
        rows_size=html_rows_size,
        cols_size=html_cols_size,
        padding=f'{int(bubble_location != "bottom")},1,1,1',
    )
    self.pop_out_of_bentobox()


def chart_and_modal_button(
    self: "PlotLayer",
    order: int,
    chart_parameters: dict,
    button_modal: str,
    rows_size: int = 3,
    cols_size: int = 12,
    chart_function: Optional[callable] = None,
    button_label: str = "Read more",
    button_side_text: str = "Click on the button to read more about this topic.",
):
    check_for_bentobox(self)
    self.set_bentobox(cols_size, rows_size)
    _call_inner_chart_function_with_parameters(
        self=self,
        order=order,
        default_rows_size=rows_size * 10 - 6,
        default_cols_size=22,
        chart_function=chart_function,
        chart_parameters=chart_parameters,
    )

    chart_padding = chart_parameters["padding"].replace(" ", "").split(",")
    vertical_padding = int(chart_padding[0]) + int(chart_padding[2])

    button_rows_size = (
        10 * rows_size - chart_parameters["rows_size"] + vertical_padding - 2
    )

    if cols_size > 3:
        html = (
            "<head>"
            f"<style>.rubik-text{{padding: 2%;"
            f"background-color: {ShimokuPalette.STRIPE_LIGHT.value};"
            f"background-size:cover; background-repeat: no-repeat;"
            "background-position: center; border-radius:var(--border-radius-m);"
            f"color: {ShimokuPalette.GRAY.value}; font-size: 16px;}}</style>"
            "</head>"
            "<div class='rubik-text'>"
            f"<p>{button_side_text}</p>"
            "</div>"
        )

        self.html(
            html=html,
            order=order + 1,
            rows_size=button_rows_size,
            cols_size=13 + int(0.5 * (cols_size - 4)),
            padding="0,1,0,1",
        )

    self.modal_button(
        order=order + 2,
        modal=button_modal,
        label=button_label,
        rows_size=button_rows_size,
        cols_size=2,
        padding="0,0,0,1",
    )
    self.pop_out_of_bentobox()


def chart_and_indicators(
    self: "PlotLayer",
    order: int,
    chart_parameters: dict,
    indicators_groups: list[Union[pd.DataFrame, list[dict]]],
    indicators_parameters: Optional[dict] = None,
    chart_rows_size: int = 3,
    cols_size: int = 12,
    chart_function: Optional[callable] = None,
) -> int:
    check_for_bentobox(self)
    if indicators_parameters is None:
        indicators_parameters = {}

    self.set_bentobox(cols_size, chart_rows_size + len(indicators_groups))

    _call_inner_chart_function_with_parameters(
        self=self,
        order=order,
        default_rows_size=chart_rows_size * 14,
        default_cols_size=22,
        chart_function=chart_function,
        chart_parameters=chart_parameters,
    )

    not_allowed_parameters = ["data", "menu_path", "order", "bentobox_data"]
    for parameter in not_allowed_parameters:
        if parameter in indicators_parameters:
            log_error(
                logger,
                f"Parameter {parameter} cannot be used in the inner indicators",
                ValueError,
            )

    indicators_parameters["padding"] = indicators_parameters.get("padding", "0,0,0,1")
    indicators_parameters["rows_size"] = indicators_parameters.get("rows_size", 8)
    indicators_parameters["cols_size"] = indicators_parameters.get("cols_size", 23)

    order += 1
    for indicators_group in indicators_groups:
        order = self.indicator(
            data=indicators_group, order=order, **indicators_parameters
        )

    self.pop_out_of_bentobox()

    return order


def indicators_with_header(
    self: "PlotLayer",
    order: int,
    indicators_groups: list[Union[pd.DataFrame, list[dict]]],
    title: str,
    indicators_parameters: Optional[dict] = None,
    subtitle: str = "",
    background_color: str = ShimokuPalette.PRIMARY.value,
    text_color: str = ShimokuPalette.BACKGROUND_PAPER.value,
    cols_size: int = 12,
    icon_url: str = "https://uploads-ssl.webflow.com/619f9fe98661d321dc3beec7/63e3615716d4435d29e0b82c_Acurracy.svg",
) -> int:
    if indicators_parameters is None:
        indicators_parameters = {}
    return chart_and_indicators(
        self=self,
        order=order,
        chart_rows_size=1,
        cols_size=cols_size,
        chart_function=self.html,
        chart_parameters=dict(
            html=create_h1_title_with_modal(
                title=title,
                subtitle=subtitle,
                background_color=background_color,
                text_color=text_color,
                icon_url=icon_url,
            ),
            padding="0,0,0,0",
            cols_size=24,
        ),
        indicators_groups=indicators_groups,
        indicators_parameters=indicators_parameters,
    )


def line_with_summary(
    self: "PlotLayer",
    order: int,
    data: Union[str, pd.DataFrame, list[dict]],
    title: str,
    x: str,
    y: Optional[Union[str, list[str]]] = None,
    description: str = "",
    value: Union[str, float, int] = "",
    rows_size: int = 2,
    cols_size: int = 2,
):
    check_for_bentobox(self)

    self.set_bentobox(cols_size, rows_size)

    _call_inner_chart_function_with_parameters(
        self=self,
        order=order,
        default_rows_size=(rows_size // 2 + rows_size % 2) * 12,
        default_cols_size=22,
        chart_function=self.area,
        chart_parameters={
            "data": data,
            "x": x,
            "y": y,
            "variant": "minimal",
            "option_modifications": {
                "xAxis": {
                    "axisLabel": {
                        "show": True,
                        "showMaxLabel": True,
                        "showMinLabel": True,
                        "interval": 10000000000000,
                    },
                    "boundaryGap": True,
                },
                "yAxis": {
                    "axisLabel": {"show": False},
                },
                "grid": {"left": "1%", "right": "1%", "top": "1%", "bottom": "11%"},
            },
        },
    )
    self.indicator(
        data={
            "title": title,
            "description": description,
            "value": value,
            "align": "center",
            "color": "var(--color-black)",
        },
        order=order + 1,
        rows_size=(rows_size // 2 + rows_size % 2) * 8,
        cols_size=22,
        padding="0,0,0,1",
    )
    self.pop_out_of_bentobox()


def table_with_header(
    self: "PlotLayer",
    order: int,
    data: Union[str, pd.DataFrame, list[dict]],
    title: str,
    table_parameters: Optional[dict] = None,
    subtitle: str = "",
    rows_size: int = 3,
    cols_size: int = 4,
    modal_title: Optional[str] = None,
    icon_url: str = "https://uploads-ssl.webflow.com/619f9fe98661d321dc3beec7/"
    "63594ccf3f311a98d72faff7_suite-customer-b.svg",
    modal_text: str = "You can click the X in the corner or click the overlay to close this modal. "
    "This is a nice way to show additional information.",
    text_color: str = ShimokuPalette.BACKGROUND_PAPER.value,
    background_color: str = ShimokuPalette.BLACK.value,
    modal_icon_color: str = ShimokuPalette.CHART_C1.value,
    modal_icon_hover_color: str = ShimokuPalette.PRIMARY_DARK.value,
):
    check_for_bentobox(self)
    self.set_bentobox(cols_size=cols_size, rows_size=rows_size)
    self.html(
        html=create_h1_title_with_modal(
            title=title,
            subtitle=subtitle,
            background_color=background_color,
            text_color=text_color,
            icon_url=icon_url,
            modal_title=modal_title,
            modal_text=modal_text,
            modal_icon_color=modal_icon_color,
            modal_icon_hover_color=modal_icon_hover_color,
        ),
        order=order,
        cols_size=24,
        rows_size=1,
        padding="0,0,0,0",
    )

    if table_parameters is None:
        table_parameters = {}
    table_parameters["data"] = data
    table_parameters["padding"] = table_parameters.get("padding", "0,0,0,1")

    _call_inner_chart_function_with_parameters(
        self=self,
        order=order + 1,
        default_rows_size=rows_size,
        default_cols_size=22,
        chart_function=self.table,
        chart_parameters=table_parameters,
    )
    self.pop_out_of_bentobox()
