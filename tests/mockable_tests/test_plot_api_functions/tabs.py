from shimoku import Client
from .data.default import data
from .data.table import table_data
from .data.input_form import input_form_data


def tabs(shimoku_client: Client):
    shimoku_client.set_menu_path("test-tabs")
    # s.plt.clear_menu_path()
    shimoku_client.plt.set_shared_data(dfs={"main data": data})

    def _test_bentobox():
        shimoku_client.plt.set_bentobox(cols_size=8, rows_size=3)
        data_indic = [
            {
                "description": "",
                "title": "Estado",
                "value": "Abierto",
            },
        ]
        shimoku_client.plt.indicator(
            data=data_indic,
            order=0,
            rows_size=10,
            cols_size=12,
        )

        shimoku_client.plt.indicator(
            data=data_indic,
            order=1,
            rows_size=10,
            cols_size=12,
        )

        shimoku_client.plt.bar(
            data="main data",
            x="date",
            order=2,
            rows_size=26,
            cols_size=24,
        )
        shimoku_client.plt.pop_out_of_bentobox()

    shimoku_client.plt.set_tabs_index(tabs_index=("Deepness 0", "Bento box"), order=0)
    _test_bentobox()

    shimoku_client.plt.change_current_tab("Table")
    shimoku_client.plt.table(
        title="Test-table",
        data=table_data,
        order=0,
        categorical_columns=["filtA", "filtB"],
        initial_sort_column="date",
        search=True,
    )

    shimoku_client.plt.change_current_tab("line test")
    shimoku_client.plt.line(data="main data", x="date", order=0)

    shimoku_client.plt.change_current_tab("Bar 1")
    shimoku_client.plt.bar(
        data="main data",
        x="date",
        x_axis_name="Date",
        y_axis_name="Revenue",
        order=0,
        rows_size=2,
        cols_size=12,
    )

    shimoku_client.plt.change_current_tab("Input Form")
    shimoku_client.plt.input_form(order=0, options=input_form_data)

    indicators_data = {
        "description": "",
        "title": "",
        "value": "INDICATOR CHANGED!",
        "color": "warning",
    }
    indicators_data_2 = {
        "description": "",
        "title": "",
        "value": "INDICATOR CHANGED!",
        "color": "main",
    }
    shimoku_client.plt.change_current_tab("Indicators 2")
    shimoku_client.plt.indicator(data=indicators_data_2, order=0)
    shimoku_client.plt.change_current_tab("Indicators 1")
    shimoku_client.plt.indicator(data=indicators_data, order=0)

    shimoku_client.plt.set_tabs_index(
        tabs_index=("Deepness 1", "Bento box"),
        order=1,
        parent_tabs_index=("Deepness 0", "Indicators 1"),
        sticky=False,
        just_labels=True,
    )
    _test_bentobox()
    shimoku_client.plt.change_current_tab("Indicators 1")

    for i in range(2, 5):
        shimoku_client.plt.set_tabs_index(
            (f"Deepness {i}", "Indicators 2"),
            order=1,
            parent_tabs_index=(f"Deepness {i - 1}", "Indicators 1"),
            sticky=False,
            just_labels=True,
        )
        shimoku_client.plt.indicator(data=indicators_data_2, order=0)
        shimoku_client.plt.change_current_tab("Indicators 1")
        shimoku_client.plt.indicator(data=indicators_data, order=0)

    shimoku_client.plt.set_tabs_index(
        ("Bar deep 1", "Bar 1"),
        order=1,
        parent_tabs_index=("Deepness 0", "Bar 1"),
        sticky=False,
        just_labels=True,
    )
    shimoku_client.plt.bar(
        data="main data",
        x="date",
        x_axis_name="Date",
        y_axis_name="Revenue",
        order=0,
        rows_size=2,
        cols_size=12,
    )
    shimoku_client.plt.set_tabs_index(
        ("Bar deep 2", "Bar 2"),
        order=1,
        parent_tabs_index=("Bar deep 1", "Bar 1"),
        sticky=False,
        just_labels=True,
    )
    shimoku_client.plt.bar(
        data="main data",
        x="date",
        y="y",
        x_axis_name="Date",
        y_axis_name="Revenue",
        order=2,
        rows_size=2,
        cols_size=12,
    )
    shimoku_client.plt.change_current_tab("Line 1")
    shimoku_client.plt.line(
        data="main data",
        x="date",
        x_axis_name="Date",
        y_axis_name="Revenue",
        order=0,
        rows_size=2,
        cols_size=12,
    )
    shimoku_client.plt.change_current_tab("Line 2")
    shimoku_client.plt.line(
        data="main data",
        x="date",
        x_axis_name="Date",
        y_axis_name="Revenue",
        order=0,
        rows_size=2,
        cols_size=12,
    )
    shimoku_client.plt.pop_out_of_tabs_group()
