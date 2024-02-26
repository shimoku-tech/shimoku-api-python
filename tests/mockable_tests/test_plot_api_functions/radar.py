from shimoku import Client
from copy import deepcopy
from .data.radar import radar_data


def radar(shimoku_client: Client):
    shimoku_client.set_menu_path("test", "radar-test")

    shimoku_client.plt.radar(
        data=radar_data, names="name", order=1, rows_size=2, cols_size=6
    )

    aux_radar_data = deepcopy(radar_data)
    aux_radar_data[0]["max"] = 90
    aux_radar_data[1]["max"] = 70
    aux_radar_data[2]["max"] = 70
    aux_radar_data[3]["max"] = 80

    shimoku_client.plt.radar(
        data=aux_radar_data,
        names="name",
        order=2,
        rows_size=2,
        cols_size=12,
        max_field="max",
        fill_area=True,
    )
