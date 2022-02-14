""""""
from sys import stdout
from typing import List, Dict, Union, Optional
import logging

import datetime as dt
from pandas import DataFrame

from .templates.shimoku_backoffice import (
    set_report_detail, set_apps_detail, set_app_type_detail,
    set_business_detail, set_overview_page,
)
from .templates.charts_catalog import (
    create_bar, create_horizontal_bar, create_zero_centered_barchart,
    create_pie, create_html,
    create_line, create_tree, create_table,
    create_ring_gauge, create_speed_gauge, create_radar, create_funnel,
    create_iframe, create_sankey, create_scatter,
    create_heatmap, create_treemap, create_themeriver,
    create_sunburst, create_stockline, create_indicator,
    create_alert_indicator, create_predictive_line
)


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logging.basicConfig(
    stream=stdout,
    datefmt='%Y-%m-%d %H:%M',
    format='%(asctime)s | %(levelname)s | %(message)s'
)


class SuiteApi:
    """
    """

    def __init__(self, s):
        """
        :param s: Shimoku instance
        """
        # Assign to the self the object 's' as the new 'self'
        self.__dict__.update(s.__dict__)

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

    def predict(
        self, data: Union[str, DataFrame, List[Dict]], suite: str,
    ) -> List[Dict]:
        """Use a model from a suite to predict a chunk of data
        that will be returned immediately (as Neuro.ai)

        :param data:
        :param suite: for example 'retention' the name of the suite
         to get data from.
        :return: the prediction
        """
        available_suites: List[str] = [
            'retention',
            'predictive_cohorts',
            'recommender',
            'anomaly',
            'sales_prediction',
        ]

        if suite not in available_suites:
            raise ValueError(
                f'Suite {suite} | '
                f'Not available |  '
                f'Available suites are {available_suites}'
            )

        if not isinstance(data, DataFrame):
            df: DataFrame = self._validate_data_is_pandarable(data)
        else:
            df = data.copy()
            del data
        # TODO first check that the specified suite exists

        # TODO this method needs to be created
        #  and potentially needs to be async
        #  study it!!!
        # df_pred: DataFrame = await self.api_get_predictions(df, suite)
        return df_pred

    def store_prediction_in_db(self):
        """This is all what MindsDB does
        NOT TO BE IMPLEMENTED SOON
        """
        raise NotImplementedError

    def charts_catalog(self):
        """self is an instance of the Client()
        """
        logger.info('Note - It takes about ~3 minutes to process it all')
        create_bar(self)
        create_horizontal_bar(self)
        create_zero_centered_barchart(self)
        create_pie(self)
        create_html(self)
        create_line(self)
        create_tree(self)
        create_table(self)
        create_ring_gauge(self)
        create_speed_gauge(self)
        create_radar(self)
        create_funnel(self)
        create_iframe(self)
        create_sankey(self)
        create_scatter(self)
        create_heatmap(self)
        create_treemap(self)
        create_themeriver(self)
        create_sunburst(self)
        create_stockline(self)
        create_indicator(self)
        create_alert_indicator(self)
        create_predictive_line(self)

    def shimoku_backoffice(self):
        """Create a BackOffice for Shimoku users that contain
        all the data regarding what Businesses, AppTypes, Apps, Reports
        they do have active for a target business
        """
        logger.info('Shimoku Backoffice - It takes about 5 minutes to be processed')
        start_time = dt.datetime.now()

        menu_path_seed: str = 'shimoku-backoffice'
        businesses: List[Dict] = self.universe.get_universe_businesses()

        bo_business = [
            business for business in businesses
            if business['name'] == menu_path_seed
        ]
        if not bo_business:
            bo_business = self.business.create_business(name=menu_path_seed)
        else:
            bo_business = bo_business[0]
        business_id = bo_business['id']
        self.plt.set_business(business_id)

        app_types: List[Dict] = self.universe.get_universe_app_types()

        apps: List[Dict] = []
        for business in businesses:
            apps_temp: List[Dict] = self.business.get_business_apps(business['id'])
            apps = apps + apps_temp

        reports: List[Dict] = []
        for app in apps:
            try:
                reports_temp = self.app.get_app_reports(
                    business_id=app['appBusinessId'],
                    app_id=app['id'],
                )
            except Exception as e:
                continue
            reports = reports + reports_temp

        set_overview_page(
            shimoku=self,
            menu_path_seed=menu_path_seed,
            businesses=businesses,
            app_types=app_types,
            apps=apps,
            reports=reports,
        )
        logger.info('Page "Overview" created')
        set_business_detail(
            shimoku=self,
            menu_path_seed=menu_path_seed,
            businesses=businesses,
            apps=apps,
        )
        logger.info('Page "Business detail" created')
        set_app_type_detail(
            shimoku=self,
            menu_path_seed=menu_path_seed,
            app_types=app_types,
            apps=apps,
        )
        logger.info('Page "Apptype detail" created')
        set_apps_detail(
            shimoku=self,
            menu_path_seed=menu_path_seed,
            apps=apps,
            reports=reports,
        )
        logger.info('Page "Apps detail" created')
        set_report_detail(
            shimoku=self,
            menu_path_seed=menu_path_seed,
            reports=reports,
        )
        logger.info('Page "Report detail" created')
        end_time = dt.datetime.now()
        logger.info(f'Execution time: {end_time - start_time}')

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
        # TODO _validate_data_is_pandarable should be inherited
        df: DataFrame = self._validate_data_is_pandarable(data)
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

    def canva(self):
        """
        The idea is to define a whole path with a single element

        canva = {
            'metrica': {
                'normalizada': {'row': 1, 'column': 1, 'component_type': 'bar'},
                'trend5': {'row': 1, 'column': 2, 'component_type': 'line'},
                'trend53': {'row': 2, 'column': 1, 'component_type': 'predictive_line'},
                'anual': {'row': 2, 'column': 2, 'component_type': 'line'},
            }
        }
        """
        raise NotImplementedError
