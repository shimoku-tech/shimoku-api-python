import unittest
from os import getenv
from tenacity import RetryError
from utils import initiate_shimoku

s = initiate_shimoku()
business_id: str = getenv('BUSINESS_ID')
mock: bool = getenv('MOCK') == 'TRUE'


class TestReport(unittest.TestCase):
    def test_get_report(self):
        s.set_workspace(uuid=business_id)
        s.set_menu_path('Report test path')

        s.plt.clear_menu_path()
        s.plt.html(html='<h1>test</h1>', order=0)

        report = s.menu_paths.get_menu_path_components(name='Report test path')[0]

        assert s.components.get_component(uuid=report['id'])

        s.components.delete_component(uuid=report['id'])

        if not mock:
            with self.assertRaises(RetryError):
                s.components.get_component(uuid=report['id'])

