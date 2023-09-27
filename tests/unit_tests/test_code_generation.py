import unittest
from test_plot_api import main, shimoku_client as tpa_shimoku_client
import shimoku_api_python as shimoku
import tempfile
import subprocess
import shutil
import json
import datetime as dt
from deepdiff import DeepDiff
from os import getenv

mock = getenv('MOCK') == 'TRUE'


def get_report_data_set_info(
    r_hash: str, report_data_set: dict, data_sets_mapping: dict[str, str]
) -> dict:
    report_data_set.pop('id')
    report_id = report_data_set.pop('reportId')
    report_data_set['dataSetId'] = data_sets_mapping[report_data_set['dataSetId']].replace(report_id, r_hash)
    return report_data_set


def get_report_data_set_info_dict(
    r_hash: str, _dict: dict, report_data_sets: dict[str, dict], data_sets_mapping: dict[str, str]
):
    for k, v in _dict.items():
        if isinstance(v, dict):
            get_report_data_set_info_dict(r_hash, v, report_data_sets, data_sets_mapping)
        elif isinstance(v, list):
            get_report_data_set_info_list(r_hash, v, report_data_sets, data_sets_mapping)
        elif isinstance(v, str) and v.startswith('#{') and v.endswith('}'):
            uuid = v[2:-1]
            _dict[k] = get_report_data_set_info(r_hash, report_data_sets[uuid], data_sets_mapping)


def get_report_data_set_info_list(
    r_hash: str, _list: list, report_data_sets: dict[str, dict], data_sets_mapping: dict[str, str]
):
    for i, v in enumerate(_list):
        if isinstance(v, dict):
            get_report_data_set_info_dict(r_hash, v, report_data_sets, data_sets_mapping)
        elif isinstance(v, list):
            get_report_data_set_info_list(r_hash, v, report_data_sets, data_sets_mapping)
        elif isinstance(v, str) and v.startswith('#{') and v.endswith('}'):
            uuid = v[2:-1]
            _list[i] = get_report_data_set_info(r_hash, report_data_sets[uuid], data_sets_mapping)


def clear_workspace(shimoku_client):
    for menu_path in shimoku_client.workspaces.get_workspace_menu_paths(shimoku_client.workspace_id):
        shimoku_client.menu_paths.delete_all_menu_path_activities(uuid=menu_path['id'])
    shimoku_client.workspaces.delete_all_workspace_menu_paths(shimoku_client.workspace_id)
    shimoku_client.workspaces.delete_all_workspace_boards(shimoku_client.workspace_id)


def change_ids_in_tabs_or_modal(component, components_by_id):
    if 'tabs' in component['properties']:
        for tab_name, tab_dict in component['properties']['tabs'].items():
            component['properties']['tabs'][tab_name]['reportIds'] = sorted([
                components_by_id[r_id]['properties']['hash'] for r_id in tab_dict['reportIds']
            ])
    if 'reportIds' in component['properties']:
        component['properties']['reportIds'] = sorted([
            components_by_id[r_id]['properties']['hash'] for r_id in component['properties']['reportIds']
        ])


def handle_events(events, components_by_id):
    on_click_events = events.get('onClick', [])
    for event in on_click_events:
        if 'modalId' in event['params']:
            event['params']['modalId'] = components_by_id[event['params']['modalId']]['properties']['hash']


def handle_bentobox(component, current_bentobox):
    if not component.get('bentobox'):
        current_bentobox['id_to_replace'] = ''
        return
    bentobox_id = component['bentobox']['bentoboxId']

    if bentobox_id != current_bentobox['id_to_replace']:
        current_bentobox['id_to_replace'] = bentobox_id
        current_bentobox['bentoboxId'] = f'_{component["order"]}'
        current_bentobox['bentoboxOrder'] = component['order']

    component['bentobox']['bentoboxId'] = current_bentobox['bentoboxId']
    component['bentobox']['bentoboxOrder'] = current_bentobox['bentoboxOrder']


def handle_component(shimoku_client, component, mpath_components_by_id, data_sets_mapping, current_bentobox):
    data_set_links = shimoku_client.components.get_component_data_set_links(component['id'])
    get_report_data_set_info_dict(
        component['properties']['hash'], component['properties'],
        {rds['id']: rds for rds in data_set_links}, data_sets_mapping
    )
    handle_bentobox(component, current_bentobox)
    if 'events' in component['properties']:
        handle_events(component['properties']['events'], mpath_components_by_id)
    if component['reportType'] in ['MODAL', 'TABS']:
        change_ids_in_tabs_or_modal(component, mpath_components_by_id)
    elif component['reportType'] == 'FILTERDATASET':
        fds_mapping = component['properties']['mapping']
        fds_mapping[0]['id'] = data_sets_mapping[fds_mapping[0]['id']]


def handle_menu_path(shimoku_client, menu_path, components, data_sets_mapping, data_by_data_set):
    shimoku_client.set_menu_path(menu_path['name'], dont_add_to_dashboard=True)
    mpath_components = sorted(shimoku_client.menu_paths.get_menu_path_components(menu_path['id']),
                              key=lambda x: x['properties']['hash'])
    components.extend(mpath_components)
    components_hash_by_id = {c['id']: c['properties']['hash'] for c in mpath_components}
    data_sets = shimoku_client.menu_paths.get_menu_path_data_sets(menu_path['id'])
    for data_set in data_sets:
        for comp_id in components_hash_by_id.keys():
            if comp_id in data_set['name']:
                data_set['name'] = data_set['name'].replace(comp_id, components_hash_by_id[comp_id])
        data_sets_mapping[data_set['id']] = data_set['name']

    for data_set in sorted(data_sets, key=lambda x: x['name']):
        data_by_data_set[data_set['name']] = shimoku_client.data.get_data_from_data_set(data_set['id'])

    mpath_components_by_id = {c['id']: c for c in mpath_components}
    current_bentobox = {'id_to_replace': '', 'bentoboxId': '', 'bentoboxOrder': ''}
    for component in mpath_components:
        handle_component(shimoku_client, component, mpath_components_by_id, data_sets_mapping, current_bentobox)


def get_diff_percentage(items1, items2):
    return sum(DeepDiff(c1, c2) != {} for c1, c2 in zip(items1, items2))/len(items1)


def get_workspace_contents(shimoku_client):
    boards = sorted(
        shimoku_client.workspaces.get_workspace_boards(shimoku_client.workspace_id),
        key=lambda x: x['order']
    )
    menu_paths = sorted(
        shimoku_client.workspaces.get_workspace_menu_paths(
            shimoku_client.workspace_id
        ),
        key=lambda x: x['order']
    )
    components = []
    data_sets_mapping = {}
    data_by_data_set = {}
    for menu_path in menu_paths:
        handle_menu_path(shimoku_client, menu_path, components, data_sets_mapping, data_by_data_set)
    shimoku_client.pop_out_of_menu_path()
    _all = [*boards, *menu_paths, *components, *[datum for data in data_by_data_set.values() for datum in data]]
    for element in _all:
        element.pop('id')
    return boards, menu_paths, components, data_by_data_set


def create_bar_chart(shimoku_client):
    data = [{'date': dt.date(2021, 1, 1), 'x': 50000000, 'y': 5},
            {'date': dt.date(2021, 1, 2), 'x': 60000000, 'y': 5},
            {'date': dt.date(2021, 1, 3), 'x': 40000000, 'y': 5},
            {'date': dt.date(2021, 1, 4), 'x': 70000000, 'y': 5},
            {'date': dt.date(2021, 1, 5), 'x': 30000000, 'y': 5}]
    shimoku_client.plt.bar(
        data=data, x='date', y=['x', 'y'],
        x_axis_name='Date', y_axis_name='Revenue',
        order=0, rows_size=2,
        cols_size=12,
    )


class TestCodeGen(unittest.TestCase):

    def test_code_gen(self):
        if not tpa_shimoku_client.playground or mock:
            # It would take too long to complete the test
            return
        tpa_shimoku_client.set_workspace()
        clear_workspace(tpa_shimoku_client)
        main()
        tpa_shimoku_client.pop_out_of_dashboard()
        tpa_shimoku_client.disable_caching()
        boards, menu_paths, components, data = get_workspace_contents(tpa_shimoku_client)
        temp_dir = tempfile.mkdtemp()
        tpa_shimoku_client.generate_code(temp_dir)
        clear_workspace(tpa_shimoku_client)
        subprocess.run(['python', f'{temp_dir}/execute_workspace_local.py'], check=True)
        (first_generation_boards,
         first_generation_menu_paths,
         first_generation_components,
         first_generation_data) = get_workspace_contents(tpa_shimoku_client)
        shutil.rmtree(temp_dir)
        temp_dir = tempfile.mkdtemp()
        tpa_shimoku_client.generate_code(temp_dir)
        subprocess.run(['python', f'{temp_dir}/execute_workspace_local.py'], check=True)
        (second_generation_boards,
         second_generation_menu_paths,
         second_generation_components,
         second_generation_data) = get_workspace_contents(tpa_shimoku_client)
        clear_workspace(tpa_shimoku_client)
        tpa_shimoku_client.run()
        shutil.rmtree(temp_dir)
        results = {
            'orig-first': (get_diff_percentage(boards, first_generation_boards),
                           get_diff_percentage(menu_paths, first_generation_menu_paths),
                           get_diff_percentage(components, first_generation_components),
                           get_diff_percentage(data, first_generation_data)),
            'orig-second': (get_diff_percentage(boards, second_generation_boards),
                            get_diff_percentage(menu_paths, second_generation_menu_paths),
                            get_diff_percentage(components, second_generation_components),
                            get_diff_percentage(data, second_generation_data)),
            'first-second': (get_diff_percentage(first_generation_boards, second_generation_boards),
                             get_diff_percentage(first_generation_menu_paths, second_generation_menu_paths),
                             get_diff_percentage(first_generation_components, second_generation_components),
                             get_diff_percentage(first_generation_data, second_generation_data)),
        }
        print(json.dumps(results, indent=4))
        assert all(all([value == 0 for value in results_list]) for results_list in results.values())

    def test_commit(self):
        if tpa_shimoku_client.playground or mock:
            # Test commit only in cloud
            return
        local_shimoku_client = shimoku.Client(verbosity='INFO')
        local_shimoku_client.disable_caching()
        local_shimoku_client.set_workspace()
        clear_workspace(local_shimoku_client)
        local_shimoku_client.set_board('Commit-board')
        local_shimoku_client.set_menu_path('Commit-menu-path')
        create_bar_chart(local_shimoku_client)
        local_boards, local_menu_paths, local_components, local_data = get_workspace_contents(local_shimoku_client)
        clear_workspace(tpa_shimoku_client)
        local_shimoku_client.commit_contents_to(
            access_token=tpa_shimoku_client.access_token,
            environment=tpa_shimoku_client.environment,
            universe_id=tpa_shimoku_client.universe_id,
            workspace_id=tpa_shimoku_client.workspace_id,
            show_progress_bar=True,
        )
        tpa_shimoku_client.disable_caching()
        tpa_shimoku_client.set_workspace(tpa_shimoku_client.workspace_id)
        boards, menu_paths, components, data = get_workspace_contents(tpa_shimoku_client)
        results = {
            'boards': (get_diff_percentage(local_boards, boards)),
            'menu_paths': (get_diff_percentage(local_menu_paths, menu_paths)),
            'components': (get_diff_percentage(local_components, components)),
            'data': (get_diff_percentage(local_data, data)),
        }
        print(json.dumps(results, indent=4))
        assert all([value == 0 for value in results.values()])

    def test_pull(self):
        if tpa_shimoku_client.playground or mock:
            # Test pull only in cloud
            return
        tpa_shimoku_client.set_workspace(tpa_shimoku_client.workspace_id)
        clear_workspace(tpa_shimoku_client)
        tpa_shimoku_client.set_board('Pull-board')
        tpa_shimoku_client.set_menu_path('Pull-menu-path')
        create_bar_chart(tpa_shimoku_client)
        tpa_boards, tpa_menu_paths, tpa_components, tpa_data = get_workspace_contents(tpa_shimoku_client)

        local_shimoku_client = shimoku.Client(verbosity='INFO')
        local_shimoku_client.disable_caching()
        local_shimoku_client.set_workspace()
        clear_workspace(local_shimoku_client)
        local_shimoku_client.pull_contents_from(
            access_token=tpa_shimoku_client.access_token,
            environment=tpa_shimoku_client.environment,
            universe_id=tpa_shimoku_client.universe_id,
            workspace_id=tpa_shimoku_client.workspace_id,
            show_progress_bar=True,
        )
        local_boards, local_menu_paths, local_components, local_data = get_workspace_contents(local_shimoku_client)

        clear_workspace(tpa_shimoku_client)
        clear_workspace(local_shimoku_client)

        results = {
            'boards': (get_diff_percentage(tpa_boards, local_boards)),
            'menu_paths': (get_diff_percentage(tpa_menu_paths, local_menu_paths)),
            'components': (get_diff_percentage(tpa_components, local_components)),
            'data': (get_diff_percentage(tpa_data, local_data)),
        }
        print(json.dumps(results, indent=4))
        assert all([value == 0 for value in results.values()])
