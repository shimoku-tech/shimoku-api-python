from typing import Optional, Union, TYPE_CHECKING

from shimoku.plt.EChart_definitions.default_echart_options import get_common_echart_options, get_common_series_options

if TYPE_CHECKING:
    from shimoku.plt.plt_layer import PlotLayer


async def sunburst_chart(
    self: 'PlotLayer', order: int, data: Union[str, dict, list],
    title: Optional[str] = None, padding: Optional[str] = None,
    rows_size: Optional[int] = None, cols_size: Optional[int] = None,
    option_modifications: Optional[dict] = None,
):
    """ Create a sunburst chart """
    common_options = get_common_echart_options()
    series_options = get_common_series_options()
    del common_options['xAxis']
    del common_options['yAxis']
    del common_options['toolbox']['feature']['magicType']
    if isinstance(data, dict):
        data = [data]
    series_options.update({
        'type': 'sunburst',
        'data': '#set_data#',
        'radius': [0, '95%'],
        'label': {
            'rotate': 'radial',
        }
    })
    common_options.update({
        'tooltip': {
            'trigger': 'item',
            'triggerOn': 'mousemove'
        },
        'series': series_options
    })
    await self._create_echart(
        data_mapping_to_tuples=await self._choose_data(order, data, dump_whole=True),
        fields=['data'], options=common_options, order=order, title=title,
        rows_size=rows_size, cols_size=cols_size, padding=padding,
        option_modifications=option_modifications
    )
