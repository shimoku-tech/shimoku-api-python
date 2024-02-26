from typing import Optional, Union, TYPE_CHECKING

from shimoku.exceptions import BentoboxError
from shimoku.plt.utils import interpret_color, ShimokuPalette

if TYPE_CHECKING:
    from shimoku.plt.plt_layer import PlotLayer

import logging
from shimoku.execution_logger import log_error

logger = logging.getLogger(__name__)


def gauge_indicator(
    self: "PlotLayer",
    order: int,
    value: int,
    title: Optional[str] = "",
    description: Optional[str] = "",
    cols_size: Optional[int] = 6,
    rows_size: Optional[int] = 1,
    color: Union[str, int] = 1,
):
    """Create a gauge indicator"""
    bentobox_data = {
        "bentoboxId": f"_{order}",
        "bentoboxOrder": order,
        "bentoboxSizeColumns": cols_size,
        "bentoboxSizeRows": rows_size,
    }

    if self._bentobox_data:
        log_error(
            logger,
            "The gauges group uses a bentobox, so it cannot be used inside another bentobox. Please"
            " pop out of the current bentobox before using this function.",
            BentoboxError,
        )
    self._bentobox_data = bentobox_data

    indicator_data = [
        {
            "description": description,
            "title": title,
            "value": "",
            "color": "",
            "align": "left",
        }
    ]

    self.indicator(
        data=indicator_data,
        order=order,
        rows_size=8,
        cols_size=15,
        padding="1, 1, 0, 1",
    )

    color = interpret_color(color)

    options = {
        "grid": {
            "left": ["5%"],
            "right": ["5%"],
            "top": ["5%"],
            "bottom": ["5%"],
            "containLabel": True,
        },
        "series": [
            {
                "data": "#set_data#",
                "type": "gauge",
                "startAngle": 360,
                "endAngle": 0,
                "radius": "80%",
                "center": ["50%", "40%"],
                "min": 0,
                "max": 100,
                "pointer": {
                    "show": False,
                },
                "progress": {
                    "show": True,
                    "width": 20,
                    "overlap": False,
                    "roundCap": False,
                    "clip": False,
                    "itemStyle": {
                        "borderWidth": 0,
                        "color": color,
                    },
                },
                "splitLine": {
                    "show": False,
                },
                "axisLine": {"lineStyle": {"width": 20}},
                "axisTick": {"show": False},
                "axisLabel": {
                    "show": False,
                },
                "title": {
                    "show": False,
                    "fontSize": 16,
                    "fontFamily": "Rubik",
                },
                "detail": {
                    "fontSize": 24,
                    "fontFamily": "Rubik",
                    "font": "inherit",
                    "color": ShimokuPalette.BLACK.value,
                    "borderColor": "auto",
                    "borderWidth": 0,
                    "formatter": "{value}%",
                    "valueAnimation": True,
                    "offsetCenter": ["0", "60"],
                },
            }
        ],
    }

    self.free_echarts(
        data=[{"value": value}],
        fields=[{"value": "value"}],
        options=options,
        order=order + 1,
        rows_size=6,
        cols_size=7,
        padding="1, 0, 1, 0",
    )

    self.pop_out_of_bentobox()
