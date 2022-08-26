""""""
from sys import stdout
from typing import List, Dict, Optional, Callable, Tuple, Any
import logging
import functools
import json
import time
from itertools import repeat

from concurrent.futures import ThreadPoolExecutor
import requests as rq
from requests.exceptions import Timeout, ReadTimeout

import pandas as pd

from shimoku_api_python.api.plot_api import BasePlot, PlotApi


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logging.basicConfig(
    stream=stdout,
    datefmt='%Y-%m-%d %H:%M',
    format='%(asctime)s | %(levelname)s | %(message)s'
)


# TODO this should not go here but in a different script, maybe aux.py?
def with_retries(
        _func: Optional[Callable] = None,
        *, max_retries: int = 3, exponential_base: int = 2,
) -> Callable:
    """
    Decorate a function for retries.
    Exponential backoff.
    """

    def wrapper(func):
        @functools.wraps(func)
        def retries(*args, **kwargs):
            """
            Attempt a transaction with retries.
            """
            retry_exceptions = (
                'ProvisionedThroughputExceededException',
                'ThrottlingException'
            )

            retries = 0
            while retries < max_retries:
                pause_time = exponential_base ** retries
                # logging.info('Back-off set to %d seconds', pause_time)

                try:
                    return func(*args, **kwargs)
                # This one for Extractions from origin that return an XML / HTML rather than a proper response.
                except json.decoder.JSONDecodeError:
                    # For when the content cannot be decoded. Usually a bad response HTML/XML.
                    # logger.warning(f'Request response raised JSONDecodeError in {func.__name__} | '
                    #               f'Retry {retries} | Sleeping {exponential_base ** retries}. \n {e}')
                    time.sleep(pause_time)
                    retries += 1
                # Requests errors.
                except Timeout as e:
                    # logger.warning(f'Request Timeout Error in {func.__name__} | Retry {retries} | '
                    #               f'Sleeping {exponential_base ** retries}. \n {e}')
                    print('Timeout | Retrying')
                    time.sleep(pause_time)
                    retries += 1
                except ReadTimeout as e:
                    print('ReadTimeout | Retrying')
                    time.sleep(pause_time)
                    retries += 1
                except ConnectionError:
                    print('ConnectionError | Retrying')
                    time.sleep(pause_time)
                    retries += 1

            # raise MaxRetriesExceeded(f'Too many retries for {func.__name__} method')
            raise ValueError(f'Too many retries for {func.__name__} method')

        return retries

    return wrapper if not _func else wrapper(_func)


class AiPlotAdapter(BasePlot):
    _table = PlotApi.table


class AiAPI(AiPlotAdapter):

    def __init__(self, api_client, **kwargs):
        self.api_client = api_client

        if kwargs.get('business_id'):
            self.business_id: Optional[str] = kwargs['business_id']
        else:
            self.business_id: Optional[str] = None

    def predict_categorical(
            self, df_test: pd.DataFrame,
            model_endpoint: Optional[str] = None,
            app_name: Optional[str] = None, model_name: Optional[str] = None,
            explain: bool = False, append_test_data: bool = True,
    ) -> Tuple[pd.DataFrame, pd.DataFrame]:

        def _create_request_data(window: int = 100):
            """Iterate over a dataframe in chunks of N row returning
            a list of json that can be sent to the ML API endpoint

            The size of the chunks is defined by `window`
            """
            raw_json: str = df_test.to_json(orient='records')
            raw_data: Dict = json.loads(raw_json)
            size = len(raw_data)
            for i in range(0, size, window):
                max_value = i + window
                if max_value > size:
                    max_value = size
                chunk_: List = raw_data[i: max_value]
                chunk_: List = [json.dumps([conditions, raw_datum]) for raw_datum in chunk_]
                yield chunk_

        def _clean_response(response_: Tuple, explainability_col_name: str = 'explainability') -> Dict:
            """Create the result out of the response

            Example
            ---------------
            input
                {'ID_POL': {'0': 651407},
                 'ID_CND': {'0': 1},
                 'PRIMER_EFECTO': {'0': '2018-01-13 00:00:00'},
                 'T_SEXO_TOMADOR': {'0': 'M'},
                 'prediction_probability': {'0': 0.6594810000302692},
                 'explainability': {
                    'sub_price_0': {'0': -0.18447917592951263},
                    'sub_npays_year': {'0': -0.0033977641276157094},
                    'hol_age': {'0': 0.0319888495770443},
                    'hol_seniority_driver': {'0': 0.016372795631977008}
                 },
                }

            output
                {'ID_POL': 653315,
                 'ID_CND': 1,
                 'PRIMER_EFECTO': '2018-01-25 12:14:00',
                 'T_SEXO_TOMADOR': 'F',
                 'prediction_probability': 0.7442640821276456,
                 'explainability': {
                    'sub_price_0': -0.32314667154583626,
                    'sub_npays_year': -0.018958441618165747,
                    'hol_age': 0.02434736937940205,
                    'hol_seniority_driver': 0.0008888141433092845,
                 }
                }
            """
            # position 0 contains the request status code
            if response_[0] < 200 or response_[0] > 300:  # position 1 contains the input
                d = json.loads(response_[1])[1]
                d['prediction_probability'] = 'ERROR'
                if explain:
                    d[explainability_col_name] = 'ERROR'
                return d

            # position 2 contains the request output
            result_: Dict = json.loads(response_[2])
            d: Dict = {k: v['0'] for k, v in result_.items() if k != explainability_col_name}
            if explain:
                d[explainability_col_name] = {
                    k: v['0'] for k, v in result_.get(explainability_col_name).items()
                }

            if not append_test_data:
                # TODO keep only: id, prediction column and explainability columns
                # cols_to_avoid = [c for c in df_test.columns if c != 'ID_POL']
                # d = {k: v for k, v in d.items() if k not in cols_to_avoid}
                pass

            return d

        @with_retries
        def _http_get_with_requests(url_: str, data: Dict) -> (int, Dict[str, Any], bytes):
            time.sleep(.25)
            response = rq.request('POST', url_, data=data)

            response_content = None
            try:
                response_content = response.content
            except Exception:
                pass

            return response.status_code, data, response_content

        def _http_get_with_requests_parallel(
                url: List[str], chunk_: List[Dict]
        ) -> Tuple[List, List]:
            rs: List = []
            rs_error: List = []
            executor = ThreadPoolExecutor(max_workers=100)
            for result in executor.map(_http_get_with_requests, repeat(url), chunk_):
                if result[0] >= 300:  # status_code
                    rs_error.append(result)
                else:
                    rs.append(result)

            # Another retry
            if rs_error:
                time.sleep(1)
                new_chunk = [element[1] for element in rs_error]
                rs_error = []
                for result in executor.map(_http_get_with_requests, repeat(url), new_chunk):
                    if result[0] >= 300:  # status_code
                        rs_error.append(result)
                    else:
                        rs.append(result)

            return rs, rs_error

        if not model_endpoint:
            if not app_name or not model_name:
                raise ValueError('model_endpoint OR app_name and model_name are required')

        results: List = []
        results_error: List = []
        # conditions: Dict = {"prediction_probability": True, "explainability": explain}
        conditions: Dict = {"churn_probability": True, "shap_contributions": explain}
        crd = _create_request_data(100)
        for chunk in crd:
            rs_, rs_error_ = _http_get_with_requests_parallel(url=model_endpoint, chunk_=chunk)
            results = results + [
                _clean_response(r, explainability_col_name='shap_contributions')
                for r in rs_
            ]
            results_error = results_error + [
                _clean_response(r, explainability_col_name='shap_contributions')
                for r in rs_error_
            ]

        return pd.DataFrame(results), pd.DataFrame(results_error)

    def train_model(self) -> str:
        """
        returns the model endpoint
        """
        raise NotImplementedError

    def predictive_table(
            self, df_test: pd.DataFrame,
            target_column: str, column_to_predict: str,
            menu_path: str, order: int,
            model_endpoint: Optional[str] = None,
            app_name: Optional[str] = None, model_name: Optional[str] = None,
            explain: bool = True,
            prediction_type: str = 'categorical',
            add_filter_by_column_to_predict: bool = True,
            add_search_by_target_column: bool = True,
            extra_filter_columns: Optional[List[str]] = None,
            extra_search_columns: Optional[List[str]] = None,
    ):
        """Predict a tabular dataset and store the results in a model

        Example
        --------------------
        target_column = 'customer_id'
        column_to_predict = 'y'

        :param df_test:
        :param target_column:
        :param column_to_predict:
        :param menu_path:
        :param order:
        :param model_endpoint:
        :param app_name:
        :param model_name:
        :param explain:
        :param prediction_type:
        :param add_filter_by_column_to_predict:
        :param add_search_by_target_column:
        :param extra_filter_columns:
        :param extra_search_columns:
        :return:
        """
        if not model_endpoint:
            if not app_name or not model_name:
                raise ValueError('model_endpoint OR app_name and model_name are required')

        available_predictions: List[str] = ['categorical']
        if prediction_type not in available_predictions:
            raise ValueError(
                f'{prediction_type} not allowed | '
                f'Prediction type available are {available_predictions}'
            )

        df_result, _ = self.predict_categorical(
            df_test=df_test, model_endpoint=model_endpoint, explain=explain,
        )

        if add_filter_by_column_to_predict:
            filter_columns: List[str] = [column_to_predict]
        else:
            filter_columns = []

        if add_search_by_target_column:
            search_columns: List[str] = [target_column]
        else:
            search_columns = []

        if extra_filter_columns:
            filter_columns = filter_columns + extra_filter_columns
        if extra_search_columns:
            search_columns = search_columns + extra_search_columns

        self._table(
            data=df_result,
            menu_path=menu_path,
            order=order,
            filter_columns=filter_columns,
            search_columns=search_columns,
        )
