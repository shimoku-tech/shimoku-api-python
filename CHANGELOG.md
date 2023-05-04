# CHANGELOG

## 0.19.0 (2023-04-28)

This is a small version that improves the UX of the dashboard manipulation.

## Improvements

- The dashboard's default behaviour on the plotting module has been changed so that the name of the working dashboard is always respected. Before the apps were only included in a dashboard by the plotting module when the apps were being created, now every time an app is used by the plotting module it will check if the app is in the working dashboard, in case it is not, the module will automatically add the app to the dashboard.

- Now the apps can be referenced by name in the dashboards module.

- New methods have been added to the dashboards module:
    - `s.dashboard.group_apps`
    - `s.dashboard.remove_all_apps_from_dashboard`
    - `s.dashboard.is_app_in_dashboard`
    - `s.dashboard.force_delete_dashboard`

See the updated documentation in:

- [Quick Start](https://docs.shimoku.com/development/getting-started/quickstart)
- [Menu]
- [Managing Dashboards]


