from shimoku import Client
from .data.annotation_chart import annotated_data, annotated_data_1, annotated_data_2


def annotation_chart(shimoku_client: Client):
    shimoku_client.set_menu_path("test", "Annotation Chart")

    shimoku_client.plt.annotated_chart(data=[annotated_data], x="date", y="x", order=0)

    shimoku_client.plt.annotated_chart(
        order=7,
        x="date",
        y=["Síntoma [1]", "Síntoma [2]"],
        annotations="Annotation",
        data=[annotated_data_1, annotated_data_2],
        slider_config={"max": 100, "defaultValue": 50},
        slider_marks=[("Low", 15), ("Medium", 50), ("High", 85)],
    )
