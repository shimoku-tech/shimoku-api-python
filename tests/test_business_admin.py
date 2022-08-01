from os import getenv
import datetime as dt
import shimoku_api_python as shimoku

#  Environment variables (credentials):

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
)

s.plt.set_business(business_id=business_id)

#  disappear = s.plt.delete_path(menu_path='testRM')

menu_path: str = 'Test 1'

data_ = [
    {
        'description': 'cryo',
        'title': 'VAC',
        'value': '15',
        'color': 'success-background'
    }
]

s.plt.indicator(
    data=data_,
    menu_path=menu_path,
    row=1, column=1,
    value='value',
    color='color',
    header='title',
    footer='description',
)

data_ = [
    {
        'description': 'multi',
        'title': 'VAC',
        'value': 'distributed',
        'color': 'error-background',
    }
]
s.plt.indicator(
    data=data_,
    menu_path=menu_path,
    row=2, column=1,
    value='value',
    color='color',
    header='title',
    footer='description',
)


data = [
    {'date': dt.date(2021, 1, 1), 'x': 5, 'y': 5},
    {'date': dt.date(2021, 1, 2), 'x': 6, 'y': 5},
    {'date': dt.date(2021, 1, 3), 'x': 4, 'y': 5},
    {'date': dt.date(2021, 1, 4), 'x': 7, 'y': 5},
    {'date': dt.date(2021, 1, 5), 'x': 3, 'y': 5},
]

s.plt.bar(
        data=data,
        x='date', y=['x', 'y'],
        menu_path=menu_path,
        row=3, column=1,
    )
