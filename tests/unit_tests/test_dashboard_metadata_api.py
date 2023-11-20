from os import getenv
from tenacity import RetryError
from shimoku_api_python.exceptions import CacheError
import unittest
from utils import initiate_shimoku

s = initiate_shimoku()

business_id: str = getenv('BUSINESS_ID')
environment: str = getenv('ENVIRONMENT')
mock: bool = getenv('MOCK') == 'TRUE'
playground: bool = getenv('PLAYGROUND') == 'TRUE'

s.set_workspace(uuid=business_id)


def delete_dashboard_if_exists(name):
    if s.boards.get_board(name=name):
        s.boards.force_delete_board(name=name)


class TestDashboardMetadataApi(unittest.TestCase):

    def test_dashboard_CRUD(self):
        name = 'Testing dashboard CRUD'
        delete_dashboard_if_exists(name)
        delete_dashboard_if_exists(name + ' updated')

        dashboard = s.boards.create_board(name=name)

        assert dashboard['name'] == name

        dashboard = s.boards.get_board(uuid=dashboard['id'])
        assert dashboard['name'] == name

        s.boards.update_board(uuid=dashboard['id'], new_name=name + ' updated', is_public=True)

        dashboard = s.boards.get_board(uuid=dashboard['id'])
        assert dashboard['name'] == name+' updated'

        assert s.boards.create_board(name=name)
        with self.assertRaises(CacheError):
            s.boards.create_board(name=name)
        with self.assertRaises(CacheError):
            s.boards.create_board(name=name + ' updated')

        s.boards.delete_board(name=name)
        s.boards.delete_board(name=name + ' updated')

        assert not s.boards.get_board(name=name)
        assert not s.boards.get_board(name=name + ' updated')

    def test_create_and_delete_app_dashboard_link(self):
        name = 'Testing dashboard for appdashboards'

        app_name = 'Testing app'
        s.menu_paths.delete_menu_path(uuid=s.menu_paths.get_menu_path(name=app_name)['id'])

        delete_dashboard_if_exists(name)
        delete_dashboard_if_exists(name + ' updated')

        s.boards.create_board(name=name)
        app_id = s.menu_paths.get_menu_path(name=app_name)['id']

        s.boards.add_menu_path_in_board(name=name, menu_path_id=app_id)

        app_ids = s.boards.get_board_menu_path_ids(name=name)
        assert app_id == app_ids[0]

        if not mock and not playground:
            with self.assertRaises(RetryError):
                s.boards.delete_board(name=name)

        s.boards.remove_menu_path_from_board(name=name, menu_path_id=app_id)
        s.boards.delete_board(name=name)
        s.menu_paths.delete_menu_path(uuid=app_id)

    def test_delete_all_app_dashboards_links(self):
        name = 'Testing dashboard for appdashboards delete all'

        app_names = ['Testing app 1', 'Testing app 2', 'Testing app 3']

        for app_name in app_names:
            s.menu_paths.delete_menu_path(uuid=s.menu_paths.get_menu_path(name=app_name)['id'])

        delete_dashboard_if_exists(name)

        app_ids = []
        s.boards.create_board(name=name)
        for app_name in app_names:
            app_id = s.menu_paths.get_menu_path(name=app_name)['id']
            s.boards.add_menu_path_in_board(name=name, menu_path_id=app_id)
            app_ids.append(app_id)

        dashboard_app_ids = s.boards.get_board_menu_path_ids(name=name)
        assert len(dashboard_app_ids) == len(app_names)

        s.boards.remove_all_menu_paths_from_board(name=name)

        dashboard_app_ids = s.boards.get_board_menu_path_ids(name=name)
        assert len(dashboard_app_ids) == 0

        for app_id in app_ids:
            s.boards.add_menu_path_in_board(name=name, menu_path_id=app_id)

        s.boards.force_delete_board(name=name)

        assert not s.boards.get_board(name=name)

        for app_id in app_ids:
            s.menu_paths.delete_menu_path(uuid=app_id)

    def test_group_apps(self):
        name = 'Testing dashboard for grouping apps'

        app_names = ['Testing app 1', 'Testing app 2', 'Testing app 3']

        for app_name in app_names:
            s.menu_paths.delete_menu_path(uuid=s.menu_paths.get_menu_path(name=app_name)['id'])

        delete_dashboard_if_exists(name)

        app_ids = []
        s.boards.create_board(name=name)
        for app_name in app_names:
            app_id = s.menu_paths.get_menu_path(name=app_name)['id']
            app_ids.append(app_id)

        s.boards.group_menu_paths(menu_path_names=app_names, name=name)
        dashboard_app_ids = s.boards.get_board_menu_path_ids(name=name)

        for app_id, app_name in zip(app_ids, app_names):
            assert app_id in dashboard_app_ids
            s.boards.remove_menu_path_from_board(menu_path_name=app_name, name=name)
            dashboard_app_ids.remove(app_id)

        assert len(dashboard_app_ids) == 0

        s.boards.group_menu_paths(menu_path_ids=app_ids, name=name)
        dashboard_app_ids = s.boards.get_board_menu_path_ids(name=name)

        for app_id, app_name in zip(app_ids, app_names):
            assert app_id in dashboard_app_ids
            s.boards.remove_menu_path_from_board(menu_path_name=app_name, name=name)
            dashboard_app_ids.remove(app_id)

        assert len(dashboard_app_ids) == 0

        all_app_ids = s.workspaces.get_workspace_menu_path_ids(uuid=business_id)

        s.boards.group_menu_paths(menu_path_names='all', name=name)
        dashboard_app_ids = s.boards.get_board_menu_path_ids(name=name)

        for app_id in all_app_ids:
            assert app_id in dashboard_app_ids
            s.boards.remove_menu_path_from_board(menu_path_id=app_id, name=name)
            dashboard_app_ids.remove(app_id)

        assert len(dashboard_app_ids) == 0

        s.boards.delete_board(name=name)

        assert not s.boards.get_board(name=name)

        for app_id in app_ids:
            s.menu_paths.delete_menu_path(uuid=app_id)



