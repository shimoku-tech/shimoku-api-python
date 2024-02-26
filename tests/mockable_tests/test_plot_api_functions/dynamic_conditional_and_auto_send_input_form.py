from shimoku import Client
from .data.dynamic_conditional_and_auto_send_input_form import form_groups


def dynamic_conditional_and_auto_send_input_form(shimoku_client: Client):
    shimoku_client.set_menu_path("Input forms", "dynamic conditional and auto send")

    shimoku_client.plt.generate_input_form_groups(
        order=0, form_groups=form_groups, dynamic_sequential_show=True
    )

    shimoku_client.plt.generate_input_form_groups(
        order=1,
        form_groups={
            "Personal information": form_groups["Personal information"],
            "Other data": form_groups["Other data"],
        },
        auto_send=True,
        dynamic_sequential_show=True,
    )
