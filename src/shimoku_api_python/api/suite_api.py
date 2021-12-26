""""""
from typing import List, Dict
import datetime as dt

from src.shimoku_api_python.templates.shimoku_backoffice import (
    set_report_detail, set_apps_detail, set_app_type_detail,
    set_business_detail, set_overview_page,
)


class SuiteApi:
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
            bo_business = self.businesself.create_business(name=menu_path_seed)
        else:
            bo_business = bo_business[0]
        business_id = bo_business['id']
        self.plt.set_business(business_id)

        app_types: List[Dict] = self.universe.get_universe_app_types()

        apps: List[Dict] = []
        for business in businesses:
            apps_temp: List[Dict] = self.businesself.get_business_apps(business['id'])
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
        set_report_detail(
            shimoku=self,
            menu_path_seed=menu_path_seed,
            reports=reports,
        )
        print('report detail created')
        set_apps_detail(
            shimoku=self,
            menu_path_seed=menu_path_seed,
            apps=apps,
            reports=reports,
        )
        print('apps detail created')
        set_app_type_detail(
            shimoku=self,
            menu_path_seed=menu_path_seed,
            app_types=app_types,
            apps=apps,
        )
        print('apptype detail created')
        set_business_detail(
            shimoku=self,
            menu_path_seed=menu_path_seed,
            businesses=businesses,
            apps=apps,
        )
        print('business detail created')
        set_overview_page(
            shimoku=self,
            menu_path_seed=menu_path_seed,
            businesses=businesses,
            app_types=app_types,
            apps=apps,
            reports=reports,
        )
        print('overview created')
        end_time = dt.datetime.now()
        print(f'End time {end_time}')
        print(f'Execution time: {end_time - start_time}')

    def cohorts(self):
        raise NotImplementedError

    def predictive_cohorts(self):
        raise NotImplementedError

    def retention(self):
        """Create the Retention Suite"""

        # TODO this two methods will always be created for suites
        def get_predictions():
            """Return the table of Retention Suite with users in churn"""
            raise NotImplementedError

        def connect_predictions():
            """Connect predictions to third party tools
            such as Hubspot, Klaviyo or Mailchimp"""
            raise NotImplementedError

        raise NotImplementedError
