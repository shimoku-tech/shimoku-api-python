from shimoku import Client
from .data.flow_and_rainfall import flow, rainfall, time


def rainfall_line(shimoku_client: Client):
    shimoku_client.set_menu_path("test-free-echarts", "rainfall-line")
    how_many = 100

    data = []
    for i in range(0, len(flow), max(3, len(flow) // how_many)):
        data.append(
            {
                "Date": time[i],
                "flow": flow[i],
                "flow+1": flow[(i + 101) % len(flow)],
                "flow+2": flow[(i + 202) % len(flow)],
                "rainfall": rainfall[i],
                "rainfall+1": rainfall[(i + 101) % len(flow)],
                "rainfall+2": rainfall[(i + 202) % len(flow)],
            }
        )

    shimoku_client.plt.top_bottom_line(
        data=data,
        order=0,
        x="Date",
        top_names=["flow", "flow+1", "flow+2"],
        bottom_names=["rainfall", "rainfall+1", "rainfall+2"],
        title="rainfall and flow",
        x_axis_name="Date",
        top_axis_name="flow(m³/s)",
        bottom_axis_name="rainfall(mm)",
    )

    data = []
    for i in range(0, len(flow), max(1, len(flow) // how_many)):
        data.append({"Date": time[i], "flow": flow[i], "rainfall": rainfall[i]})

    shimoku_client.plt.top_bottom_line(
        data=data,
        order=1,
        x="Date",
        top_names=["flow"],
        bottom_names=["rainfall"],
        title="rainfall and flow",
        x_axis_name="Date",
        top_axis_name="flow(m³/s)",
        bottom_axis_name="rainfall(mm)",
    )
