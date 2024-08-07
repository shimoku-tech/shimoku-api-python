from shimoku import Client
from .data.table import table_data


def table(shimoku_client: Client):
    shimoku_client.set_menu_path("test", "table")

    shimoku_client.plt.table(
        data=table_data,
        order=0,
        rows_size=3,
        title="Table test",
        page_size_options=[3, 5, 10],
        initial_sort_column="date",
        sort_descending=True,
        columns_options={"y": {"hideColumn": True}},
        categorical_columns=["filtA", "filtB"],
        web_link_columns={"webName": "web", "webName2": "web2"},
        buttons_column_definition=shimoku_client.plt.TableButtonColumnDefinition(
            column_name="Buttons",
            label="Press me to open a modal",
            modals_column="modal",
        ),
    )
