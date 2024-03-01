from shimoku import Client
from .data.default import data


def infographics(shimoku_client: Client):
    shimoku_client.set_menu_path("test-bentobox", "Infographics")
    title = "Lorem ipsum"
    text = (
        "Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et "
        "dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip"
        "ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu"
        " fugiat nulla pariatur. "
    )

    shimoku_client.plt.infographics_text_bubble(
        order=0,
        cols_size=6,
        title=title,
        text=text,
        bubble_location="bottom",
        chart_parameters=dict(
            data=data,
            x="date",
            rows_size=16,
            option_modifications=dict(
                toolbox={"show": False},
                grid={
                    "left": "0%",
                    "right": "0%",
                    "top": "0%",
                    "bottom": "0%",
                    "containLabel": True,
                },
            ),
        ),
    )

    shimoku_client.plt.infographics_text_bubble(
        order=2,
        cols_size=6,
        title=title,
        text=text,
        chart_function=shimoku_client.plt.line,
        chart_parameters=dict(
            x="date",
            y="x",
            data=data,
            option_modifications=dict(
                toolbox={"show": False},
                grid={
                    "left": "0%",
                    "right": "0%",
                    "top": "0%",
                    "bottom": "0%",
                    "containLabel": True,
                },
            ),
        ),
    )

    shimoku_client.plt.infographics_text_bubble(
        order=4,
        cols_size=6,
        title=title,
        text=text,
        chart_function=shimoku_client.plt.shimoku_gauge,
        chart_parameters=dict(value=70, name="Gauge", rows_size=18, padding="0,0,0,0"),
    )
    stacked_data = [
        {
            "Weekday": "Mon",
            "Email": 120,
            "Union Ads": 132,
            "Video Ads": 101,
            "Search Engine": 134,
        },
        {
            "Weekday": "Tue",
            "Email": 220,
            "Union Ads": 182,
            "Video Ads": 191,
            "Search Engine": 234,
        },
        {
            "Weekday": "Wed",
            "Email": 150,
            "Union Ads": 232,
            "Video Ads": 201,
            "Search Engine": 154,
        },
        {
            "Weekday": "Thu",
            "Email": 820,
            "Union Ads": 932,
            "Video Ads": 901,
            "Search Engine": 934,
        },
        {
            "Weekday": "Fri",
            "Email": 120,
            "Union Ads": 132,
            "Video Ads": 101,
            "Search Engine": 134,
        },
        {
            "Weekday": "Sat",
            "Email": 220,
            "Union Ads": 182,
            "Video Ads": 191,
            "Search Engine": 234,
        },
        {
            "Weekday": "Sun",
            "Email": 150,
            "Union Ads": 232,
            "Video Ads": 201,
            "Search Engine": 154,
        },
    ]
    shimoku_client.plt.infographics_text_bubble(
        order=6,
        cols_size=6,
        rows_size=4,
        title=title,
        text=text,
        bubble_location="bottom",
        chart_function=shimoku_client.plt.stacked_bar,
        chart_parameters=dict(
            data=stacked_data,
            x="Weekday",
            x_axis_name="weekday",
            y_axis_name="visits",
            option_modifications=dict(
                toolbox={"show": False},
                grid={
                    "left": "0%",
                    "right": "0%",
                    "top": "0%",
                    "bottom": "0%",
                    "containLabel": True,
                },
            ),
        ),
        background_color="var(--color-stripe-light)",
    )

    shimoku_client.plt.infographics_text_bubble(
        order=8,
        title=title,
        text=text,
        bubble_location="right",
        chart_parameters=dict(
            data=data,
            x="date",
            option_modifications=dict(
                toolbox={"show": False},
                grid={
                    "left": "0%",
                    "right": "0%",
                    "top": "0%",
                    "bottom": "0%",
                    "containLabel": True,
                },
            ),
        ),
        background_url="https://images.unsplash.com/photo-1569982175971-d92b01cf8694?ixlib=rb-4.0.3&ixid="
        "MnwxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8&auto=format&fit=crop&w=870&q=80",
    )

    form_groups = {
        "Personal information": [
            {
                "mapping": "name",
                "fieldName": "name",
                "inputType": "text",
            },
        ],
        "Other group": [
            {
                "mapping": "skills",
                "fieldName": "Skills",
                "options": ["Backend", "Frontend", "UX/UI", "Api Builder", "DevOps"],
                "inputType": "checkbox",
            },
        ],
    }

    shimoku_client.plt.infographics_text_bubble(
        order=10,
        cols_size=8,
        title=title,
        text=text,
        bubble_location="left",
        chart_function=shimoku_client.plt.generate_input_form_groups,
        chart_parameters=dict(
            form_groups=form_groups,
            dynamic_sequential_show=True,
            padding="5,1,0,0",
        ),
        background_color="var(--color-primary-light)",
    )

    shimoku_client.plt.infographics_text_bubble(
        order=12,
        cols_size=4,
        title=title,
        text=text,
        bubble_location="left",
        chart_function=shimoku_client.plt.shimoku_gauge,
        chart_parameters=dict(
            value=49,
            name="Gauge",
            padding="5,1,0,0",
            cols_size=10,
            color=3,
        ),
    )
    shimoku_client.plt.infographics_text_bubble(
        order=14,
        cols_size=6,
        title=title,
        text=text,
        bubble_location="left",
        image_url="default",
        image_size=60,
        background_color="var(--color-primary-light)",
        chart_parameters=dict(
            data=data,
            x="date",
            cols_size=10,
            option_modifications=dict(
                toolbox={"show": False},
                grid={
                    "left": "0%",
                    "right": "0%",
                    "top": "0%",
                    "bottom": "0%",
                    "containLabel": True,
                },
            ),
        ),
    )
    shimoku_client.plt.infographics_text_bubble(
        order=16,
        cols_size=6,
        rows_size=4,
        title=title,
        text=text,
        bubble_location="right",
        image_url="default",
        chart_function=shimoku_client.plt.table,
        chart_parameters=dict(
            data=data,
            rows_size=3,
            cols_size=10,
        ),
    )

    shimoku_client.plt.infographics_text_bubble(
        order=18,
        title=title,
        text=text,
        bubble_location="right",
        image_url="default",
        image_size=50,
        chart_function=shimoku_client.plt.table,
        chart_parameters=dict(
            data=stacked_data,
            cols_size=16,
            rows_size=3,
        ),
    )
