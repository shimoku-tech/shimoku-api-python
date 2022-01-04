""""""
from os import getenv
import shimoku_api_python as shimoku


api_key: str = getenv('API_TOKEN')
universe_id: str = getenv('UNIVERSE_ID')
business_id: str = getenv('BUSINESS_ID')

s = shimoku.Client(
    config={'access_token': api_key},
    universe_id=universe_id,
)
s.plt.set_business(business_id=business_id)


def test_shimoku_backoffice():
# TODO there are some bugs (ToDo) within it
    s.suite.shimoku_backoffice()


def test_charts_catalog():
# TODO it is not creating all of them!!
    s.suite.charts_catalog()


# test_shimoku_backoffice()
test_charts_catalog()
