""""""
from typing import List, Dict
import datetime as dt

from src.shimoku_api_python.templates.shimoku_backoffice import (
    set_report_detail, set_apps_detail, set_app_type_detail,
    set_business_detail, set_overview_page,
)


class TemplateApi:
    """
    """

    def __init__(self, api_client):
        self.api_client = api_client

    def shimoku_backoffice(self):
        menu_path_seed: str = 'shimoku-backoffice'
        businesses: List[Dict] = self.universe.get_universe_businesses()

        bo_business = [
            business for business in businesses
            if business['name'] == menu_path_seed
        ]
        if not bo_business:
            bo_business = s.business.create_business(name=menu_path_seed)
        else:
            bo_business = bo_business[0]
        business_id = bo_business['id']
        s.plt.set_business(business_id)

        app_types: List[Dict] = self.universe.get_universe_app_types()

        apps: List[Dict] = []
        for business in businesses:
            apps_temp: List[Dict] = self.business.get_business_apps(business['id'])
            apps = apps + apps_temp

        reports: List[Dict] = []
        for app in apps:
            reports_temp = self.app.get_app_reports(
                business_id=app['appBusinessId'],
                app_id=app['id'],
            )
            reports = reports + reports_temp

        print('Note - It takes about 5 minutes to process')
        start_time = dt.datetime.now()
        print(f'Start time {start_time}')
        set_report_detail()
        print('report detail created')
        set_apps_detail()
        print('apps detail created')
        set_app_type_detail()
        print('apptype detail created')
        set_business_detail()
        print('business detail created')
        set_overview_page()
        print('overview created')
        end_time = dt.datetime.now()
        print(f'End time {end_time}')
        print(f'Execution time: {end_time - start_time}')
