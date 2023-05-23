from os import getenv
import unittest

import shimoku_api_python as shimoku
from tenacity import RetryError


api_key: str = getenv('API_TOKEN')
universe_id: str = getenv('UNIVERSE_ID')
business_id: str = getenv('BUSINESS_ID')
environment: str = getenv('ENVIRONMENT')

config = {
    'access_token': api_key,
}

s = shimoku.Client(
    config=config,
    universe_id=universe_id,
    environment=environment,
    verbosity='DEBUG',
)
s.set_business(uuid=business_id)
s.set_menu_path('Report test path')
s.plt.clear_menu_path()
s.plt.html(html='<h1>test</h1>', order=0)
report = s.app.get_app_reports(menu_path='Report test path')[0]


def test_get_report():
    assert s.report.get_report(uuid=report['id'])


def test_delete_report():
    s.report.delete_report(uuid=report['id'])

    class MyTestCase(unittest.TestCase):
        def check_report_not_exists(self):
            with self.assertRaises(RetryError):
                s.report.get_report(uuid=report['id'])

    t = MyTestCase()
    t.check_report_not_exists()


test_get_report()
test_delete_report()
