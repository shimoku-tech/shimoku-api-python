"""Exceptions for the Shimoku API module
"""


class MaxRetriesExceeded(Exception):
    """This exception is raised whenever the maximum
    allowed number of retries is exceeded.
    """
    pass
