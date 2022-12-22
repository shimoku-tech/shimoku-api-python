""""""

from typing import List, Dict, Optional, Any, Union
import json
from time import sleep

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
        app_type_data: Dict = (
            self.api_client.query_element(
                method='GET', endpoint=endpoint, **kwargs
            )
        )
        return app_type_data

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

# TODO add new data & dataset logic!
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

    def get_dataset(self, business_id: str, dataset_id: str, **kwargs) -> Dict:
        """Retrieve an specific app_id metadata

        :param business_id: business UUID
        :param dataset_id: dataset UUID
        """
        endpoint: str = f'business/{business_id}/dataset/{dataset_id}'
        dataset_data: Dict = (
            self.api_client.query_element(
                method='GET', endpoint=endpoint, **kwargs
            )
        )
        return dataset_data

    def get_reportdataset(
            self, business_id: str, app_id: str, report_id: str,
            reportdataset_id: str, **kwargs
    ) -> Dict:
        """Retrieve an specific app_id metadata

        :param business_id: business UUID
        :param app_id: app UUID
        :param report_id: report UUID
        :param reportdataset_id: reportDataSet UUID
        """
        endpoint: str = (
            f'business/{business_id}/'
            f'app/{app_id}/'
            f'report/{report_id}/'
            f'{reportdataset_id}'
        )
        dataset_data: Dict = (
            self.api_client.query_element(
                method='GET', endpoint=endpoint, **kwargs
            )
        )
        return dataset_data

# TODO add new data & dataset logic!
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
            report_entries: List = [
                self.api_client.query_element(
                    method='GET', endpoint=endpoint,
                )
            ]
            return report_entries[0]['items']

    def get_file(
            self, business_id: Optional[str] = None,
            app_id: Optional[str] = None,
            file_id: Optional[str] = None,
    ) -> bytes:
        """Retrieve an specific file from an app

        :param business_id: business UUID
        :param app_id: Shimoku app UUID (only required if the external_id is provided)
        :param file_id: Shimoku report UUID
        """
        endpoint: str = f'business/{business_id}/app/{app_id}/file/{file_id}'
        file_data: str = self.api_client.query_element(method='GET', endpoint=endpoint)

        try:
            url: str = file_data['url']
        except KeyError:
            raise KeyError(f'Could not GET file')

        file_object = self.api_client.raw_request(
            **dict(method='GET', url=url)
        )
        return file_object.content

    def get_files(
            self, business_id: Optional[str] = None,
            app_id: Optional[str] = None,
    ) -> List[Dict]:
        """Retrieve an specific file from an app

        :param business_id: business UUID
        :param app_id: Shimoku app UUID (only required if the external_id is provided)
        """
        endpoint: str = f'business/{business_id}/app/{app_id}/files'
        files: List[Dict] = self.api_client.query_element(method='GET', endpoint=endpoint)
        return files


class CascadeExplorerAPI(GetExplorerAPI):

    def __init__(self, api_client):
        super().__init__(api_client)
        # self.cached_apps = {}

    # def __cache_apps_by_normalized_name(self, apps):
    #     for app in apps:
    #         self.cached_apps[app['appBusinessId']+app['normalizedName']] = app

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
                if app_type['normalizedName'] == normalized_name
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

    def get_business_all_files(self, business_id) -> List[Dict]:
        """Given a business retrieve all files metadata
        """
        apps: List[Dict] = self.get_business_apps(business_id=business_id)
        files: List[Dict] = list
        for app in apps:
            files = files + self.get_files(business_id=business_id, app_id=app['id'])
        return files

    def find_app_by_name_filter(
        self, business_id: str, name: Optional[str] = None,
        normalized_name: Optional[str] = None,
    ) -> Dict:
        """"""
        apps_list: List[Dict] = self.get_business_apps(business_id=business_id)

        if name:
            apps: List[Dict] = [
                app
                for app in apps_list
                if app['name'] == name
            ]
        elif normalized_name:
            apps: List[Dict] = [
                app
                for app in apps_list
                if app['normalizedName'] == normalized_name
            ]

        if not apps:
            return {}

        assert len(apps) == 1
        apps: Dict = apps[0]
        return apps

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

    def get_business_reports(self, business_id: str) -> List[Dict]:
        """Given a business retrieve all reports

        :param business_id: business UUID
        """
        business_apps = self.get_business_apps(business_id)
        return [report
                for app_id in business_apps
                    for report in self.get_app_reports(business_id, app_id['id'])]

    def get_business_report_ids(self, business_id: str) -> List[str]:
        """Given an business retrieve all report_ids

        :param business_id: business UUID
        """
        business_apps = self.get_business_apps(business_id)
        return [report['id']
                for app_id in business_apps
                    for report in self.get_app_reports(business_id, app_id['id'])]

    def get_report_datasets(
            self, business_id: str, app_id: str,  report_id: str,
    ) -> List[Dict]:
        endpoint: str = (
            f'business/{business_id}/'
            f'app/{app_id}/'
            f'report/{report_id}/'
            f'reportDataSets'
        )
        reportdatasets: List[Dict] = (
            self.api_client.query_element(
                endpoint=endpoint, method='GET',
            )
        )
        reportdatasets = reportdatasets.get('items')
        if not reportdatasets:
            return []

        data_sets: List[Dict] = []
        for reportdataset in reportdatasets:
            endpoint: str = (
                f'business/{business_id}/'
                f'dataSet/{reportdataset["dataSetId"]}'
            )
            data_set: Dict = (
                self.api_client.query_element(
                    endpoint=endpoint, method='GET',
                )
            )
            if data_set.get('reportDataSets'):
                data_sets = data_sets + [data_set]
        return data_sets

    def get_dataset_data(
            self, business_id: str, dataset_id: str,
    ) -> List[Dict]:
        endpoint: str = (
            f'business/{business_id}/'
            f'dataSet/{dataset_id}/'
            f'datas'
        )
        datas_raw: List[Dict] = (
            self.api_client.query_element(
                endpoint=endpoint, method='GET',
            )
        )
        datas = datas_raw.get('items')
        if not datas:
            return []
        return datas

    def get_report_dataset_data(
            self, business_id: str, app_id: str, report_id: str,
    ) -> List[Dict]:
        """"""
        report_datasets: List[Dict] = self.get_report_datasets(
            business_id=business_id, app_id=app_id, report_id=report_id,
        )
        data: List = []
        for report_dataset in report_datasets:
            dataset_id: str = report_dataset['id']
            datum: List[Dict] = (
                self.get_dataset_data(
                    business_id=business_id,
                    dataset_id=dataset_id,
                )
            )
            data = data + datum
        return data

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
        apps: List[Dict] = (
            self.get_business_apps(
                business_id=business_id,
            )
        )

        apps: List[Dict] = []
        for app in apps:
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

    def get_app_type_by_name(
            self, name: Optional[str] = None,
            normalized_name: Optional[str] = None,
    ) -> Dict:
        """
        :param business_id: business UUID
        :param name: appType name
        :param normalized_name: appType normalizedName
        """
        if not name and not normalized_name:
            raise ValueError('You must provide either "name" or "normalized_name"')

        app_types: List[Dict] = self.get_universe_app_types()

        result: List[Dict] = [
            app_type
            for app_type in app_types
            if (
                    app_type['name'] == name
                    or app_type['normalizedName'] == normalized_name
            )
        ]

        if result:
            assert len(result) == 1
            return result[0]
        else:
            return {}

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
            if not app.get('type'):  # is not mandatory for app to have an AppType
                continue

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

    def get_app_by_name(self, business_id: str, name: str) -> Dict:
        """
        First normalizes the name and then searches for a match, if a match isn't found it tries to search for app_type
        :param business_id: business UUID
        :param name: app or apptype name
        """
        # This normalizes the name, we can't use the function to normalize name because its in another class from this
        # file, with the same level of responsibility, and it might create unwanted dependencies
        name = name.strip().replace('_', '-')
        name = '-'.join(name.split(' ')).lower()

        # if business_id+name in self.cached_apps:
        #     return self.cached_apps[business_id+name]

        apps: List[Dict] = self.get_business_apps(business_id=business_id)
        # self.__cache_apps_by_normalized_name(apps)

        # Is expected to be a single item (Dict) but an App
        # could have several reports with the same name
        result: Any = {}
        for app in apps:
            # if App name does not match check the AppType,
            # if it does not match the AppType Name then pass to the following App
            if app.get('normalizedName'):
                if not app['normalizedName'] == name:
                    continue
            else:
                if not app.get('type'):
                    continue
                try:
                    app_type: Dict = self.get_app_type(
                        app_type_id=app['type']['id'],
                    )
                except ApiClientError:  # Business admin user
                    continue

                if (
                    not app_type['normalizedName'] == name
                    and
                    not app_type['name'] == name
                ):
                    continue

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

    def _create_normalized_name(self, name: str) -> str:
        """Having a name create a normalizedName

        Example
        ----------------------
        # "name": "   Test Borrar_grafico    "
        # "normalizedName": "test-borrar-grafico"
        """
        # remove empty spaces at the beginning and end
        name: str = name.strip()
        # replace "_" for www protocol it is not good
        name = name.replace('_', '-')

        return '-'.join(name.split(' ')).lower()

    def _create_key_name(self, name: str) -> str:
        """Having a name create a key

        Example
        ----------------------
        # "name": "Test Borrar"
        # "key": "TEST_BORRAR"
        """
        return '_'.join(name.split(' ')).upper()

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
        normalized_name: str = self._create_normalized_name(name)
        key: str = self._create_key_name(name)

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
        name: Optional[str],
        app_type_id: Optional[str] = None,
        app_metadata: Optional[Dict] = None,
    ) -> Dict:
        """
        """
        endpoint: str = f'business/{business_id}/app'
        item: Dict = {}

        if app_type_id:
            item['appTypeId'] = app_type_id

        normalized_name: str = self._create_normalized_name(name)
        item['name'] = name
        item['normalizedName'] = normalized_name

        item['hideTitle'] = 'true'
        if app_metadata:
            hide_title: bool = app_metadata.get('hideTitle')
            hide_path: bool = app_metadata.get('hidePath')
            show_breadcrumb: bool = app_metadata.get('showBreadcrumb')
            show_history: bool = app_metadata.get('showHistoryNavigation')

            if not hide_title and hide_title is not None:
                item['hideTitle'] = 'false'

            item['hidePath'] = 'true' if hide_path else 'false'
            item['showBreadcrumb'] = 'true' if show_breadcrumb else 'false'
            item['showHistoryNavigation'] = 'true' if show_history else 'false'

            # These are the optional fields (previous were the mandatory ones)
            allowed_columns: List[str] = [
                'paymentType', 'trialDays', 'appSubscriptionInUserId',
                'hideTitle', 'hidePath', 'showBreadcrumb', 'showHistoryNavigation'
            ]
            # Check all kwargs keys are in the allowed_columns list
            assert all([key in allowed_columns for key in app_metadata.keys()])
            # Update items with kwargs
            item.update(app_metadata)

        return self.api_client.query_element(
            method='POST', endpoint=endpoint, **{'body_params': item},
        )

    def create_report(
        self, business_id: str, app_id: str, report_metadata: Dict,
        real_time: bool = False,
    ) -> Dict:
        """Create new Report associated to an AppId

        :param business_id:
        :param app_id:
        :param report_metadata: A dict with all the values required to create a report
        :param real_time: Whether it is real time or not
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
        # title: str = report_metadata['title']

        # These are the mandatory fields
        item: Dict = {'appId': app_id}

        item: Dict = append_fields(item=item, field_name='title')
        item: Dict = append_fields(item=item, field_name='path')
        item: Dict = append_fields(item=item, field_name='pathOrder')
        item: Dict = append_fields(item=item, field_name='grid')
        item: Dict = append_fields(item=item, field_name='reportType')
        item: Dict = append_fields(item=item, field_name='order')
        item: Dict = append_fields(item=item, field_name='sizeColumns')
        item: Dict = append_fields(item=item, field_name='sizeRows')
        item: Dict = append_fields(item=item, field_name='padding')
        item: Dict = append_fields(item=item, field_name='bentobox')
        item: Dict = append_fields(item=item, field_name='properties')

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

    def create_dataset(self, business_id: str) -> Dict:
        """Create new DataSet associated to a business

        :param business_id:
        """
        endpoint: str = f'business/{business_id}/dataSet'

        return self.api_client.query_element(
            method='POST', endpoint=endpoint, **{'body_params': {}},
        )

    def create_reportdataset(
            self, business_id: str, app_id: str, report_id: str,
            dataset_id: str, dataset_properties: str,
    ) -> Dict:
        """Create new dataset associated to a Report

        :param business_id:
        :param app_id:
        :param report_id:
        :param dataset_id:
        :param dataset_properties: a json with the properties
        """
        endpoint: str = (
            f'business/{business_id}/'
            f'app/{app_id}/'
            f'report/{report_id}/'
            f'reportDataSet'
        )

        item: Dict = {
            'reportId': report_id,
            'dataSetId': dataset_id,
        }

        if dataset_properties:
            item['properties'] = dataset_properties

        return self.api_client.query_element(
            method='POST', endpoint=endpoint, **{'body_params': item},
        )

    def create_data_points(
            self, business_id: str, dataset_id: str,
            items: List[str],
    ) -> List[Dict]:
        """Create new row in Data (equivalent to reportEntry)

        :param business_id:
        :param dataset_id:
        :param items:
        """
        endpoint: str = (
            f'business/{business_id}/'
            f'dataSet/{dataset_id}/'
            f'data'
        )

        data: List[Dict] = []
        for item in items:
            datum: Dict = (
                self.api_client.query_element(
                    method='POST', endpoint=endpoint,
                    **{'body_params': item},
                )
            )
            sleep(.25)
            data = data + [datum]

        return data

    def _create_report_entries(
        self, business_id: str, app_id: str, report_id: str,
        items: List[Dict], batch_size: int = 999,
    ) -> List[Dict]:
        """Create new reportEntry associated to a Report

        :param business_id:
        :param app_id:
        :param report_id:
        :param items: A dict with all the values required to create a reportEntry
        """
        if batch_size >= 1000:
            raise ValueError('batch_size must be less than 1000')

        endpoint: str = (
            f'business/{business_id}/'
            f'app/{app_id}/'
            f'report/{report_id}/'
            f'reportEntry/batch'
        )

        #report_entries: List[Dict] = []
        for chunk in range(0, len(items), batch_size):
            #report_entries_batch = report_entries + (
            self.api_client.query_element(
                method='POST', endpoint=endpoint,
                **{'body_params': items[chunk:chunk + batch_size]},
            )
            #)
            sleep(.25)
            #report_entries = report_entries + [report_entries_batch]

        #return report_entries

    def create_file(
            self, business_id: str, app_id: str,
            file_metadata: Dict, file_object: bytes,
    ) -> Dict:
        """Create new Files associated to an AppId

        Example
        ------------
            file_metadata= {
                name: String
                fileName: String (It should be normalized)
                contentType: String (Content type of the file you want to upload. Ex: image/png)
            }

        :param business_id:
        :param app_id:
        :param file_metadata:
        """
        endpoint: str = f'business/{business_id}/app/{app_id}/file'

        file_data: str = (
            self.api_client.query_element(
                method='POST', endpoint=endpoint,
                **{'body_params': file_metadata},
            )
        )
        try:
            url: str = file_data['url']
        except KeyError:
            raise KeyError(f'Could not POST file')

        r = self.api_client.raw_request(
            **dict(
                method='PUT', url=url, data=file_object,
                headers={'Content-Type': 'text/csv'},
            )
        )
        try:
            assert all([r.status_code >= 200,  r.status_code < 300])
            file_data['Success'] = True
        except AssertionError:
            file_data['Success'] = False
        file_data['Status'] = r.status_code
        file_data.pop('url')
        return file_data


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
        :param app_metadata: contain the elements to update key
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

    def update_reportdataset(
            self, business_id: str, app_id: str, report_id: str,
            reportdataset_id: str, reportdataset_metadata: Dict,
    ) -> Dict:
        """"""
        endpoint: str = (
            f'business/{business_id}/'
            f'app/{app_id}/'
            f'report/{report_id}/'
            f'{reportdataset_id}'
        )
        return self.api_client.query_element(
            method='PATCH', endpoint=endpoint,
            **{'body_params': reportdataset_metadata},
        )

    def update_dataset(
            self, business_id: str, dataset_id: str,
            dataset_metadata: Dict,
    ) -> Dict:
        """"""
        endpoint: str = f'business/{business_id}/dataset/{dataset_id}'
        return self.api_client.query_element(
            method='PATCH', endpoint=endpoint,
            **{'body_params': dataset_metadata},
        )


class MultiCascadeExplorerAPI(CascadeExplorerAPI):

    def __init__(self, api_client):
        super().__init__(api_client)

    # TODO paginate
    def get_business_paths(self, business_id: str) -> List[str]:
        """Given a business retrieve all path names

        :param business_id: business UUID
        """
        apps: List[Dict] = self.get_business_apps(business_id=business_id)
        paths: List[str] = []
        for app in apps:
            app_id: str = app['id']
            app_paths: List[str] = self.get_app_paths(app_id=app_id)
            paths = paths + app_paths
        return paths

    # TODO paginate
    def get_business_reports(self, business_id: str) -> List[str]:
        """Given a business retrieve all report ids

        :param business_id: business UUID
        """
        apps: List[Dict] = self.get_business_apps(business_id=business_id)
        report_ids: List[str] = []
        for app in apps:
            app_id: str = app['id']
            app_reports: List[Dict] = self.get_app_reports(
                business_id=self.business_id,
                app_id=app_id,
            )
            report_ids = report_ids + [
                app_report['id']
                for app_report in app_reports
            ]
        return report_ids

    # TODO paginate
    def get_business_id_by_report(self, report_id: str, **kwargs) -> str:
        """Bottom-up method
        Having a report_id return the app it belongs to
        """
        app_id: str = self.get_app_id_by_report(report_id=report_id, **kwargs)
        business_id: str = self.get_business_id_by_app(app_id=app_id, **kwargs)
        return business_id


class CascadeCreateExplorerAPI(CreateExplorerAPI):
    update_report = UpdateExplorerAPI.update_report

    def __init__(self, api_client):
        self.api_client = api_client

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

    def create_report_and_dataset(
        self, business_id: str, app_id: str,
        report_metadata: Dict,
        items: Union[List[str], Dict],
        report_properties: Dict,
        report_dataset_properties: Optional[Dict] = None,
        sort: Optional[Dict] = None,
        real_time: bool = False,
    ) -> Dict[str, Union[Dict, List[Dict]]]:
        """
        Example
        -------
        sort = {
            'field': 'date'
            'direction': 'asc',
        }

        1. Create a report
        2. Create a dataset
        3. Create data associated to a dataset
        4. Associate dataset and report through reportDataSet
        """
        report: Dict = self.create_report(
            business_id=business_id,
            app_id=app_id,
            report_metadata=report_metadata,
            real_time=real_time,
        )

        dataset: Dict = self.create_dataset(business_id=business_id)
        dataset_id: str = dataset['id']

        if type(items) == list:  # ECHARTS2
            items_keys: Optional[List[str]] = list(items[0].keys())
            report_dataset_properties = {'mapping': items_keys}
            if sort:
                report_dataset_properties['sort'] = sort

        elif type(items) == dict:  # FORM
            items_keys: Optional[List[str]] = None
            items = [items]
            try:
                assert report_dataset_properties is not None
            except AssertionError:
                raise ValueError(
                    'report_dataset_properties is required if items is a dict'
                )
        else:
            raise ValueError('items must be a list or dict')

        report_dataset: Dict = self.create_reportdataset(
            business_id=business_id,
            app_id=app_id,
            report_id=report['id'],
            dataset_id=dataset_id,
            dataset_properties=json.dumps(report_dataset_properties),
        )

        data: List[Dict] = self.create_data_points(
            business_id=business_id,
            dataset_id=dataset_id,
            items=items,
        )

        # Syntax to be accepted by the FrontEnd
        options_dataset_id: str = '#{' + f'{report_dataset["id"]}' + '}'
        report_properties['dataset'] = {'source': options_dataset_id}
        if items_keys is not None:  # ECHARTS2
            report_properties['dimensions']: items_keys
        report_properties = {'properties': json.dumps({'option': report_properties})}

        report: Dict = self.update_report(
            business_id=business_id,
            app_id=app_id,
            report_id=report['id'],
            report_metadata=report_properties,
        )

        return {
            'report': report,
            'dataset': dataset,
            'report_dataset': report_dataset,
            'data': data,
        }


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
        reports: List[Dict] = (
            self.get_path_reports(
                business_id=business_id,
                app_id=app_id,
                path_name=path_name,
            )
        )
        for report in reports:
            report_id: str = report['id']
            self.delete_report_and_entries(report_id)

    def delete_report(
        self, business_id: str, app_id: str, report_id: str,
        relocating: bool = True, delete_data: bool = True,
    ) -> Dict:
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

    def delete_reportdataset(
            self, business_id: str, app_id: str,
            report_id: str, reportdataset_id: str,
    ) -> Dict:
        """"""
        endpoint: str = (
            f'business/{business_id}/'
            f'app/{app_id}/'
            f'report/{report_id}/'
            f'{reportdataset_id}'
        )
        result: Dict = self.api_client.query_element(
            method='DELETE', endpoint=endpoint
        )
        return result

    def delete_dataset(self, business_id: str, dataset_id: str) -> Dict:
        """"""
        endpoint: str = f'business/{business_id}/dataset/{dataset_id}'
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
            _: Dict = self.api_client.query_element(
                method='DELETE', endpoint=endpoint
            )

    def delete_file(
        self, business_id: str, app_id: str, file_id: str,
    ) -> Dict:
        """Delete a file
        """
        endpoint: str = f'business/{business_id}/app/{app_id}/file/{file_id}'
        result: Dict = self.api_client.query_element(method='DELETE', endpoint=endpoint)
        return result


# TODO los siguientes puntos:
#  . Si elimino (delete) un report se eliminan sus reportdataset?
#  . Tengo función cascade para dado un report coger (GET) todos los reportdataset?
#  . No puedo crear data sin un dataset asociado, esto es así?
#  . Si elimino (delete) un dataset se eliminan sus data ?
#  . Tengo función cascade para dado un dataset coger (GET) todos los data?
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
    _delete_dataset = DeleteExplorerApi.delete_dataset

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

    def delete_report_and_dataset(
            self, business_id: str, app_id: str, report_id: str, dataset_id: str,
    ):
        self._delete_report(
            business_id=business_id,
            app_id=app_id,
            report_id=report_id
        )
        self._delete_dataset(business_id=business_id, dataset_id=dataset_id)


class MultiCreateApi(MultiDeleteApi):
    """If some upper level elements are not created it does it
    """
    _get_universe_app_types = CascadeExplorerAPI.get_universe_app_types
    _get_app_by_type = CascadeExplorerAPI.get_app_by_type

    _create_business = CascadeCreateExplorerAPI.create_business
    _create_app_type = CascadeCreateExplorerAPI.create_app_type
    _create_app = CascadeCreateExplorerAPI.create_app
    _create_report = CascadeCreateExplorerAPI.create_report

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
            if app_metadata.get('name'):
                app: Dict = self._create_app(**app_metadata)
            else:  # get the AppType name and use it
                app_metadata.update({'name': app_type_metadata['name']})
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
                    business_id=self.business_id,
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

            app_type_id: str = d['app_type']['id']
            try:
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
    create_business = CascadeCreateExplorerAPI.create_business
    update_business = UpdateExplorerAPI.update_business

    get_business_apps = CascadeExplorerAPI.get_business_apps
    get_business_app_ids = CascadeExplorerAPI.get_business_app_ids
    get_business_all_apps_with_filter = CascadeExplorerAPI.get_business_apps_with_filter

    get_business_reports = CascadeExplorerAPI.get_business_reports
    get_business_report_ids = CascadeExplorerAPI.get_business_report_ids

    delete_business = DeleteExplorerApi.delete_business


class AppTypeExplorerApi:
    """"""
    _create_normalized_name = CreateExplorerAPI._create_normalized_name
    _create_key_name = CreateExplorerAPI._create_key_name

    get_app_type = GetExplorerAPI.get_app_type
    get_universe_app_types = CascadeExplorerAPI.get_universe_app_types
    _find_app_type_by_name_filter = CascadeExplorerAPI.find_app_type_by_name_filter
    create_app_type = CascadeCreateExplorerAPI.create_app_type
    update_app_type = UpdateExplorerAPI.update_app_type

    delete_app_type = DeleteExplorerApi.delete_app_type


class AppExplorerApi:
    _create_normalized_name = CreateExplorerAPI._create_normalized_name
    _create_key_name = CreateExplorerAPI._create_key_name

    get_app = GetExplorerAPI.get_app
    create_app = CascadeCreateExplorerAPI.create_app
    update_app = UpdateExplorerAPI.update_app

    _get_business_apps = CascadeExplorerAPI.get_business_apps
    get_business_apps = CascadeExplorerAPI.get_business_apps
    find_app_by_name_filter = CascadeExplorerAPI.find_app_by_name_filter
    get_app_reports = CascadeExplorerAPI.get_app_reports
    get_app_report_ids = CascadeExplorerAPI.get_app_report_ids
    get_app_path_names = CascadeExplorerAPI.get_app_path_names
    get_app_reports_by_filter = MultiCascadeExplorerAPI.get_app_reports_by_filter
    get_app_by_type = CascadeExplorerAPI.get_app_by_type
    get_app_type = CascadeExplorerAPI.get_app_type
    get_app_by_name = CascadeExplorerAPI.get_app_by_name

    delete_app = DeleteExplorerApi.delete_app


class ReportExplorerApi:

    get_report = GetExplorerAPI.get_report
    get_report_data = GetExplorerAPI.get_report_data
    _get_report_with_data = GetExplorerAPI._get_report_with_data

    _get_app_reports = CascadeExplorerAPI.get_app_reports

    create_report = CascadeCreateExplorerAPI.create_report
    create_app_and_report = MultiCreateApi.create_app_and_report

    update_report = UpdateExplorerAPI.update_report

    get_business_id_by_report = MultiCascadeExplorerAPI.get_business_id_by_report

    delete_report = DeleteExplorerApi.delete_report


class DatasetExplorerApi:

    get_dataset = GetExplorerAPI.get_dataset

    get_dataset_data = CascadeExplorerAPI.get_dataset_data

    create_data_points = CreateExplorerAPI.create_data_points
    create_dataset = CascadeCreateExplorerAPI.create_dataset

    update_dataset = UpdateExplorerAPI.update_dataset

    delete_dataset = DeleteExplorerApi.delete_dataset


class ReportDatasetExplorerApi:

    get_reportdataset = GetExplorerAPI.get_reportdataset
    get_report_datasets = CascadeExplorerAPI.get_report_datasets
    get_report_dataset_data = CascadeExplorerAPI.get_report_dataset_data

    create_reportdataset = CascadeCreateExplorerAPI.create_reportdataset
    create_report_and_dataset = CascadeCreateExplorerAPI.create_report_and_dataset

    update_reportdataset = UpdateExplorerAPI.update_reportdataset

    delete_reportdataset = DeleteExplorerApi.delete_reportdataset
    delete_report_and_dataset = MultiDeleteApi.delete_report_and_dataset


class FileExplorerApi:
    _get_file = GetExplorerAPI.get_file
    get_files = GetExplorerAPI.get_files

    _create_file = CreateExplorerAPI.create_file

    _delete_file = DeleteExplorerApi.delete_file

    _get_business_apps = CascadeExplorerAPI.get_business_apps
    _get_app_by_name = CascadeExplorerAPI.get_app_by_name
    get_business_apps = CascadeExplorerAPI.get_business_apps


class ExplorerApi(
    CascadeCreateExplorerAPI,
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
