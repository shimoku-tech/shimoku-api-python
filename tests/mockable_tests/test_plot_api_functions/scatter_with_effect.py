from shimoku import Client
from .data.scatter_with_effect import scatter_source, effect_points


def scatter_with_effect(shimoku_client: Client):
    shimoku_client.set_menu_path("test-free-echarts", "scatter-with-effect-test")

    shimoku_client.plt.scatter_with_effect(
        data=scatter_source,
        x="x",
        y="y",
        order=0,
        x_axis_name="X axis",
        y_axis_name="Y axis",
        title="Scatter with effect",
        effect_points=effect_points,
    )
