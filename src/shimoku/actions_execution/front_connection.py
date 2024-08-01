from typing import Optional
import logging

logger = logging.getLogger(__name__)


def aux_snackbar(message: str, variant: str):
    logger.info(f"Snackbar: {variant}: {message}")


class FrontEndConnectionAPI:
    def __init__(self, js_snackbar: callable = aux_snackbar):
        self.js_snackbar = js_snackbar

    def snackbar_error(self, message: str):
        """
        Show a snackbar with an error message.
        Only works in the browser.
        """
        self.js_snackbar(message, "error")

    def snackbar_info(self, message: str):
        """
        Show a snackbar with an info message.
        Only works in the browser.
        """
        self.js_snackbar(message, "info")

    def snackbar_success(self, message: str):
        """
        Show a snackbar with a success message.
        Only works in the browser.
        """
        self.js_snackbar(message, "success")


global_front_end_connection = FrontEndConnectionAPI()
