from shimoku import Client
from .data.default import data


def chart_and_indicators(shimoku_client: Client):
    shimoku_client.set_menu_path("test-bentobox", "chart-and-indicators")
    indicator_groups = [
        [
            {
                "description": "-950.55",
                "title": "Dow Jones",
                "value": "33,195.92",
                "align": "left",
                "color": "success",
                "variant": "contained",
            },
            {
                "description": "-84.68",
                "title": "Nasdaq",
                "value": "10,852.16",
                "align": "left",
                "color": "success",
                "variant": "contained",
            },
            {
                "description": "-950.55",
                "title": "Dow Jones",
                "value": "33,195.92",
                "align": "left",
                "color": "success",
                "variant": "contained",
            },
            {
                "description": "-84.68",
                "title": "Nasdaq",
                "value": "10,852.16",
                "align": "left",
                "color": "success",
                "variant": "contained",
            },
            {
                "description": "-950.55",
                "title": "Dow Jones",
                "value": "33,195.92",
                "align": "left",
                "color": "success",
                "variant": "contained",
            },
        ],
        [
            {
                "description": "-950.55",
                "title": "Dow Jones",
                "value": "33,195.92",
                "align": "left",
                "color": "success",
                "variant": "contained",
            },
            {
                "description": "-84.68",
                "title": "Nasdaq",
                "value": "10,852.16",
                "align": "left",
                "color": "success",
                "variant": "contained",
            },
        ],
        [
            {
                "description": "Return of investment",
                "title": "ROI",
                "value": "1.5M",
                "align": "left",
                "color": "success",
                "variant": "contained",
            },
            {
                "description": "% of times the algorithm has predicted the relative position of "
                "NY prices with respect to HK prices correctly",
                "title": "Accuracy",
                "value": "76.67%",
                "align": "left",
                "color": "success",
                "variant": "contained",
            },
        ],
        [
            {
                "description": "Return of investment",
                "title": "ROI",
                "value": "1.5M",
                "align": "left",
                "color": "success",
                "variant": "contained",
            },
            {
                "description": "% of times the algorithm has predicted the relative position of "
                "NY prices with respect to HK prices correctly",
                "title": "Accuracy",
                "value": "76.67%",
                "align": "left",
                "color": "success",
                "variant": "contained",
            },
            {
                "description": "% of times the algorithm has predicted the relative position of "
                "NY prices with respect to HK prices correctly",
                "title": "Accuracy",
                "value": "76.67%",
                "align": "left",
                "color": "success",
                "variant": "contained",
            },
        ],
    ]

    shimoku_client.plt.chart_and_indicators(
        order=0,
        chart_rows_size=3,
        cols_size=6,
        chart_function=shimoku_client.plt.line,
        chart_parameters=dict(
            data=data,
            x="date",
            y="x",
            title="Line Chart With Indicators",
        ),
        indicators_groups=indicator_groups,
        indicators_parameters={},
    )
