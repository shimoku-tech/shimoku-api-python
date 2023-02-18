""""""

from typing import List, Dict, Optional, Any, Union
import json
from time import sleep

from shimoku_api_python.exceptions import ApiClientError
import tqdm

import asyncio
import logging
from shimoku_api_python.execution_logger import logging_before_and_after
logger = logging.getLogger(__name__)


class GetExplorerAPI(object):

    def __init__(self, api_client):
        self.api_client = api_client

    @logging_before_and_after(logging_level=logger.debug)
    async def get_business(self, business_id: str, **kwargs) -> Dict:
        """Retrieve an specific user_id

        :param business_id: user UUID
        """
        endpoint: str = f'business/{business_id}'
        business_data: Dict = await(
            self.api_client.query_element(
                method='GET', endpoint=endpoint, **kwargs
            )
        )
        return business_data

    @logging_before_and_after(logging_level=logger.debug)
    async def get_app_type(self, app_type_id: str, **kwargs) -> Dict:
        """Retrieve an specific app_id metadata

        :param app_type_id: app type UUID
        """
        endpoint: str = f'apptype/{app_type_id}'
        app_type_data: Dict = await(
            self.api_client.query_element(
                method='GET', endpoint=endpoint, **kwargs
            )
        )
        return app_type_data

    @logging_before_and_after(logging_level=logger.debug)
    async def get_app(self, business_id: str, app_id: str, **kwargs) -> Dict:
        """Retrieve an specific app_id metadata

        :param business_id: business UUID
        :param app_id: app UUID
        """
        endpoint: str = f'business/{business_id}/app/{app_id}'
        app_data: Dict = await(
            self.api_client.query_element(
                method='GET', endpoint=endpoint, **kwargs
            )
        )
        return app_data

    # TODO add new data & dataset logic!
    @logging_before_and_after(logging_level=logger.debug)
    async def _get_report_with_data(
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
            report_data: Dict = await (
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

            report_ids_in_app: List[str] = await(
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
                    report_data: Dict = await(
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

    @logging_before_and_after(logging_level=logger.debug)
    async def get_report(
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
        report_data: Dict = await(
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

    @logging_before_and_after(logging_level=logger.debug)
    async def get_dataset(self, business_id: str, dataset_id: str, **kwargs) -> Dict:
        """Retrieve an specific app_id metadata

        :param business_id: business UUID
        :param dataset_id: dataset UUID
        """
        endpoint: str = f'business/{business_id}/dataset/{dataset_id}'
        dataset_data: Dict = await (
            self.api_client.query_element(
                method='GET', endpoint=endpoint, **kwargs
            )
        )
        return dataset_data

    @logging_before_and_after(logging_level=logger.debug)
    async def get_reportdataset(
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
        dataset_data: Dict = await(
            self.api_client.query_element(
                method='GET', endpoint=endpoint, **kwargs
            )
        )
        return dataset_data

# TODO add new data & dataset logic!
    @logging_before_and_after(logging_level=logger.debug)
    async def get_report_data(
        self, business_id: str,
        app_id: Optional[str] = None,
        report_id: Optional[str] = None,
        external_id: Optional[str] = None,
    ) -> List[Dict]:
        """"""
        report: Dict = await self.get_report(
            business_id=business_id,
            app_id=app_id,
            report_id=report_id,
        )

        if report['reportType']:
            report: Dict = await(
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
                await self.api_client.query_element(
                    method='GET', endpoint=endpoint,
                )
            ]
            return report_entries[0]['items']

    @logging_before_and_after(logging_level=logger.debug)
    async def get_file(
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
        file_data: str = await self.api_client.query_element(method='GET', endpoint=endpoint)

        try:
            url: str = file_data['url']
        except KeyError:
            raise KeyError(f'Could not GET file')

        file_object = self.api_client.raw_request(
            **dict(method='GET', url=url)
        )
        return file_object.content

    @logging_before_and_after(logging_level=logger.debug)
    async def get_files(
            self, business_id: Optional[str] = None,
            app_id: Optional[str] = None,
    ) -> List[Dict]:
        """Retrieve an specific file from an app

        :param business_id: business UUID
        :param app_id: Shimoku app UUID (only required if the external_id is provided)
        """
        endpoint: str = f'business/{business_id}/app/{app_id}/files'
        files: List[Dict] = await self.api_client.query_element(method='GET', endpoint=endpoint)
        return files


class CascadeExplorerAPI(GetExplorerAPI):

    def __init__(self, api_client):
        super().__init__(api_client)

    @logging_before_and_after(logging_level=logger.debug)
    async def get_universe_businesses(self) -> List[Dict]:
        endpoint: str = f'businesses'
        return (await self.api_client.query_element(endpoint=endpoint, method='GET'))['items']

    @logging_before_and_after(logging_level=logger.debug)
    async def find_business_by_name_filter(
        self, name: Optional[str] = None,
    ) -> Dict:
        """"""
        businesses: List[Dict] = await self.get_universe_businesses()

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

    @logging_before_and_after(logging_level=logger.debug)
    async def get_universe_app_types(self) -> List[Dict]:
        endpoint: str = f'apptypes'
        return (
            await self.api_client.query_element(
                endpoint=endpoint, method='GET',
            )
        )['items']

    @logging_before_and_after(logging_level=logger.debug)
    async def find_app_type_by_name_filter(
        self, name: Optional[str] = None,
        normalized_name: Optional[str] = None,
    ) -> Dict:
        """"""
        app_types: List[Dict] = await self.get_universe_app_types()

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

    @logging_before_and_after(logging_level=logger.debug)
    async def get_business_apps(self, business_id: str) -> List[Dict]:
        """Given a business retrieve all app metadata

        :param business_id: business UUID
        """
        endpoint: str = f'business/{business_id}/apps'
        apps_raw: Dict = await (
            self.api_client.query_element(
                endpoint=endpoint, method='GET',
            )
        )
        apps: List[Dict] = apps_raw.get('items')

        return apps if apps else []

    @logging_before_and_after(logging_level=logger.debug)
    async def get_business_app_ids(self, business_id: str) -> List[str]:
        """Given a business retrieve all app ids

        :param business_id: business UUID
        """
        apps: Optional[List[Dict]] = await(
            self.get_business_apps(
                business_id=business_id,
            )
        )
        return [app['id'] for app in apps]

    @logging_before_and_after(logging_level=logger.debug)
    async def get_business_all_files(self, business_id) -> List[Dict]:
        """Given a business retrieve all files metadata
        """
        apps: List[Dict] = await self.get_business_apps(business_id=business_id)
        tasks = [self.get_files(business_id=business_id, app_id=app['id']) for app in apps]
        results = await asyncio.gather(*tasks)
        files = []
        for result in results:
            files += result
        return files

    @logging_before_and_after(logging_level=logger.debug)
    async def find_app_by_name_filter(
        self, business_id: str, name: Optional[str] = None,
        normalized_name: Optional[str] = None,
    ) -> Dict:
        """"""
        apps_list: List[Dict] = await self.get_business_apps(business_id=business_id)

        apps = None
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

    @logging_before_and_after(logging_level=logger.debug)
    async def get_app_path_names(self, business_id: str, app_id: str) -> List[str]:
        """Given a Path that belongs to an AppId retrieve all reportId

        :param business_id: business UUID
        :param app_id: app UUID
        """
        reports: List[Dict] = (
            await self.get_app_reports(
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

    @logging_before_and_after(logging_level=logger.debug)
    async def get_app_reports(self, business_id: str, app_id: str) -> List[Dict]:
        """Given an App Id retrieve all reports data from all reports
        that belongs to such App Id.
        """
        endpoint: str = f'business/{business_id}/app/{app_id}/reports'
        reports_raw: Dict = await (
            self.api_client.query_element(
                endpoint=endpoint, method='GET',
            )
        )
        try:
            reports = reports_raw.get('items')
        except AttributeError:
            logger.warning('Reports json should have an "items" field')
            reports = None

        if not reports:
            return []
        return reports

    @logging_before_and_after(logging_level=logger.debug)
    async def get_app_activities(self, business_id: str, app_id: str) -> List[Dict]:
        """Given an App Id retrieve all activities that belong to the App.
        """
        endpoint: str = f'business/{business_id}/app/{app_id}/activities'
        reports_raw: Dict = await (
            self.api_client.query_element(
                endpoint=endpoint, method='GET',
            )
        )
        try:
            activities = reports_raw.get('items')
        except AttributeError:
            logger.warning('Reports json should have an "items" field')
            activities = None

        return activities if activities else []

    @logging_before_and_after(logging_level=logger.debug)
    async def get_app_report_ids(self, business_id: str, app_id: str) -> List[str]:
        """Given an app retrieve all report_id

        :param business_id: business UUID
        :param app_id: app UUID
        """
        reports: List[Dict] = await (
            self.get_app_reports(
                business_id=business_id,
                app_id=app_id,
            )
        )
        return [report['id'] for report in reports]

    @logging_before_and_after(logging_level=logger.debug)
    async def get_business_reports(self, business_id: str) -> List[Dict]:
        """Given a business retrieve all reports

        :param business_id: business UUID
        """
        business_apps = await self.get_business_apps(business_id)
        tasks = [self.get_app_reports(business_id=business_id, app_id=app['id']) for app in business_apps]
        results = await asyncio.gather(*tasks)

        return [report
                for reports_list in results
                for report in reports_list]

    @logging_before_and_after(logging_level=logger.debug)
    async def get_business_report_ids(self, business_id: str) -> List[str]:
        """Given an business retrieve all report_ids

        :param business_id: business UUID
        """
        business_apps = await self.get_business_apps(business_id)
        tasks = [self.get_app_reports(business_id=business_id, app_id=app['id']) for app in business_apps]
        results = await asyncio.gather(*tasks)

        return [report['id']
                for reports_list in results
                for report in reports_list]

    @logging_before_and_after(logging_level=logger.debug)
    async def get_business_activities(self, business_id: str) -> List[Dict]:
        """Given a business retrieve all activities

        :param business_id: business UUID
        """
        business_apps = await self.get_business_apps(business_id)
        tasks = [self.get_app_activities(business_id=business_id, app_id=app['id']) for app in business_apps]
        results = await asyncio.gather(*tasks)

        return [activity
                for activities_list in results
                for activity in activities_list]

    @logging_before_and_after(logging_level=logger.debug)
    async def get_report_datasets(
            self, business_id: str, app_id: str,  report_id: str,
    ) -> List[Dict]:
        endpoint: str = (
            f'business/{business_id}/'
            f'app/{app_id}/'
            f'report/{report_id}/'
            f'reportDataSets'
        )
        reportdatasets: List[Dict] = await (
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
            data_set: Dict = await (
                self.api_client.query_element(
                    endpoint=endpoint, method='GET',
                )
            )
            if data_set.get('reportDataSets'):
                data_sets = data_sets + [data_set]
        return data_sets

    @logging_before_and_after(logging_level=logger.debug)
    async def get_dataset_data(
            self, business_id: str, dataset_id: str,
    ) -> List[Dict]:
        endpoint: str = (
            f'business/{business_id}/'
            f'dataSet/{dataset_id}/'
            f'datas'
        )
        datas_raw: List[Dict] = await (
            self.api_client.query_element(
                endpoint=endpoint, method='GET',
            )
        )
        datas = datas_raw.get('items')
        if not datas:
            return []
        return datas

    @logging_before_and_after(logging_level=logger.debug)
    async def get_report_dataset_data(
            self, business_id: str, app_id: str, report_id: str,
    ) -> List[Dict]:
        """"""
        report_datasets: List[Dict] = await self.get_report_datasets(
            business_id=business_id, app_id=app_id, report_id=report_id,
        )

        tasks = [self.get_dataset_data(business_id=business_id, dataset_id=report_dataset['id'])
                 for report_dataset in report_datasets]

        results = await asyncio.gather(*tasks)

        return [report_dataset_data
                for reports_dataset_data_list in results
                for report_dataset_data in reports_dataset_data_list]

    # TODO pending
    @logging_before_and_after(logging_level=logger.debug)
    def get_report_all_report_entries(self, report_id: str) -> List[str]:
        """Given a report retrieve all reportEntries

        :param report_id: app UUID
        """
        raise NotImplementedError

    @logging_before_and_after(logging_level=logger.debug)
    async def get_path_report_ids(
        self, business_id: str, app_id: str, path_name: str,
    ) -> List[str]:
        """Given an App return all Reports ids that belong to a target path"""
        reports: List[Dict] = await self.get_app_reports(
            business_id=business_id, app_id=app_id,
        )
        path_report_ids: List[str] = []
        for report in reports:
            path: Optional[str] = report.get('path')
            if path == path_name:
                report_id: str = report['id']
                path_report_ids = path_report_ids + [report_id]
        return path_report_ids

    @logging_before_and_after(logging_level=logger.debug)
    async def get_path_reports(
        self, business_id: str, app_id: str, path_name: str,
    ) -> List[Dict]:
        """Given an App return all Reports data that belong to a target path"""
        reports: List[Dict] = await self.get_app_reports(
            business_id=business_id, app_id=app_id,
        )

        path_reports: List[Dict] = []
        for report in reports:
            path: Optional[str] = report.get('path')
            if path == path_name:
                path_reports = path_reports + [report]
        return path_reports

    @logging_before_and_after(logging_level=logger.debug)
    async def get_business_apps_with_filter(
            self, business_id: str, app_filter: Dict
    ) -> List[Dict]:
        """
        """
        apps: List[Dict] = await (
            self.get_business_apps(
                business_id=business_id,
            )
        )
        for app in apps:
            for filter_key, filter_value in app_filter.items():
                if app[filter_key] == filter_value:
                    apps.append(app)
        return apps

    @logging_before_and_after(logging_level=logger.debug)
    async def get_app_reports_by_filter(
        self, app_id: str,
        report_filter: Dict
    ) -> List[Dict]:
        """Having an AppId first retrieve all reportId that belongs
        to the target AppId. Second filter and take the reportId

        # TODO filter example!!
        """
        reports: List[dict] = await (
            self.get_app_reports(
                app_id=app_id,
            )
        )
        reports_res: List[Dict] = []
        for report in reports:
            report: Dict = await self.get_report(report_id=report['id'])
            for filter_key, filter_value in report_filter.items():
                if report[filter_key] == filter_value:
                    reports_res.append(report)
            return reports_res

    @logging_before_and_after(logging_level=logger.debug)
    async def get_app_type_by_name(
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

        app_types: List[Dict] = await self.get_universe_app_types()

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

    @logging_before_and_after(logging_level=logger.debug)
    async def get_app_by_type(
        self, business_id: str, app_type_id: str,
    ) -> Dict:
        """
        :param business_id: business UUID
        :param app_type_id: appType UUID
        """
        apps: List[Dict] = await self.get_business_apps(business_id=business_id)

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

    @logging_before_and_after(logging_level=logger.debug)
    async def get_app_by_name(self, business_id: str, name: str) -> Dict:
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

        apps: List[Dict] = await self.get_business_apps(business_id=business_id)
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
                    app_type: Dict = await self.get_app_type(
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

    @logging_before_and_after(logging_level=logger.debug)
    def __init__(self, api_client):
        self.api_client = api_client
        self.cascade_explorer_api = CascadeExplorerAPI(api_client)

        self._find_business_by_name_filter = self.cascade_explorer_api.find_business_by_name_filter
        self._find_app_type_by_name_filter = self.cascade_explorer_api.find_app_type_by_name_filter

    @logging_before_and_after(logging_level=logger.debug)
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

    @logging_before_and_after(logging_level=logger.debug)
    def _create_key_name(self, name: str) -> str:
        """Having a name create a key

        Example
        ----------------------
        # "name": "Test Borrar"
        # "key": "TEST_BORRAR"
        """
        return '_'.join(name.split(' ')).upper()

    @logging_before_and_after(logging_level=logger.debug)
    async def create_business(self, name: str) -> Dict:
        """"""
        business: Dict = await self._find_business_by_name_filter(name=name)
        if business:
            raise ValueError(f'A Business with the name {name} already exists')

        endpoint: str = 'business'

        item: Dict = {'name': name}

        return await self.api_client.query_element(
            method='POST', endpoint=endpoint, **{'body_params': item},
        )

    @logging_before_and_after(logging_level=logger.debug)
    async def create_app_type(self, name: str) -> Dict:
        """"""
        app_type: Dict = await self._find_app_type_by_name_filter(name=name)
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

        return await self.api_client.query_element(
            method='POST', endpoint=endpoint, **{'body_params': item},
        )

    @logging_before_and_after(logging_level=logger.debug)
    async def create_app(
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

        return await self.api_client.query_element(
            method='POST', endpoint=endpoint, **{'body_params': item},
        )

    @logging_before_and_after(logging_level=logger.debug)
    async def create_report(
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

        report: Dict = await (
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

    @logging_before_and_after(logging_level=logger.debug)
    async def create_dataset(self, business_id: str) -> Dict:
        """Create new DataSet associated to a business

        :param business_id:
        """
        endpoint: str = f'business/{business_id}/dataSet'

        return await self.api_client.query_element(
            method='POST', endpoint=endpoint, **{'body_params': {}},
        )

    @logging_before_and_after(logging_level=logger.debug)
    async def create_reportdataset(
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

        return await self.api_client.query_element(
            method='POST', endpoint=endpoint, **{'body_params': item},
        )

    @logging_before_and_after(logging_level=logger.debug)
    async def create_data_points(
            self, business_id: str, dataset_id: str,
            items: List[str],
    ) -> List[Dict]:
        """Create new row in Data (equivalent to reportEntry)

        :param business_id:
        :param dataset_id:
        :param items:
        """
        # TODO see if this can be batch accelerated like report entries
        endpoint: str = (
            f'business/{business_id}/'
            f'dataSet/{dataset_id}/'
            f'data'
        )

        log_level = logger.getEffectiveLevel()
        data_points_tasks = []
        len_items = len(items)
        with tqdm.tqdm(total=len_items, unit=' data points', disable=(log_level > logging.INFO or len_items < 50)) as progress_bar:
            for item in items:
                data_points_tasks.append(
                    self.api_client.query_element(
                        method='POST', endpoint=endpoint,
                        **{'body_params': item,
                           'progress_bar': (progress_bar, 1)},
                    )
                )
            result = await asyncio.gather(*data_points_tasks)

        return result

    @logging_before_and_after(logging_level=logger.debug)
    async def _create_report_entries(
        self, business_id: str, app_id: str, report_id: str,
        items: List[Dict], batch_size: int = 999,
    ):
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

        log_level = logger.getEffectiveLevel()
        if log_level >= logging.INFO:
            logger.info("Uploading table data")
            print()

        with tqdm.tqdm(total=len(items), unit=' report entries', disable=(log_level > logging.INFO)) as progress_bar:
            query_tasks = []
            for chunk in range(0, len(items), batch_size):
                query_tasks.append(
                    self.api_client.query_element(
                    method='POST', endpoint=endpoint,
                    **{'body_params': items[chunk:chunk + batch_size],
                       'progress_bar': (progress_bar, len(items[chunk:chunk + batch_size]))},
                    )
                )
            if log_level == logging.DEBUG:
                print()
            await asyncio.gather(*query_tasks)

        logger.info("Table data uploaded")

    @logging_before_and_after(logging_level=logger.debug)
    async def create_file(
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

        file_data: str = await(
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

    def __init__(self, api_client):
        super().__init__(api_client)

    @logging_before_and_after(logging_level=logger.debug)
    async def update_business(self, business_id: str, business_data: Dict) -> Dict:
        """"""
        name = business_data.get('name')
        if name:
            business: Dict = await self.find_business_by_name_filter(name=name)
            if business:
                raise ValueError(
                    f'Cannot Update | '
                    f'A Business with the name {name} already exists'
                )

        endpoint: str = f'business/{business_id}'
        return await self.api_client.query_element(
            method='PATCH', endpoint=endpoint, **{'body_params': business_data},
        )

    @logging_before_and_after(logging_level=logger.debug)
    async def update_app_type(self, app_type_id: str, app_type_metadata: Dict) -> Dict:
        """"""
        name = app_type_metadata.get('name')
        if name:
            _app_type: Dict = await self.find_app_type_by_name_filter(name=name)
            if _app_type:
                raise ValueError(
                    f'Cannot Update | '
                    f'A AppType with the name {name} already exists'
                )

        endpoint: str = f'apptype/{app_type_id}'
        return await self.api_client.query_element(
            method='PATCH', endpoint=endpoint, **{'body_params': app_type_metadata},
        )

    @logging_before_and_after(logging_level=logger.debug)
    async def update_app(self, business_id: str, app_id: str, app_metadata: Dict) -> Dict:
        """
        :param business_id:
        :param app_id:
        :param app_metadata: contain the elements to update key
            is the col name and value the value to overwrite
        """
        endpoint: str = f'business/{business_id}/app/{app_id}'
        return await self.api_client.query_element(
            method='PATCH', endpoint=endpoint,
            **{'body_params': app_metadata},
        )

    @logging_before_and_after(logging_level=logger.debug)
    async def update_report(
            self, business_id: str, app_id: str, report_id: str,
            report_metadata: Dict,
    ) -> Dict:
        """"""
        endpoint: str = f'business/{business_id}/app/{app_id}/report/{report_id}'
        return await self.api_client.query_element(
            method='PATCH', endpoint=endpoint,
            **{'body_params': report_metadata},
        )

    @logging_before_and_after(logging_level=logger.debug)
    async def update_reportdataset(
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
        return await self.api_client.query_element(
            method='PATCH', endpoint=endpoint,
            **{'body_params': reportdataset_metadata},
        )

    @logging_before_and_after(logging_level=logger.debug)
    async def update_dataset(
            self, business_id: str, dataset_id: str,
            dataset_metadata: Dict,
    ) -> Dict:
        """"""
        endpoint: str = f'business/{business_id}/dataset/{dataset_id}'
        return await self.api_client.query_element(
            method='PATCH', endpoint=endpoint,
            **{'body_params': dataset_metadata},
        )


class MultiCascadeExplorerAPI(CascadeExplorerAPI):

    def __init__(self, api_client):
        super().__init__(api_client)

    # TODO paginate
    @logging_before_and_after(logging_level=logger.debug)
    async def get_business_paths(self, business_id: str) -> List[str]:
        """Given a business retrieve all path names

        :param business_id: business UUID
        """
        apps: List[Dict] = await self.get_business_apps(business_id=business_id)
        tasks = [self.get_app_paths(app_id=app[id]) for app in apps]

        app_paths = await asyncio.gather(*tasks)

        return [path for paths in app_paths for path in paths]

    # TODO paginate and fix
    @logging_before_and_after(logging_level=logger.debug)
    def get_business_id_by_report(self, report_id: str, **kwargs) -> str:
        """Bottom-up method
        Having a report_id return the app it belongs to
        """
        app_id: str = self.get_app_id_by_report(report_id=report_id, **kwargs)
        business_id: str = self.get_business_id_by_app(app_id=app_id, **kwargs)
        return business_id


class CascadeCreateExplorerAPI(CreateExplorerAPI):

    def __init__(self, api_client):
        super().__init__(api_client)

        self.update_explorer_api = UpdateExplorerAPI(api_client)

        self.update_report = self.update_explorer_api.update_report

    @logging_before_and_after(logging_level=logger.debug)
    async def create_app_from_app_type_normalized_name(self, app_type_name: str) -> Dict:
        """Create AppType and App if required and return the App component
        """
        try:
            app_type: Dict = await self.create_app_type(name=app_type_name)
        except ValueError:  # It already exists then
            app_type: Dict = await(
                self._find_app_type_by_name_filter(name=app_type_name)
            )

        app_type_id: str = app_type['id']
        apps: Dict = await self._get_business_apps(business_id=self.business_id)
        target_apps = [app for app in apps if app['appType']['id'] == app_type_id]

        if not apps:
            app: Dict = await(
                self._create_app(
                    business_id=self.business_id,
                    app_type_id=app_type_id,
                )
            )
        else:
            app: Dict = target_apps[0]
        return app

    @logging_before_and_after(logging_level=logger.debug)
    async def create_report_and_dataset(
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
        report: Dict = await self.create_report(
            business_id=business_id,
            app_id=app_id,
            report_metadata=report_metadata,
            real_time=real_time,
        )

        dataset: Dict = await self.create_dataset(business_id=business_id)
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

        report_dataset: Dict = await self.create_reportdataset(
            business_id=business_id,
            app_id=app_id,
            report_id=report['id'],
            dataset_id=dataset_id,
            dataset_properties=json.dumps(report_dataset_properties),
        )

        data: List[Dict] = await self.create_data_points(
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

        report: Dict = await self.update_report(
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

    @logging_before_and_after(logging_level=logger.debug)
    async def delete_business(self, business_id: str):
        """Delete a Business.
        All apps, reports and data associated with that business is removed by the API
        """
        endpoint: str = f'business/{business_id}'
        await self.api_client.query_element(
            method='DELETE', endpoint=endpoint,
        )

    @logging_before_and_after(logging_level=logger.debug)
    async def delete_app_type(self, app_type_id: str):
        """Delete an appType"""
        endpoint: str = f'apptype/{app_type_id}'
        await self.api_client.query_element(
            method='DELETE', endpoint=endpoint,
        )

    @logging_before_and_after(logging_level=logger.debug)
    async def delete_app(self, business_id: str, app_id: str) -> Dict:
        """Delete an App
        All reports and data associated with that app is removed by the API
        """
        endpoint: str = f'business/{business_id}/app/{app_id}'
        result: Dict = await self.api_client.query_element(
            method='DELETE', endpoint=endpoint
        )
        return result

    @logging_before_and_after(logging_level=logger.debug)
    async def delete_path(self, business_id: str, app_id: str, path_name: str):
        """Delete all Reports in a path
        All data associated with that report is removed by the API"""
        reports: List[Dict] = await(
            self.get_path_reports(
                business_id=business_id,
                app_id=app_id,
                path_name=path_name,
            )
        )
        tasks = [self.delete_report_and_entries(report['id']) for report in reports]
        await asyncio.gather(*tasks)

    @logging_before_and_after(logging_level=logger.debug)
    async def delete_report(
        self, business_id: str, app_id: str, report_id: str,
        relocating: bool = True, delete_data: bool = True,
    ) -> Dict:
        """Delete a Report, relocating reports underneath to avoid errors
        """
        reports: List[Dict] = await(
            self.get_app_reports(
                business_id=business_id,
                app_id=app_id
            )
        )
        target_report: Dict = await self.get_report(
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
                        await self.update_report(
                            business_id=business_id,
                            app_id=app_id, report_id=report_id,
                            report_metadata={'grid': grid},
                        )

        endpoint: str = f'business/{business_id}/app/{app_id}/report/{report_id}'
        result: Dict = await self.api_client.query_element(
            method='DELETE', endpoint=endpoint
        )
        return result

    @logging_before_and_after(logging_level=logger.debug)
    async def delete_reportdataset(
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
        result: Dict = await self.api_client.query_element(
            method='DELETE', endpoint=endpoint
        )
        return result

    @logging_before_and_after(logging_level=logger.debug)
    async def delete_dataset(self, business_id: str, dataset_id: str) -> Dict:
        """"""
        endpoint: str = f'business/{business_id}/dataset/{dataset_id}'
        result: Dict = await self.api_client.query_element(
            method='DELETE', endpoint=endpoint
        )
        return result

    @logging_before_and_after(logging_level=logger.debug)
    async def delete_report_entries(
        self, business_id: str, app_id: str, report_id: str,
    ) -> None:
        """Delete a Report, relocating reports underneath to avoid errors
        """
        report_entries: List[Dict] = await(
            self.get_report_data(
                business_id=business_id,
                app_id=app_id,
                report_id=report_id,
            )
        )

        # Don't use concurrency to not overload the API
        for report_entry in report_entries:
            report_entry_id: str = report_entry['id']
            endpoint: str = (
                f'business/{business_id}/'
                f'app/{app_id}/'
                f'report/{report_id}/'
                f'reportEntry/{report_entry_id}'
            )
            _: Dict = await self.api_client.query_element(
                method='DELETE', endpoint=endpoint
            )

    @logging_before_and_after(logging_level=logger.debug)
    async def delete_file(
        self, business_id: str, app_id: str, file_id: str,
    ) -> Dict:
        """Delete a file
        """
        endpoint: str = f'business/{business_id}/app/{app_id}/file/{file_id}'
        result: Dict = await self.api_client.query_element(method='DELETE', endpoint=endpoint)
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
    def __init__(self, api_client):
        self.api_client = api_client
        self.get_explorer_api = GetExplorerAPI(api_client)
        self.delete_explorer_api = DeleteExplorerApi(api_client)

        self._get_business = self.get_explorer_api.get_business
        self._get_app_type = self.get_explorer_api.get_app_type
        self._get_app = self.get_explorer_api.get_app

        self._delete_business = self.delete_explorer_api.delete_business
        self._delete_app = self.delete_explorer_api.delete_app
        self._delete_app_type = self.delete_explorer_api.delete_app_type
        self._delete_report = self.delete_explorer_api.delete_report
        self._delete_dataset = self.delete_explorer_api.delete_dataset

    @logging_before_and_after(logging_level=logger.debug)
    async def _delete_business_and_app_type(
        self, business_id: str, app_type_id: str
    ):
        try:
            await self._delete_business(business_id)
        except Exception as e_bd:
            raise ValueError(
                f'{e_bd} | Nor Business nor AppType were deleted | ' 
                f'business_id: {business_id} | '
                f'app_type_id: {app_type_id}'
            )

        try:
            _ = await self._get_business(business_id)
        except ApiClientError:
            pass
        except Exception as e_gb:
            raise ValueError(
                f'{e_gb} | Nor Business nor AppType were deleted | '
                f'business_id: {business_id} | app_type_id: {app_type_id}'
            )

        try:
            await self._delete_app_type(app_type_id)
        except ApiClientError:
            return {}
        except Exception as e_atd:
            raise ValueError(
                f'{e_atd} | AppType was not deleted | '
                f'app_type_id: {app_type_id}'
            )

        try:
            _ = await self._get_app_type(app_type_id)
        except ApiClientError:
            return {}
        except Exception as e_atg:
            raise ValueError(
                f'{e_atg} | AppType was not deleted | '
                f'app_type_id: {app_type_id}'
            )

    @logging_before_and_after(logging_level=logger.debug)
    async def delete_report_and_dataset(
            self, business_id: str, app_id: str, report_id: str, dataset_id: str,
    ):
        await asyncio.gather(
            self._delete_report(
                business_id=business_id,
                app_id=app_id,
                report_id=report_id
            ),
            self._delete_dataset(
                business_id=business_id,
                dataset_id=dataset_id
            )
        )


class MultiCreateApi(MultiDeleteApi):
    """If some upper level elements are not created it does it
    """
    def __init__(self, api_client):
        super().__init__(api_client)
        self.cascade_explorer_api = CascadeExplorerAPI(api_client)
        self.cascade_create_explorer_api = CascadeCreateExplorerAPI(api_client)

        self._get_app_type_by_name = self.cascade_explorer_api.get_app_type_by_name
        self._get_universe_app_types = self.cascade_explorer_api.get_universe_app_types
        self._get_app_by_type = self.cascade_explorer_api.get_app_by_type

        self._create_business = self.cascade_create_explorer_api.create_business
        self._create_app_type = self.cascade_create_explorer_api.create_app_type
        self._create_app = self.cascade_create_explorer_api.create_app
        self._create_report = self.cascade_create_explorer_api.create_report

    @logging_before_and_after(logging_level=logger.debug)
    async def create_business_and_app(
        self, app_type_id: str, business_name: str, app_metadata: Dict,
    ) -> Dict[str, Dict]:
        """Create new Report associated to an AppId

        :param app_type_id:
        :param business_name:
        :param app_metadata:
        """
        business: Dict = await self._create_business(name=business_name)
        business_id: str = business['id']

        try:
            app: Dict = await (
                self._create_app(
                    business_id=business_id,
                    app_type_id=app_type_id,
                    app_metadata=app_metadata,
                )
            )
        except Exception as e:
            await self._delete_business(business_id=business_id)
            try:
                _ = await self._get_business(business_id)
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

    @logging_before_and_after(logging_level=logger.debug)
    async def create_app_type_and_app(
        self, business_id: str,
        app_type_metadata: Dict,
        app_metadata: Optional[Dict] = None,
    ) -> Dict[str, Dict]:
        """
        If app_type_id is None we create it
        """
        try:
            app_type: Dict = await self._create_app_type(**app_type_metadata)
        except ValueError:
            app_type_name: str = app_type_metadata['name']
            app_type: Dict = await self._get_app_type_by_name(app_type_name)

        app_type_id: str = app_type['id']
        app_metadata['app_type_id'] = app_type_id
        app_metadata['business_id'] = business_id

        app: Dict = await self._get_app_by_type(
            business_id=business_id,
            app_type_id=app_type_id,
        )
        if not app:
            if not app_metadata.get('name'):
                app_metadata.update({'name': app_type_metadata['name']})  # get the AppType name and use it

            app: Dict = await self._create_app(**app_metadata)

        return {
            'app_type': app_type,
            'app': app
        }

    @logging_before_and_after(logging_level=logger.debug)
    async def create_app_and_report(
        self, business_id: str, app_type_id: str,
        app_metadata: Dict, report_metadata: Dict,
    ) -> Dict:
        """Create new Report associated to an AppId

        :param business_id:
        :param app_type_id:
        :param app_metadata:
        :param report_metadata: A dict with all the values required to create a report
        """
        app: Dict = await(
            self._create_app(
                business_id=business_id,
                app_type_id=app_type_id,
                app_metadata=app_metadata,
            )
        )
        app_id: str = app['id']

        try:
            report: Dict = await(
                self._create_report(
                    business_id=business_id,
                    app_id=app_id,
                    report_metadata=report_metadata,
                )
            )
        except Exception as e:
            raise f'{e} | app_id created: {app_id} | Better delete it'

        return report

    @logging_before_and_after(logging_level=logger.debug)
    async def create_business_app_and_app_type(
        self, business_name: str,
        app_metadata: Dict,
        app_type_metadata: Dict,
    ) -> Dict[str, Dict]:
        """
        """
        app_type: Dict = await self._create_app_type(**app_type_metadata)
        app_type_id: str = app_type['id']
        app_metadata['app_type_id'] = app_type_id

        business: Dict = {}
        try:
            business: Dict = await self._create_business(business_name)
            business_id: str = business['id']
            app_metadata['business_id'] = business_id
        except Exception as e:
            try:
                await self._delete_app_type(app_type_id=app_type_id)
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
            app: Dict = await self._create_app(**app_metadata)
        except Exception as e:
            try:
                await self._delete_business_and_app_type(
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

    @logging_before_and_after(logging_level=logger.debug)
    async def create_business_app_and_report(
        self, app_type_id: str,
        business_name: str,
        app_metadata: Dict,
        report_metadata: Dict,
    ) -> Dict[str, Dict]:
        """
        """
        business: Dict = await self.create_business(business_name)
        business_id: str = business['id']
        app_metadata['business_id'] = business_id
        app_metadata['app_type_id'] = app_type_id

        try:
            app: Dict = await self.create_app(
                business_id=business_id,
                app_metadata=app_metadata,
            )
            app_id = app['id']
        except Exception as e:
            try:
                await self.delete_business(business_id)
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
            report: Dict = await self.create_report(
                business_id=business_id,
                app_id=app_id,
                report_metadata=report_metadata,
            )
        except Exception as e:
            try:
                await self._delete_business_and_app(
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

    @logging_before_and_after(logging_level=logger.debug)
    async def create_business_app_type_app_and_report(
        self, business_name: str,
        app_type_metadata: Dict,
        app_metadata: Dict,
        report_metadata: Dict,
    ) -> Dict[str, Dict]:
        """
        """
        d = await self.create_business_app_and_app_type(
            business_name=business_name,
            app_type_metadata=app_type_metadata,
            app_metadata=app_metadata,
        )
        business_id: str = d['business']['id']
        app_id: str = d['app']['id']

        try:
            report: Dict = await self.create_report(
                business_id=business_id,
                app_id=app_id,
                report_metadata=report_metadata,
            )
        except Exception as e:
            try:
                await self._delete_business_and_app(
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
                await self.delete_app_type(app_type_id)
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
    def __init__(self, api_client):
        self.cascade_explorer_api = CascadeExplorerAPI(api_client)

        self.get_universe_businesses = self.cascade_explorer_api.get_universe_businesses
        self.get_universe_app_types = self.cascade_explorer_api.get_universe_app_types


class BusinessExplorerApi:
    """"""
    def __init__(self, api_client):
        self.get_explorer_api = GetExplorerAPI(api_client)
        self.cascade_explorer_api = CascadeExplorerAPI(api_client)
        self.cascade_create_explorer_api = CascadeCreateExplorerAPI(api_client)
        self.update_explorer_api = UpdateExplorerAPI(api_client)
        self.delete_explorer_api = DeleteExplorerApi(api_client)

        self.get_business = self.get_explorer_api.get_business
        self.get_universe_businesses = self.cascade_explorer_api.get_universe_businesses
        self._find_business_by_name_filter = self.cascade_explorer_api.find_business_by_name_filter
        self.create_business = self.cascade_create_explorer_api.create_business
        self.update_business = self.update_explorer_api.update_business

        self.get_business_activities = self.cascade_explorer_api.get_business_activities
        self.get_business_apps = self.cascade_explorer_api.get_business_apps
        self.get_business_app_ids = self.cascade_explorer_api.get_business_app_ids
        self.get_business_all_apps_with_filter = self.cascade_explorer_api.get_business_apps_with_filter

        self.get_business_reports = self.cascade_explorer_api.get_business_reports
        self.get_business_report_ids = self.cascade_explorer_api.get_business_report_ids

        self.delete_business = self.delete_explorer_api.delete_business


class AppTypeExplorerApi:
    """"""
    def __init__(self, api_client):
        self.create_explorer_api = CreateExplorerAPI(api_client)
        self.get_explorer_api = GetExplorerAPI(api_client)
        self.cascade_explorer_api = CascadeExplorerAPI(api_client)
        self.cascade_create_explorer_api = CascadeCreateExplorerAPI(api_client)
        self.update_explorer_api = UpdateExplorerAPI(api_client)
        self.delete_explorer_api = DeleteExplorerApi(api_client)

        self._create_normalized_name = self.create_explorer_api._create_normalized_name
        self._create_key_name = self.create_explorer_api._create_key_name

        self.get_app_type = self.get_explorer_api.get_app_type
        self.get_universe_app_types = self.cascade_explorer_api.get_universe_app_types
        self._find_app_type_by_name_filter = self.cascade_explorer_api.find_app_type_by_name_filter
        self.create_app_type = self.cascade_create_explorer_api.create_app_type
        self.update_app_type = self.update_explorer_api.update_app_type

        self.delete_app_type = self.delete_explorer_api.delete_app_type


class AppExplorerApi:
    def __init__(self, api_client):
        self.create_explorer_api = CreateExplorerAPI(api_client)
        self.get_explorer_api = GetExplorerAPI(api_client)
        self.cascade_explorer_api = CascadeExplorerAPI(api_client)
        self.multi_cascade_explorer_api = MultiCascadeExplorerAPI(api_client)
        self.cascade_create_explorer_api = CascadeCreateExplorerAPI(api_client)
        self.update_explorer_api = UpdateExplorerAPI(api_client)
        self.delete_explorer_api = DeleteExplorerApi(api_client)

        self._create_normalized_name = self.create_explorer_api._create_normalized_name
        self._create_key_name = self.create_explorer_api._create_key_name

        self.get_app = self.get_explorer_api.get_app
        self.create_app = self.cascade_create_explorer_api.create_app
        self.update_app = self.update_explorer_api.update_app

        self._get_business_apps = self.cascade_explorer_api.get_business_apps
        self.get_business_apps = self.cascade_explorer_api.get_business_apps
        self.find_app_by_name_filter = self.cascade_explorer_api.find_app_by_name_filter
        self.get_app_reports = self.cascade_explorer_api.get_app_reports
        self.get_app_report_ids = self.cascade_explorer_api.get_app_report_ids
        self.get_app_path_names = self.cascade_explorer_api.get_app_path_names
        self.get_app_reports_by_filter = self.multi_cascade_explorer_api.get_app_reports_by_filter
        self.get_app_by_type = self.cascade_explorer_api.get_app_by_type
        self.get_app_type = self.cascade_explorer_api.get_app_type
        self.get_app_by_name = self.cascade_explorer_api.get_app_by_name

        self.delete_app = self.delete_explorer_api.delete_app


class ReportExplorerApi:
    def __init__(self, api_client):

        self.get_explorer_api = GetExplorerAPI(api_client)
        self.cascade_explorer_api = CascadeExplorerAPI(api_client)
        self.multi_cascade_explorer_api = MultiCascadeExplorerAPI(api_client)
        self.multi_create_api = MultiCreateApi(api_client)
        self.cascade_create_explorer_api = CascadeCreateExplorerAPI(api_client)
        self.update_explorer_api = UpdateExplorerAPI(api_client)
        self.delete_explorer_api = DeleteExplorerApi(api_client)

        self.get_report = self.get_explorer_api.get_report
        self.get_report_data = self.get_explorer_api.get_report_data
        self._get_report_with_data = self.get_explorer_api._get_report_with_data

        self._get_app_reports = self.cascade_explorer_api.get_app_reports

        self.create_report = self.cascade_create_explorer_api.create_report
        self.create_app_and_report = self.multi_create_api.create_app_and_report

        self.update_report = self.update_explorer_api.update_report

        self.get_business_id_by_report = self.multi_cascade_explorer_api.get_business_id_by_report

        self.delete_report = self.delete_explorer_api.delete_report


class DatasetExplorerApi:
    def __init__(self, api_client):
        self.create_explorer_api = CreateExplorerAPI(api_client)
        self.get_explorer_api = GetExplorerAPI(api_client)
        self.cascade_explorer_api = CascadeExplorerAPI(api_client)
        self.cascade_create_explorer_api = CascadeCreateExplorerAPI(api_client)
        self.update_explorer_api = UpdateExplorerAPI(api_client)
        self.delete_explorer_api = DeleteExplorerApi(api_client)

        self.get_dataset = self.get_explorer_api.get_dataset

        self.get_dataset_data = self.cascade_explorer_api.get_dataset_data

        self.create_data_points = self.create_explorer_api.create_data_points
        self.create_dataset = self.cascade_create_explorer_api.create_dataset

        self.update_dataset = self.update_explorer_api.update_dataset

        self.delete_dataset = self.delete_explorer_api.delete_dataset


class ReportDatasetExplorerApi:
    def __init__(self, api_client):
        self.get_explorer_api = GetExplorerAPI(api_client)
        self.cascade_explorer_api = CascadeExplorerAPI(api_client)
        self.cascade_create_explorer_api = CascadeCreateExplorerAPI(api_client)
        self.update_explorer_api = UpdateExplorerAPI(api_client)
        self.delete_explorer_api = DeleteExplorerApi(api_client)
        self.multi_delete_explorer_api = MultiDeleteApi(api_client)

        self.get_reportdataset = self.get_explorer_api.get_reportdataset
        self.get_report_datasets = self.cascade_explorer_api.get_report_datasets
        self.get_report_dataset_data = self.cascade_explorer_api.get_report_dataset_data

        self.create_reportdataset = self.cascade_create_explorer_api.create_reportdataset
        self.create_report_and_dataset = self.cascade_create_explorer_api.create_report_and_dataset

        self.update_reportdataset = self.update_explorer_api.update_reportdataset

        self.delete_reportdataset = self.delete_explorer_api.delete_reportdataset
        self.delete_report_and_dataset = self.multi_delete_explorer_api.delete_report_and_dataset


class FileExplorerApi:
    def __init__(self, api_client):
        self.create_explorer_api = CreateExplorerAPI(api_client)
        self.get_explorer_api = GetExplorerAPI(api_client)
        self.cascade_explorer_api = CascadeExplorerAPI(api_client)
        self.delete_explorer_api = DeleteExplorerApi(api_client)

        self._get_file = self.get_explorer_api.get_file
        self.get_files = self.get_explorer_api.get_files

        self._create_file = self.create_explorer_api.create_file

        self._delete_file = self.delete_explorer_api.delete_file

        self._get_business_apps = self.cascade_explorer_api.get_business_apps
        self._get_app_by_name = self.cascade_explorer_api.get_app_by_name
        self.get_business_apps = self.cascade_explorer_api.get_business_apps


class ExplorerApi(
    CascadeCreateExplorerAPI,
    DeleteExplorerApi,
):
    """Get Businesses, Apps, Paths and Reports in any possible combination
    """

    def __init__(self, api_client):
        super().__init__(api_client)

    # TODO WiP
    @logging_before_and_after(logging_level=logger.debug)
    async def has_app_report_data(self, business_id: str, app_id: str) -> bool:
        """"""
        report_ids: List[str] = await self.get_app_report_ids(
            business_id=business_id, app_id=app_id
        )
        for report_id in report_ids:
            result: bool = await self.has_report_report_entries(report_id)
            if result:
                return True
        return False

    # TODO WiP
    @logging_before_and_after(logging_level=logger.debug)
    async def has_path_data(self, business_id: str, app_id: str, path_name: str) -> bool:
        """"""
        report_ids: List[str] = await self.get_app_report_ids(
            business_id=business_id, app_id=app_id
        )
        for report_id in report_ids:
            result: bool = await self.has_report_report_entries(report_id)
            if result:
                return True
        return False
