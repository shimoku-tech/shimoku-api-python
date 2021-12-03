""""""

from typing import List, Dict, Optional

from pandas import DataFrame


class NotificationsApi(object):
    """
    """

    def __init__(self, api_client):
        self.api_client = api_client

    # TODO allow report_data it to be also a json!! '[{...}, {...}]'
    def post_notifications(
        self, report_df: pd.DataFrame, owner_id: str,
        remove_previous: bool, is_single_owner: bool,
    ):
        raise NotImplementedError

    def get_active_notifications(self):
        raise NotImplementedError

    def get_notification_by_date(self):
        raise NotImplementedError
