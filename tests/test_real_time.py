from typing import Dict
from os import getenv
import json


import shimoku_api_python as shimoku


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

# disappear = s.plt.delete_path(menu_path='realtime-test')


def test_real_time_feed():

    from time import sleep

    menu_path: str = 'Realtime test'

    data_ = [
        {
            "description": "",
            "title": "Estado",
            "value": "3",
            'targetPath': "audrey",
        },
    ]
    report_id: str = s.plt.indicator(
        data=data_,
        menu_path=menu_path,
        row=1, column=1,
        value='value',
        header='title',
        footer='description',
        real_time=True,
    )

    app: Dict = s.app.get_app_by_name(business_id=business_id, name=menu_path)
    app_id = app['id']
    
    count = 5
    while True:
        count -= 1
        print(count)   #  action

        data_ = json.dumps([{
            "description": "Indicator",
            "title": "State:",
            "value": count,

        }])

        s.report.update_report(
            business_id=business_id,
            app_id=app_id,
            report_id=report_id,
            report_metadata={
                'chartData': data_
            }
        )

        sleep(1)
    
        if count <= 0:
            break


test_real_time_feed()
