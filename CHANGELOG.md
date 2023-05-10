# CHANGELOG

## 0.20.0 (2023-05-10)

This version enables embedding, it's time to share dashboards with the internet!

## Improvements

When creating or updating a dashboard the user can set the parameter is_public to True, this will enable the embedding functionality for the dashboard in the frontal page.

See the updated documentation in:

- [Managing Dashboards](https://docs.shimoku.com/development/advanced-usage/management/managing-dashboards)

---

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
- [Managing Dashboards](https://docs.shimoku.com/development/advanced-usage/management/managing-dashboards)


