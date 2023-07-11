""""""
from os import getenv
from typing import Dict, List
import unittest

from shimoku_api_python.exceptions import MenuPathError
from tenacity import RetryError
from utils import initiate_shimoku

s = initiate_shimoku()
mock: bool = getenv('MOCK') == 'TRUE'
business_id: str = getenv('BUSINESS_ID')
s.set_workspace(uuid=business_id)

app_name = 'Main test app'
s.set_menu_path(app_name, 'test')
s.plt.html(html='<h1>test</h1>', order=0)


# Check it does not exists anymore
class TestApp(unittest.TestCase):
    def check_app_not_exists(self, _app_id: str):
        if mock:
            return
        with self.assertRaises(RetryError):
            s.menu_paths.get_menu_path(uuid=_app_id)

    def test_get_app(self):
        app_id = s.menu_paths.get_menu_path(name=app_name)['id']
        app: Dict = s.menu_paths.get_menu_path(uuid=app_id)
        assert app

    def test_get_fake_app(self):
        if not mock:
            with self.assertRaises(RetryError):
                app_id: str = 'this is a test'
                s.menu_paths.get_menu_path(uuid=app_id)

    def test_update_app(self):
        """Set the updatedAt field of an App to '2000-01-01'
        Then revert the updatedAt to its original value
        """
        app: Dict = s.menu_paths.get_menu_path(name=app_name)
        app_id: str = app['id']
        old_vals = dict(
            hide_title=app['hideTitle'],
            hide_path=app['hidePath'],
            show_breadcrumb=app['showBreadcrumb'],
            show_history_navigation=app['showHistoryNavigation'],
        )

        new_vals = dict(
            hide_title=True,
            hide_path=True,
            show_breadcrumb=True,
            show_history_navigation=True,
        )
        s.menu_paths.update_menu_path(uuid=app_id, **new_vals)
        app_updated: Dict = s.menu_paths.get_menu_path(uuid=app_id)

        assert app_updated['hideTitle']
        assert app_updated['hidePath']
        assert app_updated['showBreadcrumb']
        assert app_updated['showHistoryNavigation']

        #########
        # Revert the change
        #########
        s.menu_paths.update_menu_path(uuid=app_id, **old_vals)
        app_reverted: Dict = s.menu_paths.get_menu_path(uuid=app_id)

        assert app_reverted['hideTitle'] == old_vals['hide_title']
        assert app_reverted['hidePath'] == old_vals['hide_path']
        assert app_reverted['showBreadcrumb'] == old_vals['show_breadcrumb']
        assert app_reverted['showHistoryNavigation'] == old_vals['show_history_navigation']

    def test_create_and_delete_app(self):
        s.menu_paths.get_menu_path(name='auto-test')
        s.menu_paths.delete_menu_path(name='auto-test')

        app: Dict = s.menu_paths.get_menu_path(name='auto-test')

        assert app

        result: Dict = s.menu_paths.delete_menu_path(name='auto-test')

        assert result

        self.check_app_not_exists(app['id'])

    def test_get_app_reports(self):
        reports: List[Dict] = s.menu_paths.get_menu_path_components(name=app_name)
        assert reports
        assert reports[0]

    def test_get_app_report_ids(self):
        report_ids: List[str] = [r['id'] for r in s.menu_paths.get_menu_path_components(name=app_name)]
        assert report_ids
        assert len(report_ids[0]) > 0
        assert isinstance(report_ids[0], str)

    def test_get_app_path_names(self):
        path_names: List[str] = s.menu_paths.get_menu_path_sub_paths(name=app_name)
        assert path_names

    def test_get_app_activities(self):
        s.set_menu_path(app_name)
        for activity in s.menu_paths.get_menu_path_activities(name=app_name):
            s.activities.delete_activity(uuid=activity['id'])

        for i in range(3):
            s.activities.create_activity(name=f'auto-test-activity {i}')

        activities: List[Dict] = s.menu_paths.get_menu_path_activities(name=app_name)

        assert len(activities) == 3
        for activity in activities:
            assert activity['name'].startswith('auto-test-activity')

        s.menu_paths.delete_all_menu_path_activities(name=app_name)

        activities: List[Dict] = s.menu_paths.get_menu_path_activities(name=app_name)

        assert len(activities) == 0

    def test_rename_app(self):
        new_name: str = 'auto-test'
        s.menu_paths.update_menu_path(name=app_name, new_name=new_name)
        app: Dict = s.menu_paths.get_menu_path(name=new_name)

        assert app['name'] == new_name

        s.menu_paths.update_menu_path(name=new_name, new_name=app_name)
        app: Dict = s.menu_paths.get_menu_path(name=app_name)

        assert app['name'] == app_name
        self.delete_path()

    def delete_path(self):
        if not mock:
            with self.assertRaises(MenuPathError):
                s.menu_paths.delete_menu_path(name=app_name)

        s.pop_out_of_menu_path()
        s.menu_paths.delete_menu_path(name=app_name)
