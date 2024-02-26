from shimoku import Client
from .data.input_form import input_form_data


def get_input_forms(shimoku_client: Client):
    shimoku_client.set_menu_path("Input forms", "get input forms")
    shimoku_client.plt.input_form(order=0, options=input_form_data)
    rs: list[dict] = shimoku_client.plt.get_input_forms()
    print(rs)
    assert rs
