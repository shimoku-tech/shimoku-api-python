""""""
from typing import List, Dict, Callable
from collections import Counter
import json

import pandas as pd


def set_overview_page(
    shimoku: Callable,
    menu_path_seed: str,
    businesses: List[Dict],
    app_types: List[Dict],
    apps: List[Dict],
    reports: List[Dict],
):
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

    shimoku.plt.alert_indicator(
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
            "value": f'{round(len(apps) / len(businesses), 2)}',
        },
        {
            "description": "Average reports per app",
            "title": "Average reports per app",
            "value": f'{round(len(reports) / len(apps), 2)}',
        },
        {
            "description": "Average reports per business",
            "title": "Average reports per business",
            "value": f'{round(len(reports) / len(businesses), 2)}',
        },
    ]

    shimoku.plt.indicator(
        data=data_overview_indicator,
        menu_path=menu_path,
        row=2, column=1,
        value='value',
        header='title',
        footer='description',
    )


def set_business_detail(
    shimoku: Callable,
    menu_path_seed: str,
    businesses: List[Dict],
    apps: List[Dict],
):
    menu_path: str = f'{menu_path_seed}/business-detail'
    df_ = pd.DataFrame(apps)
    apps_by_business = df_.groupby('appBusinessId')['id'].count().to_dict()
    for business_ in businesses:
        try:
            business_['apps number'] = apps_by_business[business_['id']]
        except KeyError:
            business_['apps number'] = 0
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
    shimoku.plt.table(
        data=business_df,
        menu_path=menu_path,
        row=1, column=1,
        filter_columns=filter_columns,
    )


def set_app_type_detail(
    shimoku: Callable,
    menu_path_seed: str,
    app_types: List[Dict],
    apps: List[Dict],
):
    menu_path: str = f'{menu_path_seed}/app-type-detail'
    for app_ in apps:
        app_['app_type_id'] = app_['type']['id']
    df_ = pd.DataFrame(apps)
    apps_by_type = df_.groupby('app_type_id')['id'].count().to_dict()
    for app_type in app_types:
        try:
            app_type['apps number'] = apps_by_type[app_type['id']]
        except KeyError:
            app_type['apps number'] = 0
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
    shimoku.plt.table(
        data=app_types_df,
        menu_path=menu_path,
        row=1, column=1,
        filter_columns=filter_columns,
    )


def set_apps_detail(
    shimoku: Callable,
    menu_path_seed: str,
    apps: List[Dict],
    reports: List[Dict],
):
    menu_path: str = f'{menu_path_seed}/apps-detail'
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
    apps_df: pd.DataFrame = pd.DataFrame(apps)
    cols_to_keep: List[str] = [
        'id', 'appBusinessId', 'createdAt',
    ]
    apps_df = apps_df[cols_to_keep]
    shimoku.plt.table(
        data=apps_df,
        menu_path=menu_path,
        row=1, column=1,
        filter_columns=filter_columns,
    )


def set_report_detail(
    shimoku: Callable,
    menu_path_seed: str,
    reports: List[Dict],
):
    if not reports:
        return

    menu_path: str = f'{menu_path_seed}/reports-detail'
    report_types: List[str] = [
        json.loads(report['dataFields'])['type'].capitalize()
        if report["reportType"] == 'ECHARTS'
        else report["reportType"].lower().capitalize()
        if report["reportType"]
        else 'Table'
        for report in reports
    ]

    data = dict(Counter(report_types))
    df = pd.DataFrame(data, index=[0]).T.reset_index()
    df.columns = ['report_type', 'count']
    shimoku.plt.bar(
        data=df,
        title='Total number of reports by type in your apps',
        x='report_type', y=['count'],
        x_axis_name='Report Type', y_axis_name='Count',
        menu_path=menu_path,
        row=1, column=1,
    )

    filter_columns: List[str] = []
    reports_df: pd.DataFrame = pd.DataFrame(reports)
    cols_to_keep: List[str] = [
        'id', 'appId', 'path', 'grid', 'createdAt', 'reportType',
    ]
    reports_df = reports_df[cols_to_keep]
    reports_df = reports_df.fillna('-')
    shimoku.plt.table(
        data=reports_df,
        menu_path=menu_path,
        row=2, column=1,
        title='All reports detail',
        filter_columns=filter_columns,
    )
