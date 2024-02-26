from typing import Optional, TYPE_CHECKING

from pandas import DataFrame

from shimoku.plt.EChart_definitions.default_echart_options import (
    get_common_echart_options,
    get_common_series_options,
)

if TYPE_CHECKING:
    from shimoku.plt.plt_layer import PlotLayer


async def sankey_chart(
    self: "PlotLayer",
    order: int,
    sources: str,
    targets: str,
    values: str,
    data: list[dict],
    option_modifications: Optional[dict] = None,
    title: Optional[str] = None,
    padding: Optional[str] = None,
    rows_size: Optional[int] = None,
    cols_size: Optional[int] = None,
):
    """Create a sankey chart"""
    df = DataFrame(data)
    common_options = get_common_echart_options()
    series_options = get_common_series_options()
    del common_options["xAxis"]
    del common_options["yAxis"]
    del common_options["toolbox"]["feature"]["magicType"]
    del common_options["grid"]
    names = df[sources].to_list() + df[targets].to_list()
    series_options.update(
        {
            "type": "sankey",
            "layout": "none",
            "emphasis": {
                "focus": "adjacency",
            },
            "data": [
                {"name": name} for i, name in enumerate(names) if name not in names[:i]
            ],
            "links": "#set_data#",
        }
    )
    common_options["series"] = [series_options]
    await self._create_echart(
        data_mapping_to_tuples=await self._choose_data(order, data),
        fields=[{"source": sources, "target": targets, "value": values}],
        options=common_options,
        order=order,
        title=title,
        option_modifications=option_modifications,
        rows_size=rows_size,
        cols_size=cols_size,
        padding=padding,
    )
