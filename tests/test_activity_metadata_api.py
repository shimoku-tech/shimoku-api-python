from os import getenv
import shimoku_api_python as shimoku
from shimoku_api_python.exceptions import CacheError
import unittest

api_key: str = getenv('API_TOKEN')
universe_id: str = getenv('UNIVERSE_ID')
business_id: str = getenv('BUSINESS_ID')
environment: str = getenv('ENVIRONMENT')
verbose: str = getenv('VERBOSITY')
async_execution: bool = getenv('ASYNC_EXECUTION') == 'TRUE'


s = shimoku.Client(
    access_token=api_key,
    universe_id=universe_id,
    environment=environment,
    verbosity=verbose,
    async_execution=async_execution,
    business_id=business_id,
)
s.set_menu_path(menu_path='test_activity')

activity_name = 'test_activity'
run_id = getenv('RUN_ID')

activity_id = s.activity.get_activity(name=activity_name)['id']


class MyTestCase(unittest.TestCase):
    def activity_doesnt_exist(self, _activity_name):
        with self.assertRaises(CacheError):
            s.activity.delete_activity(name=_activity_name)

    def cant_create_activity(self, _activity_name):
        with self.assertRaises(CacheError):
            s.activity.create_activity(name=_activity_name)


def delete_new_activity_if_it_exists():
    """
    Deletes the activity created in the test_create_delete_get_activities test.
    """
    try:
        s.activity.delete_activity(name='new_'+activity_name)
    except CacheError:
        pass


def test_get_run_settings():
    """
    Makes a call to the activity metadata API to get run settings.
    """
    s.activity.get_run_settings(uuid=activity_id, run_id=run_id)
    s.activity.get_run_settings(uuid=activity_id, run_id=run_id)
    s.activity.get_run_settings(name=activity_name, run_id=run_id)
    s.activity.get_run_settings(name=activity_name, run_id=run_id)


def test_create_delete_get_activities():
    """
    Makes various calls to the activity metadata API to create, delete and get activities in different ways.
    """

    new_activity_name = 'new_'+activity_name
    n_activities_before = len(s.activity.get_activities())

    activity = s.activity.create_activity(name=new_activity_name)
    
    new_activity_id = activity['id']

    assert activity['name'] == 'new_'+activity_name
    assert activity['runs'] == []

    n_activities_mid = len(s.activity.get_activities())
    assert n_activities_mid == n_activities_before + 1

    s.set_menu_path(menu_path='test_activity')

    n_activities_mid = len(s.activity.get_activities())
    assert n_activities_mid == n_activities_before + 1

    s.activity.delete_activity(uuid=new_activity_id)

    n_activities_after = len(s.activity.get_activities())

    assert n_activities_before == n_activities_after

    t = MyTestCase()
    t.activity_doesnt_exist(new_activity_name)


def test_update_activity():
    """
    Makes various calls to the activity metadata API to update activities.
    """
    new_activity_name = 'new_'+activity_name

    n_activities_before = len(s.activity.get_activities())

    activity = s.activity.create_activity(name=new_activity_name)

    new_activity_id = activity['id']

    assert activity['name'] == new_activity_name

    s.activity.update_activity(uuid=new_activity_id, new_name='updated '+new_activity_name)

    assert not s.activity.get_activity(name=new_activity_name)
    assert s.activity.get_activity(name='updated '+new_activity_name)
    assert s.activity.create_activity(name=new_activity_name)
    t = MyTestCase()
    t.cant_create_activity(new_activity_name)

    s.activity.delete_activity(uuid=new_activity_id)
    s.activity.delete_activity(name=new_activity_name)

    n_activities_after = len(s.activity.get_activities())

    assert n_activities_before == n_activities_after


def test_create_get_runs():
    """
    Makes various calls to the activity metadata API to create, and get runs.
    """
    new_activity_name = 'new_'+activity_name
    activity = s.activity.create_activity(name=new_activity_name)
    new_activity_id = activity['id']

    assert activity['name'] == new_activity_name
    assert activity['runs'] == []

    run1 = s.activity.create_run(name=new_activity_name)
    run2 = s.activity.create_run(uuid=new_activity_id)
    run3 = s.activity.create_run(name=new_activity_name)

    activity = s.activity.get_activity(uuid=new_activity_id, how_many_runs=1)

    assert activity['name'] == new_activity_name
    assert len(activity['runs']) == 1
    assert activity['runs'][0]['id'] in [run1['id'], run2['id'], run3['id']]

    activity = s.activity.get_activity(name=new_activity_name, how_many_runs=3)
    activities_run_ids = [run['id'] for run in activity['runs']]

    assert activity['name'] == new_activity_name
    assert len(activity['runs']) == 3
    assert run1['id'] in activities_run_ids
    assert run2['id'] in activities_run_ids
    assert run3['id'] in activities_run_ids

    # delete the activity and test that it doesn't exist
    s.activity.delete_activity(name=new_activity_name)

    t = MyTestCase()
    t.activity_doesnt_exist(new_activity_name)


def test_create_get_run_logs():
    """
    Makes various calls to the activity metadata API to create, and get logs.
    """
    new_activity_name = 'new_'+activity_name
    activity = s.activity.create_activity(name=new_activity_name)
    new_activity_id = activity['id']

    assert activity['name'] == new_activity_name
    assert activity['runs'] == []

    run = s.activity.create_run(name=new_activity_name)

    log1 = s.activity.create_run_log(name=new_activity_name, run_id=run['id'],
                                     message='test message 1', severity='INFO')
    log2 = s.activity.create_run_log(uuid=new_activity_id, run_id=run['id'],
                                     message='test message 2', severity='DEBUG', tags={'tag1': 'tag1', 'tag2': 'tag2'})
    log3 = s.activity.create_run_log(name=new_activity_name, run_id=run['id'],
                                     message='test message 3', severity='ERROR', tags={'tag1': 'tag1'})

    activity = s.activity.get_activity(name=new_activity_name, how_many_runs=1)
    run = activity['runs'][0]
    logs = s.activity.get_run_logs(uuid=new_activity_id, run_id=run['id'])

    # test that the logs are in the correct order, they are ordered by creation time
    assert len(logs) == 3
    assert log1 == logs[0]
    assert log2 == logs[1]
    assert log3 == logs[2]

    # delete the activity and test that it doesn't exist
    s.activity.delete_activity(name=new_activity_name)

    t = MyTestCase()
    t.activity_doesnt_exist(new_activity_name)


def test_default_activity_settings():
    """
    Tests that the default settings are being set and used correctly.
    """
    new_activity_name = 'new_' + activity_name
    # test that the default settings are being set
    settings = {'name': 'test1', 'value': 'test1'}
    activity = s.activity.create_activity(name=new_activity_name, settings=settings)

    assert activity['settings'] == settings

    # test that the default settings persist in the API
    s.set_menu_path(menu_path='test_activity')

    activity = s.activity.get_activity(uuid=activity['id'])
    assert activity['settings'] == settings

    # delete the activity and test that it doesn't exist
    s.activity.delete_activity(name=new_activity_name)

    t = MyTestCase()
    t.activity_doesnt_exist(new_activity_name)


def test_get_run_logs():
    """
    Makes various calls to the activity metadata API to create, and get logs.
    """
    new_activity_name = 'new_'+activity_name
    activity = s.activity.create_activity(name=new_activity_name)
    new_activity_id = activity['id']

    run = s.activity.create_run(name=new_activity_name)

    log1 = s.activity.create_run_log(name=new_activity_name, run_id=run['id'],
                                     message='test message 1', severity='INFO')
    log2 = s.activity.create_run_log(uuid=new_activity_id, run_id=run['id'],
                                     message='test message 2', severity='DEBUG', tags={'tag1': 'tag1', 'tag2': 'tag2'})
    log3 = s.activity.create_run_log(name=new_activity_name, run_id=run['id'],
                                     message='test message 3', severity='ERROR', tags={'tag1': 'tag1'})

    activity = s.activity.get_activity(name=new_activity_name, how_many_runs=1)
    run = activity['runs'][0]

    # test that the logs can be retrieved by run id
    logs = s.activity.get_run_logs(uuid=new_activity_id, run_id=run['id'])
    assert len(logs) == 3
    assert log1 == logs[0]
    assert log2 == logs[1]
    assert log3 == logs[2]

    # delete the activity and test that it doesn't exist
    s.activity.delete_activity(name=new_activity_name)

    t = MyTestCase()
    t.activity_doesnt_exist(new_activity_name)


def test_execute_activity():
    """
    Executes an activity and tests that the activity and run are created, also tests that the run has a log and that the
    settings are being passed correctly.
    The activity must have a webhook linked for it to work.
    """
    run = s.activity.execute_activity(name=activity_name)

    activity = s.activity.get_activity(name=activity_name, how_many_runs=1)

    # Runs are ordered by execution time, so the first run is the most recently executed
    assert activity['runs'][0]['id'] == run['id']
    assert len(activity['runs'][0]['logs']) == 1

    settings = [{'name': 'test1', 'value': 'test1'}, {'name': 'test2', 'value': 'test2'}]

    run1 = s.activity.execute_activity(name=activity_name, run_settings=settings[0])
    run2 = s.activity.execute_activity(name=activity_name, run_settings=settings[1])
    run3 = s.activity.create_run(name=activity_name, settings=run2['id'])
    s.activity.execute_run(name=activity_name, run_id=run3['id'])

    activity = s.activity.get_activity(name=activity_name, how_many_runs=4)

    assert activity['runs'][0]['id'] == run['id']
    assert activity['runs'][0]['settings'] == {}
    assert len(activity['runs'][0]['logs']) == 1
    assert activity['runs'][1]['id'] == run1['id']
    assert activity['runs'][1]['settings'] == settings[0]
    assert len(activity['runs'][1]['logs']) == 1
    assert activity['runs'][2]['id'] == run2['id']
    assert activity['runs'][2]['settings'] == settings[1]
    assert len(activity['runs'][2]['logs']) == 1
    assert activity['runs'][3]['id'] == run3['id']
    assert activity['runs'][3]['settings'] == settings[1]
    assert len(activity['runs'][3]['logs']) == 1


def test_button_and_form_execute_activity():
    """
    Creates a button in the dashboard with the capability to execute an activity.
    """
    menu_path = 'test-activity'

    s.plt.button_execute_activity(
        activity_name=activity_name, order=0, label='test_button',
        cols_size=12, align='start', menu_path=menu_path
    )
    s.plt.button_execute_activity(
        activity_name=activity_name, order=1, label='test_button',
        cols_size=12, align='center', menu_path=menu_path
    )
    s.plt.button_execute_activity(
        activity_name=activity_name, order=2, label='test_button',
        rows_size=2, cols_size=12, align='right', menu_path=menu_path
    )

    for i in range(6):
        s.plt.button_execute_activity(
            activity_name=activity_name, order=3+i, label='test_button',
            rows_size=2, cols_size=12-i*2, align='stretch', padding=f'0,{i},0,{i}',
            menu_path=menu_path
        )

    s.plt.button_execute_activity(
        activity_name=activity_name, order=9, label='test_button',
        cols_size=12, align='center', menu_path=menu_path
    )

    form_sent = (
        "<head>"
        "<style>"  # Styles title
        ".component-title{height:auto; width:100%; "
        "border-radius:16px; padding:16px;"
        "display:flex; align-items:center;"
        "background-color:var(--chart-C1); color:var(--color-white);}"
        "<style>.base-white{color:var(--color-white);}</style>"
        "</head>"  # Styles subtitle
        "<div class='component-title'>"
        "<div class='big-icon-banner'></div>"
        "<div class='text-block'>"
        "<h1>The activity has been called</h1>"
        "<p class='base-white'>"
        "Activity Test</p>"
        "</div>"
        "</div>"
    )

    s.plt.html(
        html=form_sent, modal_name='Activity called', order=0, menu_path=menu_path
    )

    form_groups = {
        'Personal information': [
            {
                'mapping': 'name',
                'fieldName': 'name',
                'inputType': 'text',
            },
        ]
    }

    s.plt.generate_input_form_groups(
        order=10, menu_path=menu_path,
        form_groups=form_groups,
        acivity_name_to_call_on_submit=activity_name,
        modal_to_open_on_submit='Activity called',
    )
    if async_execution:
        s.activate_async_execution()


if __name__ == '__main__':
    delete_new_activity_if_it_exists()
    test_get_run_settings()
    test_create_delete_get_activities()
    test_update_activity()
    test_create_get_runs()
    test_create_get_run_logs()
    test_default_activity_settings()
    test_get_run_logs()
    test_execute_activity()
    test_button_and_form_execute_activity()
    s.activity.get_activities(pretty_print=True)
