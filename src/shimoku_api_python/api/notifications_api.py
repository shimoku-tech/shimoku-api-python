""""""

from typing import Dict, Union

from pandas import DataFrame


class NotificationsApi(object):
    """
    """

    def __init__(self, api_client):
        self.api_client = api_client

    def post_notifications(
        self, report_data: Union[Dict, str, DataFrame],
        remove_previous: bool, is_single_owner: bool,
    ):
        raise NotImplementedError

    def get_active_notifications(self):
        raise NotImplementedError

    def get_notification_by_date(self):
        raise NotImplementedError
