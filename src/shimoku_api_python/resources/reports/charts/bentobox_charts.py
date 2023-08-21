from typing import List, Callable, Dict, Any, Union, Optional, Tuple, TYPE_CHECKING

import logging

import pandas as pd

if TYPE_CHECKING:
    from shimoku_api_python.api.plot_api import PlotApi
from shimoku_api_python.exceptions import BentoboxError
from shimoku_api_python.utils import create_normalized_name
from shimoku_components_catalog.html_components import create_h1_title_with_modal

from ....execution_logger import logging_before_and_after, log_error
logger = logging.getLogger(__name__)


@logging_before_and_after(logging_level=logger.debug)
def _call_inner_chart_function_with_parameters(
    self: 'PlotApi', order: int, default_rows_size: int, default_cols_size: int,
    chart_parameters: Dict, chart_function: Optional[Callable] = None,
) -> Any:
    if not chart_parameters or not isinstance(chart_parameters, Dict):
        chart_parameters = {}

    restricted_parameters = ['order']

    for parameter in restricted_parameters:
        if parameter in chart_parameters:
            log_error(logger, f'Parameter {parameter} cannot be used in the inner chart', ValueError)

    chart_parameters.update(dict(
        order=order,
        padding='1,0,0,1' if 'padding' not in chart_parameters else chart_parameters['padding'],
        rows_size=default_rows_size if 'rows_size' not in chart_parameters else chart_parameters['rows_size'],
        cols_size=default_cols_size if 'cols_size' not in chart_parameters else chart_parameters['cols_size'],
    ))

    if chart_function is None:
        chart_function = self.bar

    return chart_function(**chart_parameters)


@logging_before_and_after(logging_level=logger.info)
def infographics_text_bubble(
    self: 'PlotApi', title: str, text: str, order: int, chart_parameters: Dict,
    rows_size: int = 3, cols_size: int = 12, chart_function: Optional[Callable] = None,
    background_url: Optional[str] = None, background_color: str = 'var(--background-default)',
    bubble_location: str = 'top', image_url: Optional[str] = None, image_size: int = 100,
):
    if bubble_location not in ['top', 'bottom', 'left', 'right']:
        log_error(logger, f"Invalid location value '{bubble_location}'.", ValueError)

    chart_first = bubble_location in ['bottom', 'right']
    vertical = bubble_location in ['top', 'bottom']

    if image_url and vertical:
        log_error(logger, "The image cannot be displayed vertically.", ValueError)

    default_rows_size = int(10 * rows_size * (2 / 3))-2*int(bubble_location == 'bottom') if vertical else 10 * rows_size
    default_cols_size = 23 if vertical else 15

    if image_url == 'default':
        image_url = 'https://uploads-ssl.webflow.com/619f9fe98661d321dc3beec7/63332131120af18c03d2b69a_APAME-about.svg'

    bentobox_data = {
        'bentoboxId': f'_{order}',
        'bentoboxOrder': order,
        'bentoboxSizeColumns': cols_size,
        'bentoboxSizeRows': rows_size,
    }

    if self._bentobox_data:
        log_error(logger, 'This function groups a chart and a text bubble with a bentobox,'
                          ' so it cannot be used inside another bentobox. Please'
                          ' pop out of the current bentobox before using this function.', BentoboxError)
    self._bentobox_data = bentobox_data

    _call_inner_chart_function_with_parameters(
        self=self, order=order+int(not chart_first),
        default_rows_size=default_rows_size, default_cols_size=default_cols_size,
        chart_function=chart_function, chart_parameters=chart_parameters
    )

    chart_padding = chart_parameters['padding'].replace(' ', '').split(',')
    sides_padding = int(chart_padding[1]) + int(chart_padding[3])
    vertical_padding = int(chart_padding[0]) + int(chart_padding[2])

    html_cols_size = 22 - int(not vertical)*(chart_parameters['cols_size'] + sides_padding)
    html_rows_size = 10 * rows_size - int(vertical)*(chart_parameters['rows_size'] + vertical_padding)

    r_hash = create_normalized_name(self._get_chart_hash(order))

    html = (
        "<head>"
        f"<style>.block-text-{r_hash}{{padding:24px; "
        "color: var(--color-black); font-size: 16px;" +
        (f"background-color: {background_color}; " if background_url is None else "") +
        f"background-size:cover; background-repeat: no-repeat;background-image: url('{background_url}');"
        "background-position: center; border-radius:var(--border-radius-m);}</style>"
        "</head>" 
        f"<div class='block-text-{r_hash}'>" +
        (f"<img src={image_url} width='{image_size}%'>"
         if image_url else "") +
        f"<h1>{title}</h1>"
        f"<p>{text}</p>"
        "</div>"
    )

    self.html(
        html=html,
        order=order+int(chart_first),
        rows_size=html_rows_size,
        cols_size=html_cols_size,
        padding=f'{int(bubble_location != "bottom")},1,1,1'
    )

    self._bentobox_data = {}


@logging_before_and_after(logging_level=logger.info)
def chart_and_modal_button(
    self: 'PlotApi', order: int, chart_parameters: Dict, button_modal: str, rows_size: int = 3,
    cols_size: int = 12, chart_function: Optional[Callable] = None, button_label: str = 'Read more',
    button_side_text: str = "Click on the button to read more about this topic.",
):
    bentobox_data = {
        'bentoboxId': f'_{order}',
        'bentoboxOrder': order,
        'bentoboxSizeColumns': cols_size,
        'bentoboxSizeRows': rows_size,
    }

    if self._bentobox_data:
        log_error(logger, 'This function groups a chart and a button with a bentobox,'
                          ' so it cannot be used inside another bentobox. Please'
                          ' pop out of the current bentobox before using this function.', BentoboxError)
    self._bentobox_data = bentobox_data

    _call_inner_chart_function_with_parameters(
        self=self, order=order, default_rows_size=rows_size*10-6, default_cols_size=22,
        chart_function=chart_function, chart_parameters=chart_parameters
    )

    chart_padding = chart_parameters['padding'].replace(' ', '').split(',')
    vertical_padding = int(chart_padding[0]) + int(chart_padding[2])

    button_rows_size = 10 * rows_size - chart_parameters['rows_size'] + vertical_padding - 2

    if cols_size > 3:
        html = (
            "<head>"
            f"<style>.rubik-text{{padding: 2%;"      
            f"background-color: var(--color-stripe-light);"
            f"background-size:cover; background-repeat: no-repeat;"
            "background-position: center; border-radius:var(--border-radius-m);"
            "color: var(--color-gray); font-size: 16px;}</style>"
            "</head>"
            "<div class='rubik-text'>"
            f"<p>{button_side_text}</p>"
            "</div>"
        )

        self.html(
            html=html,
            order=order + 1,
            rows_size=button_rows_size,
            cols_size=13 + int(0.5*(cols_size-4)),
            padding='0,1,0,1'
        )

    self.modal_button(
        order=order + 2, modal=button_modal, label=button_label,
        rows_size=button_rows_size, cols_size=2, padding='0,0,0,1',
    )

    self._bentobox_data = {}

# Wait until the new iteration of the bentobox is ready

# @logging_before_and_after(logging_level=logger.info)
# def indicator_and_modal_button(
#     self, menu_path: str, order: int, indicator_parameters: Dict, button_modal: str, rows_size: int = 1,
#     cols_size: int = 3, button_label: str = 'Read more', tabs_index: Optional[Tuple[str, str]] = None,
#     modal_name: Optional[str] = None,
# ) -> int:
#
#     bentobox_data = {
#         'bentoboxId': str(uuid1()),
#         'bentoboxOrder': order,
#         'bentoboxSizeColumns': cols_size,
#         'bentoboxSizeRows': rows_size,
#     }
#
#     vertical = indicator_parameters.get('vertical')
#
#     len_df = 1
#
#     if isinstance(indicator_parameters['data'], list):
#         len_df = len(indicator_parameters['data'])
#
#     default_rows_size = max(rows_size//len_df, 1) if vertical else 8*rows_size-2*int(rows_size == 1)
#
#     indicator_parameters['padding'] = indicator_parameters.get('padding', '1,1,1,1')
#
#     returned_order = _call_inner_chart_function_with_parameters(
#         self=self, menu_path=menu_path, order=order,
#         default_rows_size=default_rows_size, default_cols_size=22,
#         bentobox_data=bentobox_data, tabs_index=tabs_index, modal_name=modal_name,
#         chart_function=self.indicator, chart_parameters=indicator_parameters
#     )
#
#     chart_padding = indicator_parameters['padding'].replace(' ', '').split(',')
#     vertical_padding = int(chart_padding[0]) + int(chart_padding[2])
#
#     button_rows_size = 2
#     if not vertical:
#         button_rows_size = 10 * rows_size - (indicator_parameters['rows_size'] + vertical_padding)
#
#     print(button_rows_size)
#     self.modal_button(
#         menu_path=menu_path, order=returned_order, modal_name_to_open=button_modal, label=button_label,
#         bentobox_data=bentobox_data, rows_size=button_rows_size, cols_size=23,
#         tabs_index=tabs_index, modal_name=modal_name, align='right'
#     )
#
#     return returned_order + 1


@logging_before_and_after(logging_level=logger.info)
def chart_and_indicators(
    self: 'PlotApi', order: int, chart_parameters: Dict,
    indicators_groups: List[Union[pd.DataFrame, List[Dict]]], indicators_parameters: Dict,
    chart_rows_size: int = 3, cols_size: int = 12,
    chart_function: Optional[Callable] = None,
) -> int:

    bentobox_data = {
        'bentoboxId': f'_{order}',
        'bentoboxOrder': order,
        'bentoboxSizeColumns': cols_size,
        'bentoboxSizeRows': chart_rows_size+len(indicators_groups),
    }

    if self._bentobox_data:
        log_error(logger, 'This function groups a chart and a group of indicators with a bentobox,'
                          ' so it cannot be used inside another bentobox. Please'
                          ' pop out of the current bentobox before using this function.', BentoboxError)
    self._bentobox_data = bentobox_data

    _call_inner_chart_function_with_parameters(
        self=self, order=order, default_rows_size=chart_rows_size*14, default_cols_size=22,
        chart_function=chart_function, chart_parameters=chart_parameters
    )

    not_allowed_parameters = ['data', 'menu_path', 'order', 'bentobox_data']
    for parameter in not_allowed_parameters:
        if parameter in indicators_parameters:
            log_error(logger, f'Parameter {parameter} cannot be used in the inner indicators', ValueError)

    indicators_parameters['padding'] = indicators_parameters.get('padding', '0,0,0,1')
    indicators_parameters['rows_size'] = indicators_parameters.get('rows_size', 8)
    indicators_parameters['cols_size'] = indicators_parameters.get('cols_size', 23)

    order += 1
    for indicators_group in indicators_groups:
        order = self.indicator(
            data=indicators_group,
            order=order,
            **indicators_parameters
        )

    self._bentobox_data = {}
    return order


@logging_before_and_after(logging_level=logger.info)
def indicators_with_header(
    self, order: int, indicators_groups: List[Union[pd.DataFrame, List[Dict]]],
    indicators_parameters: Dict, title: str, subtitle: str = '', background_color: str = 'var(--color-primary)',
    text_color: str = 'var(--background-paper)', cols_size: int = 12,
    icon_url: str = 'https://uploads-ssl.webflow.com/619f9fe98661d321dc3beec7/63e3615716d4435d29e0b82c_Acurracy.svg',
) -> int:
    return chart_and_indicators(
        self=self, order=order,
        chart_rows_size=1, cols_size=cols_size,
        chart_function=self.html,
        chart_parameters=dict(
            html=create_h1_title_with_modal(
                title=title, subtitle=subtitle, background_color=background_color,
                text_color=text_color, icon_url=icon_url
            ),
            padding='0,0,0,0',
            cols_size=24,
        ),
        indicators_groups=indicators_groups,
        indicators_parameters=indicators_parameters
    )
