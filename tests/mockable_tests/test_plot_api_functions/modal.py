from shimoku import Client
from .data.table import table_data


def modal(shimoku_client: Client):
    prediction_header = (
        "<head>"
        "<style>"  # Styles title
        ".component-title{height:auto; width:100%; "
        "border-radius:16px; padding:16px;"
        "display:flex; align-items:center;"
        "background-color:var(--chart-C1); color:var(--color-white);}"
        "<style>.base-white{color:var(--color-white);}</style>"
        "</head>"  # Styles subtitle
        "<div class='component-title'>"
        "<div class='big-icon-banner'></div>"
        "<div class='text-block'>"
        "<h1>Predictions</h1>"
        "<p class='base-white'>"
        "Modal Test</p>"
        "</div>"
        "</div>"
    )
    shimoku_client.set_menu_path("Modal Test")

    shimoku_client.plt.set_modal(
        "Test modal", open_by_default=True, width=70, height=60
    )
    shimoku_client.plt.html(html=prediction_header, order=0)

    shimoku_client.plt.set_tabs_index(("Test", "Tab 1"), order=1)
    shimoku_client.plt.table(
        data=table_data,
        order=0,
        rows_size=3,
        title="Table test",
        categorical_columns=["filtA", "filtB"],
    )
    shimoku_client.plt.pop_out_of_tabs_group()

    shimoku_client.plt.html(html=prediction_header, order=2)
    shimoku_client.plt.pop_out_of_modal()

    shimoku_client.plt.html(html=prediction_header, order=0)
    shimoku_client.plt.set_tabs_index(("TestNoModal", "Table"), order=1)
    shimoku_client.plt.table(
        data=table_data,
        order=0,
        rows_size=3,
        title="Table test",
        categorical_columns=["filtA", "filtB"],
    )
    shimoku_client.plt.pop_out_of_tabs_group()

    shimoku_client.plt.modal_button(order=2, modal="Test modal", label="Open modal")
