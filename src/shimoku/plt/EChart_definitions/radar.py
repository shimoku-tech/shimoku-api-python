from typing import Optional, Union, TYPE_CHECKING

from pandas import DataFrame

from shimoku.plt.EChart_definitions.default_echart_options import (
    get_common_echart_options,
    get_common_series_options,
)

if TYPE_CHECKING:
    from shimoku.plt.plt_layer import PlotLayer


async def radar_chart(
    self: "PlotLayer",
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
    common_options = get_common_echart_options()
    series_options = get_common_series_options()
    series_options["type"] = "radar"
    del common_options["yAxis"]
    del common_options["xAxis"]
    del common_options["grid"]
    del common_options["toolbox"]["feature"]["magicType"]
    common_options["radar"] = {"indicator": "#set_data#"}
    if fill_area:
        series_options["areaStyle"] = {"opacity": 0.25}

    data_mapping_to_tuples = await self._choose_data(order, data)
    if not values:
        values = [
            f for f in data_mapping_to_tuples.keys() if f != names and f != max_field
        ]

    series_options["data"] = [{"value": "#set_data#", "name": vf} for vf in values]
    common_options["series"] = [series_options]
    indicator_fields = (
        {"name": names} if not max_field else {"name": names, "max": max_field}
    )
    await self._create_echart(
        fields=[indicator_fields, *values],
        options=common_options,
        data_mapping_to_tuples=data_mapping_to_tuples,
        option_modifications=option_modifications,
        order=order,
        title=title,
        rows_size=rows_size,
        cols_size=cols_size,
        padding=padding,
    )
