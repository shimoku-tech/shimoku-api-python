from shimoku.utils import IN_BROWSER

import logging

logger = logging.getLogger(__name__)


def snackbar_error(message: str):
    """
    Show a snackbar with an error message.
    Only works in the browser.
    """
    if IN_BROWSER:
        js_snackbar(message, "error")
    else:
        logger.info(f"Snackbar error: {message}")


def snackbar_info(message: str):
    """
    Show a snackbar with an info message.
    Only works in the browser.
    """
    if IN_BROWSER:
        js_snackbar(message, "info")
    else:
        logger.info(f"Snackbar info: {message}")


def snackbar_success(message: str):
    """
    Show a snackbar with a success message.
    Only works in the browser.
    """
    if IN_BROWSER:
        js_snackbar(message, "success")
    else:
        logger.info(f"Snackbar success: {message}")
