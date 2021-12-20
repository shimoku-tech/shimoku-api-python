""""""
from os import getenv
from typing import List, Dict
from collections import Counter
import json

import pandas as pd

import shimoku_api_python as shimoku


api_key: str = getenv('API_TOKEN')
universe_id: str = getenv('UNIVERSE_ID')


config = {
    'access_token': api_key,
}

s = shimoku.Client(
    config=config,
    universe_id=universe_id,
)


menu_path_seed: str = 'shimoku-backoffice'
businesses: List[Dict] = s.universe.get_universe_businesses()

bo_business = [
    business for business in businesses if business['name'] == 'shimoku-backoffice'
]
if not bo_business:
    bo_business = s.business.create_business(name='shimoku-backoffice')
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

reports: List[Dict] = []
for app in apps:
    reports_temp = s.app.get_app_reports(
        business_id=app['appBusinessId'],
        app_id=app['id'],
    )
    reports = reports + reports_temp


def set_overview_page():
    menu_path: str = f'{menu_path_seed}/overview'
    data_overview_alert_indicator: List[Dict] = [
        {
            "description": "Number of Businesses",
            "title": "Businesses",
            "value": len(businesses),
            "color": "warning-background",
            "targetPath": f"/{menu_path_seed}/business-detail",
        },
        {
            "description": "Number of different apps",
            "title": "Apps types",
            "value": len(app_types),
            "color": "warning-background",
            "targetPath": f"/{menu_path_seed}/app-type-detail",
        },
        {
            "description": "Number of Apps",
            "title": "Apps",
            "value": len(apps),
            "color": "warning-background",
            "targetPath": f"/{menu_path_seed}/apps-detail",
        },
        {
            "description": "Number of Reports",
            "title": "Reports",
            "value": len(reports),
            "color": "warning-background",
            "targetPath": f"/{menu_path_seed}/reports-detail",
        },
    ]

    s.plt.alert_indicator(
        data=data_overview_alert_indicator,
        menu_path=menu_path,
        row=1, column=1,
        value='value',
        header='title',
        footer='description',
        color='color',
        target_path='targetPath',
    )

    data_overview_indicator = [
        {
            "description": "Average apps per business",
            "title": "Average apps per business",
            "value": f'{len(apps) / len(businesses)}',
        },
        {
            "description": "Average reports per app",
            "title": "Average reports per app",
            "value": f'{len(reports) / len(apps)}',
        },
        {
            "description": "Average reports per business",
            "title": "Average reports per business",
            "value": f'{len(reports) / len(business)}',
        },
    ]

    s.plt.indicator(
        data=data_overview_indicator,
        menu_path=menu_path,
        row=2, column=1,
        value='value',
        header='title',
        footer='description',
    )


def set_business_detail():
    menu_path: str = f'{menu_path_seed}/business-detail'
    df_ = pd.DataFrame(apps)
    apps_by_business = df_.groupby('appBusinessId')['id'].count().to_dict()
    for business_ in businesses:
        business_['apps number'] = apps_by_business[business_['id']]
        business_['universe_id'] = business_['universe']['id']

    cols_to_keep: List[str] = [
        'id',
        'name',
        'apps number',
        'universe_id',
    ]
    business_df = pd.DataFrame(businesses)
    business_df = business_df[cols_to_keep]

    filter_columns: List[str] = []
    s.plt.table(
        data=business_df,
        menu_path=menu_path,
        row=1, column=1,
        filter_columns=filter_columns,
    )


def set_app_type_detail():
    menu_path: str = f'{menu_path_seed}/app-type-detail'
    for app_ in apps:
        app_['app_type_id'] = app_['type']['id']
    df_ = pd.DataFrame(apps)
    apps_by_type = df_.groupby('app_type_id')['id'].count().to_dict()
    for app_type in app_types:
        app_type['apps number'] = apps_by_type[app_type['id']]
        app_type['universe_id'] = app_type['universe']['id']

    cols_to_keep: List[str] = [
        'id',
        'name',
        'apps number',
        'universe_id',
    ]
    app_types_df = pd.DataFrame(app_types)
    app_types_df = app_types_df[cols_to_keep]

    filter_columns: List[str] = []
    s.plt.table(
        data=app_types_df,
        menu_path=menu_path,
        row=1, column=1,
        filter_columns=filter_columns,
    )


def set_apps_detail():
    menu_path: str = f'{menu_path_seed}/app-detail'
    df_ = pd.DataFrame(reports)
    reports_by_apps = df_.groupby('appId')['id'].count().to_dict()
    data_error: List[str] = []
    for app_ in apps:
        try:
            app_['apps number'] = reports_by_apps[app_['id']]
        except KeyError:
            # TODO this is to make an indicator
            data_error: List[str] = data_error + [app_['id']]

    filter_columns: List[str] = []
    s.plt.table(
        data=apps,
        menu_path=menu_path,
        row=1, column=1,
        filter_columns=filter_columns,
    )


def set_report_detail():
    menu_path: str = f'{menu_path_seed}/report-detail'
    report_types: List[str] = [
        json.loads(report['dataFields'])['type'].capitalize()
        if report["reportType"] == 'ECHARTS'
        else report["reportType"].lower().capitalize()
        if report["reportType"]
        else 'Table'
        for report in reports
    ]
    data_reports_indicator = [
        {
            "description": "Different types of reports",
            "title": "Type of reports",
            "value": f'{set(report_types)}',
        },
    ]

    s.plt.indicator(
        data=data_reports_indicator,
        menu_path=menu_path,
        row=1, column=1,
        value='value',
        header='title',
        footer='description',
    )

    data = dict(Counter(report_types))
    s.plt.bar(
        data=data,
        x='report_type', y='count',
        menu_path='test/bar-test',
        row=2, column=1,
    )

    filter_columns: List[str] = []
    s.plt.table(
        data=reports,
        menu_path=menu_path,
        row=3, column=1,
        filter_columns=filter_columns,
    )


# set_overview_page()
print('overview created')
# set_business_detail()
set_app_type_detail()
print('business detail created')
set_apps_detail()
print('apps detail created')
set_report_detail()
print('report detail created')
