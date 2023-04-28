from os import getenv
import shimoku_api_python as shimoku
from tenacity import RetryError
from shimoku_api_python.exceptions import CacheError
import unittest
import asyncio

api_key: str = getenv('API_TOKEN')
universe_id: str = getenv('UNIVERSE_ID')
business_id: str = getenv('BUSINESS_ID')
environment: str = getenv('ENVIRONMENT')
verbose: str = getenv('VERBOSITY')
async_execution: bool = getenv('ASYNC_EXECUTION') == 'TRUE'


s = shimoku.Client(
    access_token=api_key,
    universe_id=universe_id,
    environment=environment,
    verbosity=verbose,
    async_execution=async_execution,
    business_id=business_id,
)


def delete_dashboard_if_exists(name):
    if s.dashboard.get_dashboard(name=name):
        s.dashboard.force_delete_dashboard(name=name)


class TestDashboardMetadataApi(unittest.TestCase):

    def test_dashboard_CRUD(self):
        name = 'Testing dashboard CRUD'
        delete_dashboard_if_exists(name)
        delete_dashboard_if_exists(name + ' updated')

        dashboard = s.dashboard.create_dashboard(name=name)

        assert dashboard['name'] == name

        dashboard = s.dashboard.get_dashboard(uuid=dashboard['id'])
        assert dashboard['name'] == name

        s.dashboard.update_dashboard(uuid=dashboard['id'], new_name=name + ' updated')

        dashboard = s.dashboard.get_dashboard(uuid=dashboard['id'])
        assert dashboard['name'] == name+' updated'

        assert s.dashboard.create_dashboard(name=name)
        with self.assertRaises(CacheError):
            s.dashboard.create_dashboard(name=name)
        with self.assertRaises(CacheError):
            s.dashboard.create_dashboard(name=name + ' updated')

        s.dashboard.delete_dashboard(name=name)
        s.dashboard.delete_dashboard(name=name+' updated')

        assert not s.dashboard.get_dashboard(name=name)
        assert not s.dashboard.get_dashboard(name=name + ' updated')

    def test_create_and_delete_app_dashboard_link(self):
        name = 'Testing dashboard for appdashboards'

        app_name = 'Testing app'
        s.app.delete_app(uuid=s.app.get_app(menu_path=app_name)['id'])

        delete_dashboard_if_exists(name)
        delete_dashboard_if_exists(name + ' updated')

        s.dashboard.create_dashboard(name=name)
        app_id = s.app.get_app(menu_path=app_name)['id']

        s.dashboard.add_app_in_dashboard(name=name, app_id=app_id)

        app_ids = s.dashboard.get_dashboard_app_ids(name=name)
        assert app_id == app_ids[0]

        with self.assertRaises(RetryError):
            s.dashboard.delete_dashboard(name=name)

        s.dashboard.remove_app_from_dashboard(name=name, app_id=app_id)
        s.dashboard.delete_dashboard(name=name)
        s.app.delete_app(uuid=app_id)

    def test_delete_all_app_dashboards_links(self):
        name = 'Testing dashboard for appdashboards delete all'

        app_names = ['Testing app 1', 'Testing app 2', 'Testing app 3']

        for app_name in app_names:
            s.app.delete_app(uuid=s.app.get_app(menu_path=app_name)['id'])

        delete_dashboard_if_exists(name)

        app_ids = []
        s.dashboard.create_dashboard(name=name)
        for app_name in app_names:
            app_id = s.app.get_app(menu_path=app_name)['id']
            s.dashboard.add_app_in_dashboard(name=name, app_id=app_id)
            app_ids.append(app_id)

        dashboard_app_ids = s.dashboard.get_dashboard_app_ids(name=name)
        assert len(dashboard_app_ids) == len(app_names)

        s.dashboard.remove_all_apps_from_dashboard(name=name)

        dashboard_app_ids = s.dashboard.get_dashboard_app_ids(name=name)
        assert len(dashboard_app_ids) == 0

        for app_id in app_ids:
            s.dashboard.add_app_in_dashboard(name=name, app_id=app_id)

        s.dashboard.force_delete_dashboard(name=name)

        assert not s.dashboard.get_dashboard(name=name)

        for app_id in app_ids:
            s.app.delete_app(uuid=app_id)

    def test_group_apps(self):
        name = 'Testing dashboard for grouping apps'

        app_names = ['Testing app 1', 'Testing app 2', 'Testing app 3']

        for app_name in app_names:
            s.app.delete_app(uuid=s.app.get_app(menu_path=app_name)['id'])

        delete_dashboard_if_exists(name)

        app_ids = []
        s.dashboard.create_dashboard(name=name)
        for app_name in app_names:
            app_id = s.app.get_app(menu_path=app_name)['id']
            app_ids.append(app_id)

        s.dashboard.group_apps(menu_paths=app_names, name=name)
        dashboard_app_ids = s.dashboard.get_dashboard_app_ids(name=name)

        for app_id, app_name in zip(app_ids, app_names):
            assert app_id in dashboard_app_ids
            s.dashboard.remove_app_from_dashboard(menu_path=app_name, name=name)
            dashboard_app_ids.remove(app_id)

        assert len(dashboard_app_ids) == 0

        s.dashboard.group_apps(app_ids=app_ids, name=name)
        dashboard_app_ids = s.dashboard.get_dashboard_app_ids(name=name)

        for app_id, app_name in zip(app_ids, app_names):
            assert app_id in dashboard_app_ids
            s.dashboard.remove_app_from_dashboard(menu_path=app_name, name=name)
            dashboard_app_ids.remove(app_id)

        assert len(dashboard_app_ids) == 0

        all_app_ids = s.business.get_business_app_ids(uuid=business_id)

        s.dashboard.group_apps(menu_paths='all', name=name)
        dashboard_app_ids = s.dashboard.get_dashboard_app_ids(name=name)

        for app_id in all_app_ids:
            assert app_id in dashboard_app_ids
            s.dashboard.remove_app_from_dashboard(app_id=app_id, name=name)
            dashboard_app_ids.remove(app_id)

        assert len(dashboard_app_ids) == 0

        s.dashboard.delete_dashboard(name=name)

        assert not s.dashboard.get_dashboard(name=name)

        for app_id in app_ids:
            s.app.delete_app(uuid=app_id)



