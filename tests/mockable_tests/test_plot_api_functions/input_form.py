from shimoku import Client
from .data.input_form import input_form_data


def input_form(shimoku_client: Client):
    """Test input form"""
    shimoku_client.set_menu_path("Input forms")
    shimoku_client.plt.input_form(order=0, options=input_form_data)
