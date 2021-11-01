""""""

from typing import List, Dict, Optional

from pandas import DataFrame


# TODO https://trello.com/c/4cMvn5OU/


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
        """Post notification. In case a notification
        exists with the same owner and same title
        we can choose to remove that one
        """
        table_name: str = f'Notification-{self.table_name_suffix}'

        # IMPORTANT
        # Note we want it to be
        # such as '2014-12-10T12:00:00Z'
        # rather than '2014-12-10T12:00:00.895210'
        # to match our FE processing
        now = dt.datetime.utcnow().isoformat()[:-3]+'Z'

        # Whether to send this notification to a
        # single user or to the whole databse of users
        if is_single_owner:
            owner: str = owner_id
        else:
            owner: str = 'shimoku'

        report_df['owner'] = owner

        # Many notifications happen with a certain frequency
        #  what we do here is remove the previous notification
        #  of the same kind that the one we are about to send
        if remove_previous:
            filter_expression = (
                    Key('owner').eq(owner)
                    &
                    Key('title').eq(report_df['title'].values[0])
            )
            self.delete_many_items_in_table(
                table_name=table_name, filter_expression=filter_expression
            )

        report_df['createdAt'] = now
        report_df['updatedAt'] = now
        report_df['__typename'] = 'Notification'
        # Set hashes for id
        report_df['id'] = [
            str(uuid.uuid4()) for _ in range(len(report_df.index))
        ]

        # owner, reportId and abstract columns
        entries: List[Dict] = (
            report_df.to_dict(orient='records')
        )

        # query_conditions = Key('reportId').eq(report_id)
        # post all entries to Dynamo
        self.put_many_items(
            table_name=table_name, items=entries,
        )

    def get_active_notifications(self):
        raise NotImplementedError

    def get_notification_by_date(self):
        raise NotImplementedError
