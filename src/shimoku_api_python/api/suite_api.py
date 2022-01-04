""""""
from typing import List, Dict, Union, Optional, Callable
import datetime as dt

from pandas import DataFrame

from .templates.shimoku_backoffice import (
    set_report_detail, set_apps_detail, set_app_type_detail,
    set_business_detail, set_overview_page,
)
from .templates.charts_catalog import (
    create_bar, create_pie, create_html,
    create_line, create_tree, create_table,
    create_gauge, create_radar, create_funnel,
    create_iframe, create_sankey, create_scatter,
    create_heatmap, create_treemap, create_themeriver,
    create_sunburst, create_stockline, create_indicator,
    create_alert_indicator, create_predictive_line
)


class SuiteApi:
    """
    """

    def __init__(self, api_client):
        self.api_client = api_client

    def get_predictions(self, suite: str):
        """
        :param suite: for example 'retention' the name of the suite
         to get data from. In that case return the table of the
         Retention Suite with users in churn
        """
        # TODO first check that the specified suite exists
        # TODO for every suite the report to retrieve will be different
        raise NotImplementedError

    def get_prediction_performance(self, suite: str):
        """
        :param suite: for example 'retention' the name of the suite
         to get data from. In that case return the results table
         of the Retention Suite
        """
        # TODO first check that the specified suite exists
        # TODO for every suite the report to retrieve will be different
        raise NotImplementedError

    def connect_predictions(self, suite: str, third_party_tool: str):
        """Connect predictions to third party tools
        such as Hubspot, Klaviyo or Mailchimp

        :param suite: for example 'retention' the name of the suite
         to get data from.
        :param third_party_tool: The tool you want to connect a suite to
        """
        # TODO first check that the specified suite exists
        # TODO second check that the specified third_party_tool is allowed
        raise NotImplementedError

    def predict(self, suite: str) -> List[Dict]:
        """Use a model from a suite to predict a chunk of data
        that will be returned immediately (as Neuro.ai)

        :param suite: for example 'retention' the name of the suite
         to get data from.
        :return: the prediction
        """
        # TODO first check that the specified suite exists
        raise NotImplementedError

    def store_prediction_in_db(self):
        """This is all what MindsDB does
        NOT TO BE IMPLEMENTED SOON
        """
        raise NotImplementedError

    def charts_catalog(self, s: Callable):
        """
        :param s: SDK class instance Client()
        """
        print('Note - It takes about ~3 minutes to process it all')
        create_bar(s)
        create_pie(s)
        create_html(s)
        create_line(s)
        create_tree(s)
        create_table(s)
        create_gauge(s)
        create_radar(s)
        create_funnel(s)
        create_iframe(s)
        create_sankey(s)
        create_scatter(s)
        create_heatmap(s)
        create_treemap(s)
        create_themeriver(s)
        create_sunburst(s)
        create_stockline(s)
        create_indicator(s)
        create_alert_indicator(s)
        create_predictive_line(s)

    # TODO WiP
    def shimoku_backoffice(self, s):
        """Create a BackOffice for Shimoku users that contain
        all the data regarding what Businesses, AppTypes, Apps, Reports
        they do have active for a target business
        """
        menu_path_seed: str = 'shimoku-backoffice'
        businesses: List[Dict] = s.universe.get_universe_businesses()

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

        app_types: List[Dict] = s.universe.get_universe_app_types()

        apps: List[Dict] = []
        for business in businesses:
            apps_temp: List[Dict] = s.business.get_business_apps(business['id'])
            apps = apps + apps_temp

        reports: List[Dict] = []
        for app in apps:
# TODO quitar este try exceot
            try:
                reports_temp = s.app.get_app_reports(
                    business_id=app['appBusinessId'],
                    app_id=app['id'],
                )
            except Exception:
                continue
            reports = reports + reports_temp

# TODO quitar los pirnts
        print('Note - It takes about 5 minutes to process')
        start_time = dt.datetime.now()
        print(f'Start time {start_time}')
        set_report_detail(
            shimoku=s,
            menu_path_seed=menu_path_seed,
            reports=reports,
        )
        print('report detail created')
        set_apps_detail(
            shimoku=s,
            menu_path_seed=menu_path_seed,
            apps=apps,
            reports=reports,
        )
        print('apps detail created')
        set_app_type_detail(
            shimoku=s,
            menu_path_seed=menu_path_seed,
            app_types=app_types,
            apps=apps,
        )
        print('apptype detail created')
        set_business_detail(
            shimoku=s,
            menu_path_seed=menu_path_seed,
            businesses=businesses,
            apps=apps,
        )
        print('business detail created')
        set_overview_page(
            shimoku=s,
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

    def cohorts(
        self, data: Union[str, DataFrame, List[Dict]],
        user_col: str, event_date_col: str, creation_date_col: str,
    ):
        # TODO data is for create or update?
        raise NotImplementedError

    def predictive_cohorts(
        self, data: Union[str, DataFrame, List[Dict]],
        user_col: str, event_date_col: str, creation_date_col: str,
        metadata: Dict,
    ):
        # TODO data is for create or update?
        raise NotImplementedError

    def retention(
        self, data: Union[str, DataFrame, List[Dict]],
        user_col: str, event_date_col: str, event_revenue_col: str,
        metadata: Dict,
        churn_col: Optional[str] = None  # Supervised (churn) or unsupervised (retention)
    ):
        """Create the Retention Suite

        :param data:
        :param user_col:
        :param event_date_col:
        :param event_revenue_col:
        :param metadata: Further columns to consider in the prediction (AutoML)
        :param churn_col:
        """
        # TODO data is for create or update?
        raise NotImplementedError

    def recommender(
        self, data: Union[str, DataFrame, List[Dict]],
        user_col: str, purchase_id_col: str, product_id_col: str,
        event_date_col: str, event_revenue_col: str,
        metadata: Dict,
    ):
        """Create a Recommender Suite"""
        # TODO data is for create or update?
        raise NotImplementedError

    def anomaly(
        self, data: Union[str, DataFrame, List[Dict]],
        target_cols: List[str], event_datetime_col: str,
        metadata: Dict,
    ):
        """Create the Anomaly Suite"""
        # TODO data is for create or update?
        raise NotImplementedError

    def sales_prediction(
        self, data: Union[str, DataFrame, List[Dict]],
        user_col: str, purchase_id_col: str, product_id_col: str,
        event_date_col: str, event_revenue_col: str,
        metadata: Dict,
    ):
        """Create the Product Sales Suite"""
        # TODO data is for create or update?
        raise NotImplementedError
