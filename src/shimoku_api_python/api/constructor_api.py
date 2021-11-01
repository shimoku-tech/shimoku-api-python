""""""

from typing import List, Dict
import uuid

import datetime as dt


class ConstructorApi(object):
    """
    """

    def __init__(self, api_client):
        self.api_client = api_client

    def create_app(
        self, business_id: str, owner_id: str, app_type_id: str,
        trial_days: int = 30, hide_title: bool = True,
        **kwargs,
    ) -> None:
        """"""
        table_name: str = f'App-{self.table_name_suffix}'
        now: str = (
            f'{dt.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3]}Z'
        )

        # IMPORTANT!! If you change the names
        # `codeETLId` or `codeETLVersion` change
        # them as well in the method
        # create_or_update_report() herein
        item: Dict = {  # This are the mandatory fields
            'appBusinessId': business_id,
            'owner': owner_id,
            'appTypeId': app_type_id,
            'createdAt': now,
            'updatedAt': now,
            'trialDays': trial_days,
            '__typename': 'App',
        }

        if hide_title:
            item['hideTitle'] = hide_title

        # This are the optional fields (previous were the mandatory ones)
        allowed_columns: List[str] = [
            'paymentType', 'trialDays',
            'appSubscriptionInUserId',
        ]
        # Check all kwargs keys are in the allowed_columns list
        assert all([key in allowed_columns for key in kwargs.keys()])
        # Update items with kwargs
        item.update(kwargs)
        item['id'] = str(uuid.uuid4())

        self.put_item(table_name=table_name, item=item)

# TODO it must contain the possibility to pass the data already
    def create_report(
        self, app_id: str, owner_id: str,
        fields: str, order: int, title: str,
        smart_filters: str, is_disabled: str,
        code_id: str, etl_code_version: str,
        db_report_id: str = str(),
        report_created_at: Optional[str] = None,
        report_type: Optional[str] = None,
        **kwargs,
    ) -> None:
        """Create new Report associated to an AppId

        :param app_id:
        :param owner_id:
        :param fields: Example
            {
                "Churn class":
                 {
                    "field": "stringField1",
                    "filterBy": [
                        "Very probable", "Probable",
                        "Improbable", "Very Improbable",
                    ]
                },
                "Churn probability" : {
                    "field" : "intField1",
                    "filterBy": None,
                    }
                },
                ...
            }
        :param smart_filters:
            [
                {
                    "filters": {
                        # segment
                        abstractFilters.stringField1.value: [
                            "Best customers",
                            "Good customers"
                        ],
                        # purchase soon
                        abstractFilters.stringField2.value: [
                            "caution"
                        ]
                    },
                    "question": "Prepare next shoppers offer"
                },
                {
                    "filters": {
                        # segment
                        abstractFilters.stringField1.value: [
                            "Best customers",
                            "Good customers"
                        ],
                        # churn
                        abstractFilters.stringField3.value: [
                            "caution"
                        ]
                    },
                    "question": "Customers to save from churn"
                }
            ],
        :param is_disabled: whether the report is shown or not
        :param order:
        :param title:
        :param code_id: It is the code identifier of the report BusinessETL.
            Every ETL has an ID field that identifies it.
        :param etl_code_version: It is the version of the BusinessETL.
            When versions change we know we have to UPDATE (NEVER delete+create)
            the Report
        :param db_report_id: It is the `ID` of the target `Report` within Dynamo
            When it is not null is because we are doing and update (delete+create)
            and we have to keep the ID for the rows in `ReportEntry`
        :param report_created_at: For when we re-create an existing report we pass
            the old report creationAt so that we hold it as it is.
        :param report_type: Whether it is an Indicator, BarChart or any other
            non table report type.
        """
        table_name: str = f'Report-{self.table_name_suffix}'
        now = dt.datetime.utcnow().isoformat()

        # IMPORTANT!! If you change the names
        # `codeETLId` or `codeETLVersion` change
        # them as well in the method
        # create_or_update_report() herein
        item: Dict = {  # This are the mandatory fields
            'codeETLId': code_id,
            'codeETLVersion': etl_code_version,
            'appId': app_id,
            'owner': owner_id,
            'order': order,
            'title': title,
            'updatedAt': now,
            'isDisabled': is_disabled,
            '__typename': 'Report',
        }

        # This are the optional fields (previous were the mandatory ones)
        allowed_columns: List[str] = [
            'isDisabled', 'chartData',
            'reportType', 'path',
            'subscribe', 'chartDataAux',
            'description', 'grid'
        ]
        # Check all kwargs keys are in the allowed_columns list
        assert all([key in allowed_columns for key in kwargs.keys()])
        # Update items with kwargs
        item.update(kwargs)

        if fields:
            item['dataFields'] = fields

        if smart_filters:
            item['smartFilters'] = smart_filters

        if db_report_id:
            item['id'] = db_report_id
        else:
            item['id'] = str(uuid.uuid4())

        if report_type is None:
            pass
        else:
            item['reportType'] = report_type

        if report_created_at is None:
            item['createdAt'] = now
        else:
            item['createdAt'] = report_created_at

        self.put_item(table_name=table_name, item=item)

# TODO
    def create_path(self):
        pass

### Deletes
    def delete_app(self, app_id: str, remove_reports: bool = True):
        """Delete an App"""
        table_name: str = f'App-{self.table_name_suffix}'
        self.delete_item(
            table_name=table_name,
            item_id=app_id,
            key_attribute='id',
        )

    def delete_path(self, app_id: str, path: str):
        """Delete all Reports in a path"""
        report_ids: List[str] = (
            self.get_target_path_all_reports(
                app_id=app_id, path=path,
            )
        )
        for report_id in report_ids:
            self.delete_report_and_entries(report_id)

# TODO is much smarter to pass relocating as argument of delete_report()
# TODO we wouldnt need the app_id as input here
    def delete_report(
        self, report_id: str, relocating: bool = True,
        delete_data: bool = True,
    ) -> None:
        """Delete a Report, relocating reports underneath to avoid errors
        """
        reports: List[Dict] = (
            self.get_target_app_all_reports_data(app_id=app_id)
        )
        target_report: Dict = self.get_target_report(report_id)
        target_report_grid: str = target_report.get('grid')

        # TODO this looks like a different method
        if target_report_grid:
            target_report_row: int = int(target_report_grid.split(',')[0])
            for report in reports:
                report_row: int = int(report.get('grid').split(',')[0])
                if report_row > target_report_row:
                    report_row -= 1
                    report_column: int = int(report.get('grid').split(',')[1])
                    grid: str = f'{report_row}, {report_column}'
                    self.update_report_grid_position(
                        app_id=app_id, report_id=report_id,
                        grid=grid, reorganize_grid=False,
                    )

        table_name: str = f'Report-{self.table_name_suffix}'
        self.delete_item(
            table_name=table_name,
            item_id=report_id,
            key_attribute='id',
        )
