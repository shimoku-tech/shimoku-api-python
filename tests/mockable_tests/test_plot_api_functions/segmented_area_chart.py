from shimoku import Client


def segmented_area_chart(shimoku_client: Client):
    shimoku_client.set_menu_path("test-free-echarts", "Segmented Area Chart")
    labels = [
        "A",
        "B",
        "C",
        "D",
        "E",
        "F",
        "G",
        "H",
        "I",
        "J",
        "K",
        "L",
        "M",
        "N",
        "O",
        "P",
        "Q",
        "R",
        "S",
        "T",
        "U",
        "V",
        "W",
        "X",
        "Y",
        "Z",
    ]
    shimoku_client.plt.segmented_area(
        data="noise",
        order=1,
        x="x",
        y="y",
        threshold=0.7,
        top_area=True,
        default_color=(0, 0, 255),
        labels=labels,
    )
    shimoku_client.plt.segmented_area(
        data="noise", order=2, x="x", y="y", threshold=0.7, labels=labels
    )
    shimoku_client.plt.segmented_area(
        data="noise",
        order=3,
        x="x",
        y="y",
        segments=[(30, 45), (60, 70, "var(--chart-C1)"), (75, 95, (1, 220, 1))],
    )
