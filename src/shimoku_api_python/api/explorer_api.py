""""""

from typing import List, Dict, Optional


class GetExplorerAPI(object):

    def __init__(self, api_client):
        self.api_client = api_client

    # TODO pending https://trello.com/c/18GLgLoQ
    def get_business(self, business_id: str, **kwargs) -> Dict:
        """Retrieve an specific user_id

        :param business_id: user UUID
        """
        endpoint: str = f'business/{business_id}'
        business_data: Dict = (
            self.api_client.query_element(
                method='GET', endpoint=endpoint, **kwargs
            )
        )
        return business_data

    def get_app_type(self, app_type_id: str, **kwargs) -> Dict:
        """Retrieve an specific app_id metadata

        :param app_type_id: app type UUID
        """
        endpoint: str = f'apptype/{app_type_id}'
        app_data: Dict = (
            self.api_client.query_element(
                method='GET', endpoint=endpoint, **kwargs
            )
        )
        return app_data

    def get_app(self, business_id: str, app_id: str, **kwargs) -> Dict:
        """Retrieve an specific app_id metadata

        :param business_id: business UUID
        :param app_id: app UUID
        """
        endpoint: str = f'business/{business_id}/app/{app_id}'
        app_data: Dict = (
            self.api_client.query_element(
                method='GET', endpoint=endpoint, **kwargs
            )
        )
        return app_data

    def get_report(
        self,
        business_id: Optional[str] = None,
        app_id: Optional[str] = None,
        report_id: Optional[str] = None,
        external_id: Optional[str] = None,
        **kwargs,
    ) -> Dict:
        """Retrieve an specific report data

        :param business_id: business UUID
        :param app_id: Shimoku app UUID (only required if the external_id is provided)
        :param report_id: Shimoku report UUID
        :param external_id: external report UUID
        """
        if report_id:
            endpoint: str = f'business/{business_id}/app/{app_id}/report/{report_id}'
            report_data: Dict = (
                self.api_client.query_element(
                    method='GET',
                    endpoint=endpoint,
                    **kwargs
                )
            )
        elif external_id:
            if not app_id:
                raise ValueError(
                    'If you retrieve by external_id '
                    'you must provide an app_id'
                )

            report_ids_in_app: List[str] = (
                self.get_app_all_reports(app_id)
            )

            for report_id in report_ids_in_app:
                report_data_: Dict = self.get_report(report_id=report_id)
                if report_data_['etl_code_id'] == external_id:
                    endpoint: str = (
                        f'business/{business_id}/'
                        f'app/{app_id}/'
                        f'report/{report_id}'
                    )
                    report_data: Dict = (
                        self.api_client.query_element(
                            method='GET', endpoint=endpoint, **kwargs
                        )
                    )
                    return report_data
            else:
                return {}
        else:
            raise ValueError('Either report_id or external_id must be provided')

        return report_data

    # TODO pending
    #  https://trello.com/c/ndJs1WzW
    # TODO make it for both Table and non-table and paginate
    def get_report_data(
        self, business_id: str,
        app_id: Optional[str] = None,
        report_id: Optional[str] = None,
        external_id: Optional[str] = None,
    ) -> List[Dict]:
        """"""
        report = self.get_report(report_id)

        if report['reportType']:
            report: Dict = (
                self.get_report(
                    business_id=business_id,
                    app_id=app_id,
                    report_id=report_id,
                    external_id=external_id,
                )
            )
            return report['chartData']
        else:  # Table case
            raise NotImplementedError


class CreateExplorerAPI(object):

    def __init__(self, api_client):
        self.api_client = api_client

    # TODO pending https://trello.com/c/18GLgLoQ
    def create_business(
        self, owner_id: str, name: str,
    ):
        """"""
        endpoint: str = 'business'

        item: Dict = {  # This are the mandatory fields
            'owner': owner_id,
            'name': name,
            'type': 'PERSONAL',
            '__typename': 'Business',
            'businessUniverseId': '',  # TODO,
        }

        return self.api_client.query_element(
            method='POST', endpoint=endpoint, **{'data': item},
        )

    def create_app_type(
        self, owner_id: str, name: str,
    ):
        """"""
# TODO
        endpoint: str = 'apptype'

        item: Dict = {  # This are the mandatory fields
            'owner': owner_id,
            'name': name,
            'type': 'PERSONAL',
            '__typename': 'Business',
            'businessUniverseId': '',  # TODO,
        }

        return self.api_client.query_element(
            method='POST', endpoint=endpoint, **{'data': item},
        )

    # TODO pending https://trello.com/c/CNhYPEDe/
    def create_app(
        self, business_id: str,
        owner_id: Optional[str] = None,
        app_type_id: str = 'test',
        hide_title: bool = True,
        **kwargs,
    ):
        """"""
        endpoint: str = f'business/{business_id}/app'

        if not owner_id:
            owner_id = business_id

        item: Dict = {  # This are the mandatory fields
            'appBusinessId': business_id,
            'owner': owner_id,
            'appTypeId': app_type_id,
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

        return self.api_client.query_element(
            method='POST', endpoint=endpoint, **{'data': item},
        )

    # TODO
    def create_path(self):
        pass

    # TODO pending to be tried
    def create_report(
        self, business_id: str,
        app_id: str, owner_id: str,
        title: str, grid: str,
        order: Optional[int] = 0,
        smart_filters: str = '',
        fields: str = '',
        is_disabled: Optional[bool] = None,
        report_type: Optional[str] = None,  # None is table
        data: Optional[List] = None,
        code_id: Optional[str] = None, etl_code_version: Optional[str] = None,
        **kwargs,
    ) -> str:
        """Create new Report associated to an AppId

        :param business_id:
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
        :param data: data to post
        :param grid:
        :param report_type: Whether it is an Indicator, BarChart or any other
            non table report type.
        """
        endpoint: str = f'business/{business_id}/app/{app_id}/report'

        # This are the mandatory fields
        item: Dict = {
            'appId': app_id,
            'owner': owner_id,
            'order': order,
            'title': title,
            'isDisabled': is_disabled,
            '__typename': 'Report',
        }

        # This are the optional fields (previous were the mandatory ones)
        allowed_columns: List[str] = [
            'isDisabled', 'chartData',
            'reportType', 'path',
            'subscribe', 'chartDataAux',
            'description', 'grid',
            'codeETLId', 'codeETLVersion',
        ]
        # Check all kwargs keys are in the allowed_columns list
        assert all([key in allowed_columns for key in kwargs.keys()])
        # Update items with kwargs
        item.update(kwargs)

        if code_id:
            item['codeETLId'] = code_id

        if etl_code_version:
            item['codeETLVersion'] = etl_code_version

        if fields:
            item['dataFields'] = fields

        if grid:
            item['grid'] = grid

        if data:
            item['chartData'] = data

        if smart_filters:
            item['smartFilters'] = smart_filters

        if report_type is None:
            pass
        else:
            item['reportType'] = report_type

        return self.api_client.query_element(
            method='POST', endpoint=endpoint, **{'data': item},
        )


class UpdateExplorerAPI(object):

    def __init__(self, api_client):
        self.api_client = api_client

    # TODO pending https://trello.com/c/18GLgLoQ
    def update_business(self, business_id: str, business_data: Dict):
        """"""
        endpoint: str = f'business/{business_id}'
        return self.api_client.query_element(
            method='PATCH', endpoint=endpoint, **business_data,
        )

    def update_app_type(self, app_type_id: str, app_type_data: Dict):
        """"""
        endpoint: str = f'apptype/{app_type_id}'
        return self.api_client.query_element(
            method='PATCH', endpoint=endpoint, **app_type_data,
        )

    def update_app(self, business_id: str, app_id: str, app_data: Dict):
        """
        :param business_id:
        :param app_id:
        :param app_data: contain the elements to update key
            is the col name and value the value to overwrite
        """
        endpoint: str = f'business/{business_id}/app/{app_id}'
        return self.api_client.query_element(
            method='PATCH', endpoint=endpoint, **app_data,
        )

    def update_report(
        self, business_id: str, app_id: str, report_id: str, report_data,
    ) -> str:
        """"""
        endpoint: str = f'business/{business_id}/app/{app_id}/report/{report_id}'
        return self.api_client.query_element(
            method='PATCH', endpoint=endpoint, **report_data,
        )


class CascadeExplorerAPI(GetExplorerAPI):

    def __init__(self, api_client):
        super().__init__(api_client)

    # TODO pending
    #  https://trello.com/c/18GLgLoQ
    #  https://trello.com/c/lLvXz5UB
    def get_account_businesses(self):
        raise NotImplementedError

    def get_business_apps(self, business_id: str) -> List[Dict]:
        """Given a business retrieve all app metadata

        :param business_id: business UUID
        """
        endpoint: str = f'business/{business_id}/apps'
        apps_raw: Dict = (
            self.api_client.query_element(
                endpoint=endpoint, method='GET',
            )
        )
        apps = apps_raw.get('items')

        if not apps:
            return []
        return apps

    # TODO paginate
    def get_business_app_ids(self, business_id: str) -> List[str]:
        """Given a business retrieve all app ids

        :param business_id: business UUID
        """
        apps: Optional[List[Dict]] = (
            self.get_business_apps(
                business_id=business_id,
            )
        )
        return [app['id'] for app in apps]

    # TODO not possible yet
    def get_app_type_apps(self, app_type_id: str) -> List[Dict]:
        """"""
        endpoint: str = f'apptype/{app_type_id}/apps'
        apps_raw: Dict = (
            self.api_client.query_element(
                endpoint=endpoint, method='GET',
            )
        )
        apps = apps_raw.get('items')

        if not apps:
            return []
        return apps

    # TODO paginate
    def get_app_path_names(self, business_id: str, app_id: str) -> List[str]:
        """Given a Path that belongs to an AppId retrieve all reportId

        :param business_id: business UUID
        :param app_id: app UUID
        """
        reports: List[Dict] = (
            self.get_app_reports(
                business_id=business_id,
                app_id=app_id,
            )
        )

        paths: List[str] = []
        for report in reports:
            path: Optional[str] = report.get('path')
            if path:
                paths = paths + [path]
        return paths

    # TODO paginate
    def get_app_reports(self, business_id: str, app_id: str) -> List[Dict]:
        """Given an App Id retrieve all reports data from all reports
        that belongs to such App Id.
        """
        endpoint: str = f'business/{business_id}/app/{app_id}/reports'
        reports_raw: Dict = (
            self.api_client.query_element(
                endpoint=endpoint, method='GET',
            )
        )
        reports = reports_raw.get('items')
        if not reports:
            return []
        return reports

    # TODO paginate
    def get_app_report_ids(self, business_id: str, app_id: str) -> List[str]:
        """Given an app retrieve all report_id

        :param business_id: business UUID
        :param app_id: app UUID
        """
        reports: List[Dict] = (
            self.get_app_reports(
                business_id=business_id,
                app_id=app_id,
            )
        )
        return [report['id'] for report in reports]

# TODO pending
    def get_report_all_report_entries(self, report_id: str) -> List[str]:
        """Given a report retrieve all reportEntries

        :param report_id: app UUID
        """
        raise NotImplementedError

    # TODO paginate
    def get_path_report_ids(
        self, business_id: str, app_id: str, path_name: str,
    ) -> List[str]:
        """Given an App return all Reports ids that belong to a target path"""
        reports: List[Dict] = self.get_app_reports(
            business_id=business_id, app_id=app_id,
        )

        path_report_ids: List[str] = []
        for report in reports:
            path: Optional[str] = report.get('path')
            if path == path_name:
                report_id: str = report['id']
                path_report_ids = path_report_ids + [report_id]
        return path_report_ids

    def get_path_reports(
        self, business_id: str, app_id: str, path_name: str,
    ) -> List[Dict]:
        """Given an App return all Reports data that belong to a target path"""
        reports: List[Dict] = self.get_app_reports(
            business_id=business_id, app_id=app_id,
        )

        path_reports: List[Dict] = []
        for report in reports:
            path: Optional[str] = report.get('path')
            if path == path_name:
                path_reports = path_reports + [report]
        return path_reports

    # TODO pending
    #  https://trello.com/c/18GLgLoQ
    #  https://trello.com/c/lLvXz5UB
    # TODO paginate
    def get_business_apps_with_filter(
            self, business_id: str, app_filter: Dict
    ) -> List[Dict]:
        """
        # TODO filter example!!
        """
        app_ids: List[str] = (
            self.get_business_apps(
                business_id=business_id,
            )
        )

        apps: List[Dict] = []
        for app_id in app_ids:
            app: Dict = self.get_app(app_id)
            for filter_key, filter_value in app_filter.items():
                if app[filter_key] == filter_value:
                    apps.append(app)
        return apps

    # TODO pending
    #  https://trello.com/c/lLvXz5UB
    # TODO paginate
    def get_app_reports_by_filter(
        self, app_id: str,
        report_filter: Dict
    ) -> List[Dict]:
        """Having an AppId first retrieve all reportId that belongs
        to the target AppId. Second filter and take the reportId

        # TODO filter example!!
        """
        report_ids: List[str] = (
            self.get_app_all_reports(
                app_id=app_id,
            )
        )

        reports: List[Dict] = []
        for report_id in report_ids:
            report: Dict = self.get_report(report_id=report_id)
            for filter_key, filter_value in report_filter.items():
                if report[filter_key] == filter_value:
                    reports.append(report)
            return reports


# TODO unused by the moment
class ReverseCascadeExplorerAPI(CascadeExplorerAPI):

    def __init__(self, api_client):
        super().__init__(api_client)

    def get_business_id_by_app(self, app_id: str, **kwargs) -> str:
        """Retrieve an specific app_id metadata

        :param app_id: app UUID
        """
        app_data: Dict = self.get_app(app_id=app_id, **kwargs)
        return app_data['businessId']

    def get_app_id_by_path(self, path_name: str, **kwargs) -> str:
        """Bottom-up method
        Having a path return the app it belongs to
        """
        raise NotImplemented

    def get_app_id_by_report(self, report_id: str, **kwargs) -> str:
        """Bottom-up method
        Having a report_id return the app it belongs to
        """
        report_data: Dict = self.get_report(
            report_id=report_id, **kwargs,
        )
        return report_data['appId']

    def get_reports_in_same_app(self, report_id: str) -> List[str]:
        """Return all reports that are in the same app that the target report"""
        report_data: Dict = self.get_report(report_id=report_id)
        app_id: str = report_data['appId']
        return self.get_app_all_reports(app_id)

    def get_reports_in_same_path(
        self, business_id, app_id: str, report_id: str,
    ) -> List[str]:
        """Return all reports that are in the same path that the target report"""
        report_data: Dict = self.get_report(
            business_id=business_id, app_id=app_id, report_id=report_id,
        )
        path_name: str = report_data['path']
        return self.get_path_reports(
            business_id=business_id,
            app_id=app_id,
            path_name=path_name,
        )


class MultiCascadeExplorerAPI(ReverseCascadeExplorerAPI):

    def __init__(self, api_client):
        super().__init__(api_client)

    # TODO paginate
    def get_business_paths(self, business_id: str) -> List[str]:
        """Given a business retrieve all path names

        :param business_id: business UUID
        """
        app_ids: List[str] = self.get_business_apps(business_id=business_id)
        paths: List[str] = []
        for app_id in app_ids:
            app_paths: List[str] = self.get_app_paths(app_id=app_id)
            paths = paths + app_paths
        return paths

    # TODO paginate
    def get_business_reports(self, business_id: str) -> List[str]:
        """Given a business retrieve all report ids

        :param business_id: business UUID
        """
        app_ids: List[str] = self.get_business_apps(business_id=business_id)
        report_ids: List[str] = []
        for app_id in app_ids:
            app_report_ids: List[str] = self.get_app_reports(app_id=app_id)
            report_ids = report_ids + app_report_ids
        return report_ids

    # TODO paginate
    def get_business_id_by_report(self, report_id: str, **kwargs) -> str:
        """Bottom-up method
        Having a report_id return the app it belongs to
        """
        app_id: str = self.get_app_id_by_report(report_id=report_id, **kwargs)
        business_id: str = self.get_business_id_by_app(app_id=app_id, **kwargs)
        return business_id


class DeleteExplorerApi(MultiCascadeExplorerAPI):
    """Get Businesses, Apps, Paths and Reports in any possible combination
    """

    def __init__(self, api_client):
        super().__init__(api_client)

    # TODO pending
    #  https://trello.com/c/18GLgLoQ
    #  https://trello.com/c/lLvXz5UB
    def delete_business(self, business_id: str):
        """Delete a Business.
        All apps, reports and data associated with that business is removed by the API
        """
        endpoint: str = f'business/{business_id}'
        self.api_client.query_element(
            method='DELETE', endpoint=endpoint,
        )

    def delete_app_type(self, app_type_id: str):
        """Delete an appType"""
        endpoint: str = f'apptype/{app_type_id}'
        self.api_client.query_element(
            method='DELETE', endpoint=endpoint,
        )

# TODO remove reports must not be configurable, it must do it always
# TODO joder claro puedo hacer un cascade de business
#  y así con el app_id por parte del cliente es suficiente!!!
    # TODO pending
    #  https://trello.com/c/18GLgLoQ
    #  https://trello.com/c/lLvXz5UB
    def delete_app(self, business_id: str, app_id: str) -> Dict:
        """Delete an App
        All reports and data associated with that app is removed by the API
        """
        endpoint: str = f'business/{business_id}/app/{app_id}'
        result: Dict = self.api_client.query_element(
            method='DELETE', endpoint=endpoint
        )
        return result

    # TODO pending
    #  https://trello.com/c/18GLgLoQ
    #  https://trello.com/c/lLvXz5UB
    def delete_path(self, business_id: str, app_id: str, path_name: str):
        """Delete all Reports in a path
        All data associated with that report is removed by the API"""
        report_ids: List[str] = (
            self.get_path_reports(
                business_id=business_id,
                app_id=app_id,
                path_name=path_name,
            )
        )
        for report_id in report_ids:
            self.delete_report_and_entries(report_id)

    # TODO pending
    #  https://trello.com/c/18GLgLoQ
    #  https://trello.com/c/lLvXz5UB
    # TODO WiP
    def delete_report(
        self, business_id: str, app_id: str, report_id: str,
        relocating: bool = True, delete_data: bool = True,
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


class BusinessExplorerApi:
    """"""
    get_business = GetExplorerAPI.get_business
    create_business = CreateExplorerAPI.create_business
    update_business = UpdateExplorerAPI.update_business

    get_business_apps = CascadeExplorerAPI.get_business_apps
    get_business_app_ids = CascadeExplorerAPI.get_business_app_ids
    get_business_all_apps_with_filter = CascadeExplorerAPI.get_business_apps_with_filter

    delete_business = DeleteExplorerApi.delete_business


class AppTypeExplorerApi:
    """"""
    get_app_type = GetExplorerAPI.get_app_type
    create_app_type = CreateExplorerAPI.create_app_type
    update_app_type = UpdateExplorerAPI.update_app_type

    get_app_type_apps = CascadeExplorerAPI.get_app_type_apps

    delete_app_type = DeleteExplorerApi.delete_app_type


class AppExplorerApi:

    get_app = GetExplorerAPI.get_app
    create_app = CreateExplorerAPI.create_app
    update_app = UpdateExplorerAPI.update_app

    get_app_reports = CascadeExplorerAPI.get_app_reports
    get_app_report_ids = CascadeExplorerAPI.get_app_report_ids
    get_app_path_names = CascadeExplorerAPI.get_app_path_names
    get_app_reports_by_filter = MultiCascadeExplorerAPI.get_app_reports_by_filter

    delete_app = DeleteExplorerApi.delete_app


class PathExplorerApi:

    get_report = GetExplorerAPI.get_report
    update_report = UpdateExplorerAPI.update_report
    get_path_reports = MultiCascadeExplorerAPI.get_path_reports
    get_path_report_ids = MultiCascadeExplorerAPI.get_path_report_ids


class ReportExplorerApi:

    get_report = GetExplorerAPI.get_report
    get_report_data = GetExplorerAPI.get_report_data

    create_report = CreateExplorerAPI.create_report

    update_report = UpdateExplorerAPI.update_report

    get_business_id_by_report = MultiCascadeExplorerAPI.get_business_id_by_report

    delete_report = DeleteExplorerApi.delete_report


class ExplorerApi(
    CreateExplorerAPI,
    UpdateExplorerAPI,
    DeleteExplorerApi,
):
    """Get Businesses, Apps, Paths and Reports in any possible combination
    """

    def __init__(self, api_client):
        super().__init__(api_client)

    # TODO WiP
    def has_app_report_data(self, business_id: str, app_id: str) -> bool:
        """"""
        report_ids: List[str] = self.get_app_report_ids(
            business_id=business_id, app_id=app_id
        )
        for report_id in report_ids:
            result: bool = self.has_report_report_entries(report_id)
            if result:
                return True
        return False

    # TODO WiP
    def has_path_data(self, business_id: str, app_id: str, path_name: str) -> bool:
        """"""
        report_ids: List[str] = self.get_app_report_ids(
            business_id=business_id, app_id=app_id
        )
        for report_id in report_ids:
            result: bool = self.has_report_report_entries(report_id)
            if result:
                return True
        return False
