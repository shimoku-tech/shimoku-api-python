""""""

from typing import List, Dict, Optional
import json

from shimoku_api_python.exceptions import ApiClientError


class GetExplorerAPI(object):

    def __init__(self, api_client):
        self.api_client = api_client

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

    def _get_report_with_data(
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

        if report_data.get('chartData'):
            report_data['chartData'] = json.loads(report_data['chartData'])
        return report_data

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
        report_data: Dict = (
            self._get_report_with_data(
                business_id=business_id,
                app_id=app_id,
                report_id=report_id,
                external_id=external_id,
            )
        )
        # we do not return the chartData in the get_report()
        #  use _get_report_with_data() instead
        if report_data.get('chartData'):
            report_data.pop('chartData')
        return report_data

    def get_report_data(
        self, business_id: str,
        app_id: Optional[str] = None,
        report_id: Optional[str] = None,
        external_id: Optional[str] = None,
    ) -> List[Dict]:
        """"""
        report: Dict = self.get_report(
            business_id=business_id,
            app_id=app_id,
            report_id=report_id,
        )

        if report['reportType']:
            report: Dict = (
                self._get_report_with_data(
                    business_id=business_id,
                    app_id=app_id,
                    report_id=report_id,
                    external_id=external_id,
                )
            )
            report_data: List = report.get('chartData')
            if report_data:
                return report_data
            else:
                return list()
        else:
            endpoint: str = (
                f'business/{business_id}/'
                f'app/{app_id}/'
                f'report/{report_id}/reportEntries'
            )
            report_entries: Dict = [
                self.api_client.query_element(
                    method='GET', endpoint=endpoint,
                )
            ]
            return report_entries[0]['items']


class CascadeExplorerAPI(GetExplorerAPI):

    def __init__(self, api_client):
        super().__init__(api_client)

    def get_universe_businesses(self) -> List[Dict]:
        endpoint: str = f'businesses'
        return (
            self.api_client.query_element(
                endpoint=endpoint, method='GET',
            )
        )['items']

    def find_business_by_name_filter(
        self, name: Optional[str] = None,
    ) -> Dict:
        """"""
        businesses: List[Dict] = self.get_universe_businesses()

        businesses: List[Dict] = [
            business
            for business in businesses
            if business['name'] == name
        ]
        if not businesses:
            return {}

        assert len(businesses) == 1
        business: Dict = businesses[0]
        return business

    def get_universe_app_types(self) -> List[Dict]:
        endpoint: str = f'apptypes'
        return (
            self.api_client.query_element(
                endpoint=endpoint, method='GET',
            )
        )['items']

    def find_app_type_by_name_filter(
        self, name: Optional[str] = None,
        normalized_name: Optional[str] = None,
    ) -> Dict:
        """"""
        app_types: List[Dict] = self.get_universe_app_types()

        if name:
            app_types: List[Dict] = [
                app_type
                for app_type in app_types
                if app_type['name'] == name
            ]
        elif normalized_name:
            app_types: List[Dict] = [
                app_type
                for app_type in app_types
                if app_type['normalizedName'] == app_type_name
            ]

        if not app_types:
            return {}

        assert len(app_types) == 1
        app_type: Dict = app_types[0]
        return app_type

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
        apps: List[Dict] = apps_raw.get('items')

        if not apps:
            return []
        return apps

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

    def get_business_apps_with_filter(
            self, business_id: str, app_filter: Dict
    ) -> List[Dict]:
        """
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

    def get_app_by_type(
        self, business_id: str, app_type_id: str,
    ) -> Dict:
        """
        :param business_id: business UUID
        :param app_type_id: appType UUID
        """
        apps: List[Dict] = self.get_business_apps(business_id=business_id)

        # Is expected to be a single item (Dict) but an App
        # could have several reports with the same name
        result: Any = {}
        for app in apps:
            if app['type']['id'] == app_type_id:
                if result:
                    if len(result) == 1:
                        result: List[Dict] = result + [app]
                    else:
                        result: List[Dict] = result + [app]
                else:
                    result: List[Dict] = [app]
        if result:
            assert len(result) == 1
            return result[0]
        else:
            return {}

    def get_app_by_name(
        self, business_id: str, name: str,
    ) -> Dict:
        """
        :param business_id: business UUID
        :param app_type_id: appType UUID
        """
        apps: List[Dict] = self.get_business_apps(business_id=business_id)

        # Is expected to be a single item (Dict) but an App
        # could have several reports with the same name
        result: Any = {}
        for app in apps:
            app_type: Dict = self.get_app_type(
                # business_id=business_id,
                app_type_id=app['type']['id'],
            )
            if app_type['normalizedName'] == name:
                if result:
                    if len(result) == 1:
                        result: List[Dict] = result + [app]
                    else:
                        result: List[Dict] = result + [app]
                else:
                    result: List[Dict] = [app]
        if result:
            assert len(result) == 1
            return result[0]
        else:
            return {}


class CreateExplorerAPI(object):
    _find_business_by_name_filter = CascadeExplorerAPI.find_business_by_name_filter
    _find_app_type_by_name_filter = CascadeExplorerAPI.find_app_type_by_name_filter

    def __init__(self, api_client):
        self.api_client = api_client

    def create_business(self, name: str) -> Dict:
        """"""
        business: Dict = self._find_business_by_name_filter(name=name)
        if business:
            raise ValueError(f'A Business with the name {name} already exists')

        endpoint: str = 'business'

        item: Dict = {'name': name}

        return self.api_client.query_element(
            method='POST', endpoint=endpoint, **{'body_params': item},
        )

    def create_app_type(self, name: str) -> Dict:
        """"""
        app_type: Dict = self._find_app_type_by_name_filter(name=name)
        if app_type:
            raise ValueError(f'An AppType with the name {name} already exists')

        endpoint: str = 'apptype'
        # for instance:
        # "name": "Test Borrar"
        # "key": "TEST_BORRAR"
        # "normalizedName": "test-borrar"
        key: str = '_'.join(name.split(' ')).upper()
        normalized_name: str = '-'.join(name.split(' ')).lower()

        item: Dict = {
            'name': name,
            'key': key,
            'normalizedName': normalized_name,
        }

        return self.api_client.query_element(
            method='POST', endpoint=endpoint, **{'body_params': item},
        )

    def create_app(
        self, business_id: str,
        app_type_id: Optional[str],
        app_metadata: Optional[Dict] = None,
    ) -> Dict:
        """
        """
        endpoint: str = f'business/{business_id}/app'

        item: Dict = {  # These are the mandatory fields
            # 'appBusinessId': business_id,  # Not necessary its taken from the URL
            'appTypeId': app_type_id,
        }

        if app_metadata:
            hide_title: bool = app_metadata.get('hideTitle')
            if hide_title:
                item['hideTitle'] = 'true' if hide_title else 'false'
            else:
                item['hideTitle'] = 'true'

            # These are the optional fields (previous were the mandatory ones)
            allowed_columns: List[str] = [
                'paymentType', 'trialDays',
                'appSubscriptionInUserId',
            ]
            # Check all kwargs keys are in the allowed_columns list
            assert all([key in allowed_columns for key in app_metadata.keys()])
            # Update items with kwargs
            item.update(app_metadata)
        else:
            item['hideTitle'] = 'true'

        return self.api_client.query_element(
            method='POST', endpoint=endpoint, **{'body_params': item},
        )

    def create_app_from_app_type_normalized_name(self, app_type_name: str) -> Dict:
        """Create AppType and App if required and return the App component
        """
        try:
            app_type: Dict = self._create_app_type(name=app_type_name)
        except ValueError:  # It already exists then
            app_type: Dict = (
                self._find_app_type_by_name_filter(name=app_type_name)
            )

        app_type_id: str = app_type['id']
        apps: Dict = self._get_business_apps(business_id=self.business_id)
        target_apps = [app for app in apps if app['appType']['id'] == app_type_id]

        if not apps:
            app: Dict = (
                self._create_app(
                    business_id=self.business_id,
                    app_type_id=app_type_id,
                )
            )
        else:
            app: Dict = target_apps[0]
        return app

    def create_report(
        self, business_id: str, app_id: str, report_metadata: Dict,
        real_time: bool = False,
    ) -> Dict:
        """Create new Report associated to an AppId

        :param business_id:
        :param app_id:
        :param report_metadata: A dict with all the values required to create a report
        """
        def append_fields(item: Dict, field_name: str) -> Dict:
            """Equivalent to
            grid: Optional[str] = report_metadata.get('grid')
            if grid:
                item['grid'] = grid
            """
            field_value: Optional[str] = report_metadata.get(field_name)
            if field_value is not None:
                item[field_name] = field_value
            return item

        endpoint: str = f'business/{business_id}/app/{app_id}/report'

        # These are the mandatory fields
        title: str = report_metadata['title']

        # These are the mandatory fields
        item: Dict = {
            'appId': app_id,
            'title': title,
        }

        item: Dict = append_fields(item=item, field_name='path')
        item: Dict = append_fields(item=item, field_name='grid')
        item: Dict = append_fields(item=item, field_name='reportType')
        item: Dict = append_fields(item=item, field_name='order')
        item: Dict = append_fields(item=item, field_name='sizeColumns')
        item: Dict = append_fields(item=item, field_name='sizeRows')
        item: Dict = append_fields(item=item, field_name='padding')

        if real_time:
            item['subscribe'] = True

        # Update items with kwargs
        item.update(report_metadata)

        # Optional values
        report_type: str = report_metadata.get('reportType')
        if report_type:
            if report_type != 'Table':  # Tables have reportType as None
                item['reportType'] = report_type
            elif report_metadata.get('smartFilters'):
                # Smart filters only exists for Tables
                item['smartFilters'] = report_metadata['smartFilters']

        report: Dict = (
            self.api_client.query_element(
                method='POST', endpoint=endpoint,
                **{'body_params': item},
            )
        )

        return {
            k: v
            for k, v in report.items()
            if k not in ['chartData', 'owner', 'chartDataItem']  # we do not return the data
        }

    def _create_report_entries(
        self, business_id: str, app_id: str, report_id: str,
        items: List[Dict],
    ) -> List[Dict]:
        """Create new reportEntry associated to a Report

        :param business_id:
        :param app_id:
        :param report_id:
        :param report_entry_metadata: A dict with all the values required to create a reportEntry
        """
        endpoint: str = (
            f'business/{business_id}/'
            f'app/{app_id}/'
            f'report/{report_id}/'
            f'reportEntry'
        )

        report_entries: List[Dict] = []
        for item in items:
            report_entry: Dict = (
                self.api_client.query_element(
                    method='POST', endpoint=endpoint,
                    **{'body_params': item},
                )
            )
            report_entries = report_entries + [report_entry]

        return report_entries


class UpdateExplorerAPI(CascadeExplorerAPI):
    _find_business_by_name_filter = CascadeExplorerAPI.find_business_by_name_filter
    _find_app_type_by_name_filter = CascadeExplorerAPI.find_app_type_by_name_filter

    def __init__(self, api_client):
        self.api_client = api_client

    def update_business(self, business_id: str, business_data: Dict) -> Dict:
        """"""
        name = business_data.get('name')
        if name:
            business: Dict = self._find_business_by_name_filter(name=name)
            if business:
                raise ValueError(
                    f'Cannot Update | '
                    f'A Business with the name {name} already exists'
                )

        endpoint: str = f'business/{business_id}'
        return self.api_client.query_element(
            method='PATCH', endpoint=endpoint, **{'body_params': business_data},
        )

    def update_app_type(self, app_type_id: str, app_type_metadata: Dict) -> Dict:
        """"""
        name = app_type_metadata.get('name')
        if name:
            _app_type: Dict = self._find_app_type_by_name_filter(name=name)
            if _app_type:
                raise ValueError(
                    f'Cannot Update | '
                    f'A AppType with the name {name} already exists'
                )

        endpoint: str = f'apptype/{app_type_id}'
        return self.api_client.query_element(
            method='PATCH', endpoint=endpoint, **{'body_params': app_type_metadata},
        )

    def update_app(self, business_id: str, app_id: str, app_metadata: Dict) -> Dict:
        """
        :param business_id:
        :param app_id:
        :param app_data: contain the elements to update key
            is the col name and value the value to overwrite
        """
        endpoint: str = f'business/{business_id}/app/{app_id}'
        return self.api_client.query_element(
            method='PATCH', endpoint=endpoint,
            **{'body_params': app_metadata},
        )

    def update_report(
        self, business_id: str, app_id: str, report_id: str,
        report_metadata: Dict,
    ) -> Dict:
        """"""
        endpoint: str = f'business/{business_id}/app/{app_id}/report/{report_id}'
        return self.api_client.query_element(
            method='PATCH', endpoint=endpoint,
            **{'body_params': report_metadata},
        )


class MultiCascadeExplorerAPI(CascadeExplorerAPI):

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


class DeleteExplorerApi(MultiCascadeExplorerAPI, UpdateExplorerAPI):
    """Get Businesses, Apps, Paths and Reports in any possible combination
    """

    def __init__(self, api_client):
        super().__init__(api_client)

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

    def delete_app(self, business_id: str, app_id: str) -> Dict:
        """Delete an App
        All reports and data associated with that app is removed by the API
        """
        endpoint: str = f'business/{business_id}/app/{app_id}'
        result: Dict = self.api_client.query_element(
            method='DELETE', endpoint=endpoint
        )
        return result

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

    def delete_report(
        self, business_id: str, app_id: str, report_id: str,
        relocating: bool = True, delete_data: bool = True,
    ) -> None:
        """Delete a Report, relocating reports underneath to avoid errors
        """
        reports: List[Dict] = (
            self._get_app_reports(
                business_id=business_id,
                app_id=app_id
            )
        )
        target_report: Dict = self.get_report(
            business_id=business_id,
            app_id=app_id,
            report_id=report_id,
        )
        target_report_grid: str = target_report.get('grid')

        # TO BE deprecated with row, column and grid!
        # TODO this looks like a different method
        if target_report_grid:
            target_report_row: int = int(target_report_grid.split(',')[0])
            for report in reports:
                report_grid: str = report.get('grid')
                if report_grid:
                    report_row: int = int(report_grid.split(',')[0])
                    if report_row > target_report_row:
                        report_row -= 1
                        report_column: int = int(report.get('grid').split(',')[1])
                        grid: str = f'{report_row}, {report_column}'
                        self.update_report(
                            business_id=business_id,
                            app_id=app_id, report_id=report_id,
                            report_metadata={'grid': grid},
                        )

        endpoint: str = f'business/{business_id}/app/{app_id}/report/{report_id}'
        result: Dict = self.api_client.query_element(
            method='DELETE', endpoint=endpoint
        )
        return result

    def delete_report_entries(
        self, business_id: str, app_id: str, report_id: str,
    ) -> None:
        """Delete a Report, relocating reports underneath to avoid errors
        """
        report_entries: List[Dict] = (
            self.get_report_data(
                business_id=business_id,
                app_id=app_id,
                report_id=report_id,
            )
        )

        for report_entry in report_entries:
            report_entry_id: str = report_entry['id']
            endpoint: str = (
                f'business/{business_id}/'
                f'app/{app_id}/'
                f'report/{report_id}/'
                f'reportEntry/{report_entry_id}'
            )
            result: Dict = self.api_client.query_element(
                method='DELETE', endpoint=endpoint
            )


class MultiDeleteApi:
    """Get Businesses, Apps, Paths and Reports in any possible combination
    """
    _get_business = GetExplorerAPI.get_business
    _get_app_type = GetExplorerAPI.get_app_type
    _get_app = GetExplorerAPI.get_app

    _delete_business = DeleteExplorerApi.delete_business
    _delete_app = DeleteExplorerApi.delete_app
    _delete_app_type = DeleteExplorerApi.delete_app_type
    _delete_report = DeleteExplorerApi.delete_report

    def __init__(self):
        return

    def _delete_business_and_app_type(
        self, business_id: str, app_type_id: str
    ):
        try:
            self._delete_business(business_id)
        except Exception as e_bd:
            raise ValueError(
                f'{e_bd} | Nor Business nor AppType were deleted | ' 
                f'business_id: {business_id} | '
                f'app_type_id: {app_type_id}'
            )

        try:
            _ = self._get_business(business_id)
        except ApiClientError:
            pass
        except Exception as e_gb:
            raise ValueError(
                f'{e_gb} | Nor Business nor AppType were deleted | '
                f'business_id: {business_id} | app_type_id: {app_type_id}'
            )

        try:
            self._delete_app_type(app_type_id)
        except ApiClientError:
            return {}
        except Exception as e_atd:
            raise ValueError(
                f'{e_atd} | AppType was not deleted | '
                f'app_type_id: {app_type_id}'
            )

        try:
            _ = self._get_app_type(app_type_id)
        except ApiClientError:
            return {}
        except Exception as e_atg:
            raise ValueError(
                f'{e_atg} | AppType was not deleted | '
                f'app_type_id: {app_type_id}'
            )

    def _delete_business_and_app(
        self, business_id: str, app_id: str,
    ):
        try:
            self._delete_business(business_id)
        except Exception as e_bd:
            raise ValueError(
                f'{e_bd} | Nor Business nor App were deleted | ' 
                f'business_id: {business_id} | '
                f'app_id: {app_id}'
            )

        try:
            _ = self._get_business(business_id)
        except ApiClientError:
            pass
        except Exception as e_gb:
            raise ValueError(
                f'{e_gb} | Nor Business nor App were deleted | '
                f'business_id: {business_id} | '
                f'app_id: {app_id}'
            )

        try:
            self._delete_app(app_id)
        except ApiClientError:
            return {}
        except Exception as e_atd:
            raise ValueError(
                f'{e_atd} | App was not deleted | '
                f'app_id: {app_id}'
            )

        try:
            _ = self._get_app(app_id)
        except ApiClientError:
            return {}
        except Exception as e_atg:
            raise ValueError(
                f'{e_atg} | App was not deleted | '
                f'app_id: {app_id}'
            )


class MultiCreateApi(MultiDeleteApi):
    """If some upper level elements are not created it does it
    """
    _get_universe_app_types = CascadeExplorerAPI.get_universe_app_types
    _get_app_by_type = CascadeExplorerAPI.get_app_by_type

    _create_business = CreateExplorerAPI.create_business
    _create_app_type = CreateExplorerAPI.create_app_type
    _create_app = CreateExplorerAPI.create_app
    _create_report = CreateExplorerAPI.create_report

    def __init__(self):
        super().__init__()

    def create_business_and_app(
        self, app_type_id: str, business_name: str, app_metadata: Dict,
    ) -> Dict[str, Dict]:
        """Create new Report associated to an AppId

        :param app_type_id:
        :param business_name:
        :param app_metadata:
        """
        business: Dict = self._create_business(name=business_name)
        business_id: str = business['id']

        try:
            app: Dict = (
                self._create_app(
                    business_id=business_id,
                    app_type_id=app_type_id,
                    app_metadata=app_metadata,
                )
            )
        except Exception as e:
            self._delete_business(business_id=business_id)
            try:
                _ = self._get_business(business_id)
                raise ValueError(
                    f'{e} | The app was not created but a new business did '
                    f'that probably should be deleted manually with id '
                    f'{business_id}'
                )
            except ApiClientError:
                return {}

        return {
            'business': business,
            'app': app,
        }

    def create_app_type_and_app(
        self, business_id: str,
        app_type_metadata: Dict,
        app_metadata: Optional[Dict] = None,
    ) -> Dict[str, Dict]:
        """
        If app_type_id is None we create it
        """
        try:
            app_type: Dict = self._create_app_type(**app_type_metadata)
        except ValueError:
            app_type_name: str = app_type_metadata['name']
            app_type: Dict = self._get_app_type_by_name(app_type_name)

        app_type_id: str = app_type['id']
        app_metadata['app_type_id'] = app_type_id
        app_metadata['business_id'] = business_id

        app: Dict = self._get_app_by_type(
            business_id=business_id,
            app_type_id=app_type_id,
        )
        if not app:
            app: Dict = self._create_app(**app_metadata)

        return {
            'app_type': app_type,
            'app': app
        }

    def create_app_and_report(
        self, business_id: str, app_type_id: str,
        app_metadata: Dict, report_metadata: Dict,
    ) -> Dict:
        """Create new Report associated to an AppId

        :param business_id:
        :param app_type_id:
        :param app_metadata:
        :param report_metadata: A dict with all the values required to create a report
        """
        app: Dict = (
            self._create_app(
                business_id=business_id,
                app_type_id=app_type_id,
                app_metadata=app_metadata,
            )
        )
        app_id: str = app['id']

        try:
            report: Dict = (
                self._create_report(
                    business_id=business_id,
                    app_id=app_id,
                    report_metadata=report_metadata,
                )
            )
        except Exception as e:
            raise f'{e} | app_id created: {app_id} | Better delete it'

        return report

    def create_business_app_and_app_type(
        self, business_name: str,
        app_metadata: Dict,
        app_type_metadata: Dict,
    ) -> Dict[str, Dict]:
        """
        """
        app_type: Dict = self._create_app_type(**app_type_metadata)
        app_type_id: str = app_type['id']
        app_metadata['app_type_id'] = app_type_id

        business: Dict = {}
        try:
            business: Dict = self._create_business(business_name)
            business_id: str = business['id']
            app_metadata['business_id'] = business_id
        except Exception as e:
            try:
                self._delete_app_type(app_type_id=app_type_id)
            except ApiClientError:
                return {}
            except Exception as e:
                raise ValueError(
                    f'Business was not created | '
                    f'AppType was created with app_type_id = {app_type_id}'
                    f'App was not created | '
                )

        app: Dict = {}
        try:
            app: Dict = self._create_app(**app_metadata)
        except Exception as e:
            try:
                self._delete_business_and_app_type(
                    business_id=business_id,
                    app_type_id=app_type_id,
                )
            except ApiClientError:
                return {}
            except Exception as e:
                raise ValueError(f'App was not created | {e}')

        return {
            'business': business,
            'app_type': app_type,
            'app': app
        }

    def create_business_app_and_report(
        self, app_type_id: str,
        business_name: str,
        app_metadata: Dict,
        report_metadata: Dict,
    ) -> Dict[str, Dict]:
        """
        """
        business: Dict = self.create_business(business_name)
        business_id: str = business['id']
        app_metadata['business_id'] = business_id
        app_metadata['app_type_id'] = app_type_id

        try:
            app: Dict = self.create_app(
                business_id=business_id,
                app_metadata=app_metadata,
            )
            app_id = app['id']
        except Exception as e:
            try:
                self.delete_business(business_id)
            except ApiClientError:
                return {}
            except Exception as e:
                raise ValueError(
                    f'{e} | Business with business_id {business_id} '
                    f'created that probably wants to be removed | '
                    f'App was not created | '
                    f'Report was not created'
                )

        try:
            report: Dict = self.create_report(
                business_id=business_id,
                app_id=app_id,
                report_metadata=report_metadata,
            )
        except Exception as e:
            try:
                self._delete_business_and_app(
                    business_id=business_id,
                    app_id=app_id,
                )
            except ApiClientError:
                return {}
            except Exception as e_dba:
                raise ValueError(
                    f'{e} | {e_dba} | Report was not created'
                )
            return {}

        return {
            'business': business,
            'app': app,
            'report': report,
        }

    def create_business_app_type_app_and_report(
        self, business_name: str,
        app_type_metadata: Dict,
        app_metadata: Dict,
        report_metadata: Dict,
    ) -> Dict[str, Dict]:
        """
        """
        d = self.create_business_app_and_app_type(
            business_name=business_name,
            app_type_metadata=app_type_metadata,
            app_metadata=app_metadata,
        )
        business_id: str = d['business']['id']
        app_id: str = d['app']['id']

        try:
            report: Dict = self.create_report(
                business_id=business_id,
                app_id=app_id,
                report_metadata=report_metadata,
            )
        except Exception as e:
            try:
                self._delete_business_and_app(
                    business_id=business_id,
                    app_id=app_id,
                )
            except ApiClientError:
                return {}
            except Exception as e_:
                raise ValueError(
                    f'{e} | {e_} | Report was not created'
                )

            try:
                app_type_id: str = d['app_type']['id']
                self.delete_app_type(app_type_id)
            except Exception as e_:
                raise ValueError(
                    f'{e_} | Report was not created | '
                    f'App type was created with app_type_id: {app_type_id}'
                )
            return {}

        return {
            'app_type': d['app_type'],
            'business': d['business'],
            'app': d['app'],
            'report': report,
        }


class UniverseExplorerApi:
    """"""
    get_universe_businesses = CascadeExplorerAPI.get_universe_businesses
    get_universe_app_types = CascadeExplorerAPI.get_universe_app_types


class BusinessExplorerApi:
    """"""
    get_business = GetExplorerAPI.get_business
    get_universe_businesses = CascadeExplorerAPI.get_universe_businesses
    _find_business_by_name_filter = CascadeExplorerAPI.find_business_by_name_filter
    create_business = CreateExplorerAPI.create_business
    update_business = UpdateExplorerAPI.update_business

    get_business_apps = CascadeExplorerAPI.get_business_apps
    get_business_app_ids = CascadeExplorerAPI.get_business_app_ids
    get_business_all_apps_with_filter = CascadeExplorerAPI.get_business_apps_with_filter

    delete_business = DeleteExplorerApi.delete_business


class AppTypeExplorerApi:
    """"""
    get_app_type = GetExplorerAPI.get_app_type
    get_universe_app_types = CascadeExplorerAPI.get_universe_app_types
    _find_app_type_by_name_filter = CascadeExplorerAPI.find_app_type_by_name_filter
    create_app_type = CreateExplorerAPI.create_app_type
    update_app_type = UpdateExplorerAPI.update_app_type

    delete_app_type = DeleteExplorerApi.delete_app_type


class AppExplorerApi:

    get_app = GetExplorerAPI.get_app
    create_app = CreateExplorerAPI.create_app
    update_app = UpdateExplorerAPI.update_app

    _get_business_apps = CascadeExplorerAPI.get_business_apps
    get_business_apps = CascadeExplorerAPI.get_business_apps
    get_app_reports = CascadeExplorerAPI.get_app_reports
    get_app_report_ids = CascadeExplorerAPI.get_app_report_ids
    get_app_path_names = CascadeExplorerAPI.get_app_path_names
    get_app_reports_by_filter = MultiCascadeExplorerAPI.get_app_reports_by_filter
    get_app_by_type = CascadeExplorerAPI.get_app_by_type
    get_app_type = CascadeExplorerAPI.get_app_type
    get_app_by_name = CascadeExplorerAPI.get_app_by_name

    delete_app = DeleteExplorerApi.delete_app


class PathExplorerApi:

    _get_report = GetExplorerAPI.get_report

    _update_report = UpdateExplorerAPI.update_report

    _get_app_reports = CascadeExplorerAPI.get_app_reports
    _get_app_path_names = CascadeExplorerAPI.get_app_path_names

    get_path_reports = MultiCascadeExplorerAPI.get_path_reports
    get_path_report_ids = MultiCascadeExplorerAPI.get_path_report_ids


class ReportExplorerApi:

    get_report = GetExplorerAPI.get_report
    get_report_data = GetExplorerAPI.get_report_data
    _get_report_with_data = GetExplorerAPI._get_report_with_data

    _get_app_reports = CascadeExplorerAPI.get_app_reports

    create_report = CreateExplorerAPI.create_report
    create_app_and_report = MultiCreateApi.create_app_and_report

    update_report = UpdateExplorerAPI.update_report

    get_business_id_by_report = MultiCascadeExplorerAPI.get_business_id_by_report

    delete_report = DeleteExplorerApi.delete_report


class ExplorerApi(
    CreateExplorerAPI,
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
