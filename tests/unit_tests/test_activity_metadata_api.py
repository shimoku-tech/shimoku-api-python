from os import getenv
from shimoku_api_python.exceptions import ActivityError, CacheError
import unittest
from utils import initiate_shimoku

s = initiate_shimoku()
business_id: str = getenv('BUSINESS_ID')
mock: bool = getenv('MOCK') == 'TRUE'
async_execution: bool = getenv('ASYNC_EXECUTION') == 'TRUE'

s.set_workspace(uuid=business_id)
s.set_menu_path('test_activity')

activity_name = 'test_activity'

_activity = s.activities.get_activity(name=activity_name)
if not _activity:
    _activity = s.activities.create_activity(name=activity_name)

activity_id = _activity['id']
run_id = s.activities.create_run(uuid=activity_id)['id']


def delete_new_activity_if_it_exists():
    """
    Deletes the activity created in the test_create_delete_get_activities test.
    """
    try:
        s.activities.delete_activity(name='new_' + activity_name)
    except ActivityError:
        pass


class TestActivity(unittest.TestCase):

    def test_get_run_settings(self):
        """
        Makes a call to the activity metadata API to get run settings.
        """
        s.activities.get_run_settings(uuid=activity_id, run_id=run_id)
        s.activities.get_run_settings(uuid=activity_id, run_id=run_id)
        s.activities.get_run_settings(name=activity_name, run_id=run_id)
        s.activities.get_run_settings(name=activity_name, run_id=run_id)

    def test_create_delete_get_activities(self):
        """
        Makes various calls to the activity metadata API to create, delete and get activities in different ways.
        """

        new_activity_name = '0_new_'+activity_name
        n_activities_before = len(s.activities.get_activities())

        activity = s.activities.create_activity(name=new_activity_name)

        new_activity_id = activity['id']

        assert activity['name'] ==  new_activity_name
        assert activity['runs'] == []

        n_activities_mid = len(s.activities.get_activities())
        assert n_activities_mid == n_activities_before + 1

        s.set_menu_path(name='test_activity')

        n_activities_mid = len(s.activities.get_activities())
        assert n_activities_mid == n_activities_before + 1

        s.activities.delete_activity(uuid=new_activity_id)

        n_activities_after = len(s.activities.get_activities())

        assert n_activities_before == n_activities_after

        self.activity_doesnt_exist(new_activity_name)

    def test_update_activity(self):
        """
        Makes various calls to the activity metadata API to update activities.
        """
        new_activity_name = '1_new_'+activity_name

        n_activities_before = len(s.activities.get_activities())

        activity = s.activities.create_activity(name=new_activity_name)

        new_activity_id = activity['id']

        assert activity['name'] == new_activity_name

        s.activities.update_activity(uuid=new_activity_id, new_name='updated ' + new_activity_name)

        assert not s.activities.get_activity(name=new_activity_name)
        assert s.activities.get_activity(name='updated ' + new_activity_name)
        assert s.activities.create_activity(name=new_activity_name)
        self.cant_create_activity(new_activity_name)

        s.activities.delete_activity(uuid=new_activity_id)
        s.activities.delete_activity(name=new_activity_name)

        n_activities_after = len(s.activities.get_activities())

        assert n_activities_before == n_activities_after

    def test_create_get_runs(self):
        """
        Makes various calls to the activity metadata API to create, and get runs.
        """
        new_activity_name = '2_new_'+activity_name
        activity = s.activities.create_activity(name=new_activity_name)
        new_activity_id = activity['id']

        assert activity['name'] == new_activity_name
        assert activity['runs'] == []

        run1 = s.activities.create_run(name=new_activity_name)
        run2 = s.activities.create_run(uuid=new_activity_id)
        run3 = s.activities.create_run(name=new_activity_name)

        activity = s.activities.get_activity(uuid=new_activity_id, how_many_runs=1)

        assert activity['name'] == new_activity_name
        assert len(activity['runs']) == 1
        assert activity['runs'][0]['id'] in [run1['id'], run2['id'], run3['id']]

        activity = s.activities.get_activity(name=new_activity_name, how_many_runs=3)
        activities_run_ids = [run['id'] for run in activity['runs']]

        assert activity['name'] == new_activity_name
        assert len(activity['runs']) == 3
        assert run1['id'] in activities_run_ids
        assert run2['id'] in activities_run_ids
        assert run3['id'] in activities_run_ids

        # delete the activity and test that it doesn't exist
        s.activities.delete_activity(name=new_activity_name)

        self.activity_doesnt_exist(new_activity_name)

    def test_create_get_run_logs(self):
        """
        Makes various calls to the activity metadata API to create, and get logs.
        """
        new_activity_name = '3_new_'+activity_name
        activity = s.activities.create_activity(name=new_activity_name)
        new_activity_id = activity['id']

        assert activity['name'] == new_activity_name
        assert activity['runs'] == []

        run = s.activities.create_run(name=new_activity_name)

        log1 = s.activities.create_run_log(name=new_activity_name, run_id=run['id'],
                                           message='test message 1', severity='INFO')
        log2 = s.activities.create_run_log(uuid=new_activity_id, run_id=run['id'],
                                           message='test message 2', severity='DEBUG', tags={'tag1': 'tag1', 'tag2': 'tag2'})
        log3 = s.activities.create_run_log(name=new_activity_name, run_id=run['id'],
                                           message='test message 3', severity='ERROR', tags={'tag1': 'tag1'})

        activity = s.activities.get_activity(name=new_activity_name, how_many_runs=1)
        run = activity['runs'][0]
        logs = s.activities.get_run_logs(uuid=new_activity_id, run_id=run['id'])

        # test that the logs are in the correct order, they are ordered by creation time
        assert len(logs) == 3
        assert log1 == logs[0]
        assert log2 == logs[1]
        assert log3 == logs[2]

        # delete the activity and test that it doesn't exist
        s.activities.delete_activity(name=new_activity_name)

        self.activity_doesnt_exist(new_activity_name)

    def test_default_activity_settings(self):
        """
        Tests that the default settings are being set and used correctly.
        """
        new_activity_name = '4_new_' + activity_name
        # test that the default settings are being set
        settings = {'name': 'test1', 'value': 'test1'}
        activity = s.activities.create_activity(name=new_activity_name, settings=settings)

        assert activity['settings'] == settings

        # test that the default settings persist in the API
        s.set_menu_path(name='test_activity')

        activity = s.activities.get_activity(uuid=activity['id'])
        assert activity['settings'] == settings

        # delete the activity and test that it doesn't exist
        s.activities.delete_activity(name=new_activity_name)

        self.activity_doesnt_exist(new_activity_name)

    def test_get_run_logs(self):
        """
        Makes various calls to the activity metadata API to create, and get logs.
        """
        new_activity_name = '5_new_'+activity_name
        activity = s.activities.create_activity(name=new_activity_name)
        new_activity_id = activity['id']

        run = s.activities.create_run(name=new_activity_name)

        log1 = s.activities.create_run_log(name=new_activity_name, run_id=run['id'],
                                           message='test message 1', severity='INFO')
        log2 = s.activities.create_run_log(uuid=new_activity_id, run_id=run['id'],
                                           message='test message 2', severity='DEBUG', tags={'tag1': 'tag1', 'tag2': 'tag2'})
        log3 = s.activities.create_run_log(name=new_activity_name, run_id=run['id'],
                                           message='test message 3', severity='ERROR', tags={'tag1': 'tag1'})

        activity = s.activities.get_activity(name=new_activity_name, how_many_runs=1)
        run = activity['runs'][0]

        # test that the logs can be retrieved by run id
        logs = s.activities.get_run_logs(uuid=new_activity_id, run_id=run['id'])
        assert len(logs) == 3
        assert log1 == logs[0]
        assert log2 == logs[1]
        assert log3 == logs[2]

        # delete the activity and test that it doesn't exist
        s.activities.delete_activity(name=new_activity_name)

        self.activity_doesnt_exist(new_activity_name)

    def test_execute_activity(self):
        """
        Executes an activity and tests that the activity and run are created, also tests that the run has a log
        and that the settings are being passed correctly. The activity must have a webhook linked for it to work.
        """
        s.activities.create_webhook(name=activity_name, url='https://www.google.com')

        run = s.activities.execute_activity(name=activity_name)
        activity = s.activities.get_activity(name=activity_name, how_many_runs=1)

        # Runs are ordered by execution time, so the first run is the most recently executed
        assert activity['runs'][0]['id'] == run['id']
        assert len(activity['runs'][0]['logs']) == 1 or mock

        settings = [{'name': 'test1', 'value': 'test1'}, {'name': 'test2', 'value': 'test2'}]

        run1 = s.activities.execute_activity(name=activity_name, run_settings=settings[0])
        run2 = s.activities.execute_activity(name=activity_name, run_settings=settings[1])
        run3 = s.activities.create_run(name=activity_name, settings=run2['id'])
        s.activities.execute_run(name=activity_name, run_id=run3['id'])

        activity = s.activities.get_activity(name=activity_name, how_many_runs=4)

        assert activity['runs'][0]['id'] == run['id']
        assert activity['runs'][0]['settings'] == {}
        assert len(activity['runs'][0]['logs']) == 1 or mock
        assert activity['runs'][1]['id'] == run1['id']
        assert activity['runs'][1]['settings'] == settings[0]
        assert len(activity['runs'][1]['logs']) == 1 or mock
        assert activity['runs'][2]['id'] == run2['id']
        assert activity['runs'][2]['settings'] == settings[1]
        assert len(activity['runs'][2]['logs']) == 1 or mock
        assert activity['runs'][3]['id'] == run3['id']
        assert activity['runs'][3]['settings'] == settings[1]
        assert len(activity['runs'][3]['logs']) == 1 or mock

    def test_button_and_form_execute_activity(self):
        """
        Creates a button in the dashboard with the capability to execute an activity.
        """
        s.set_menu_path('test_activity')

        s.plt.activity_button(
            activity_name=activity_name, order=0, label='test_button',
            cols_size=12, align='start',
        )
        s.plt.activity_button(
            activity_name=activity_name, order=1, label='test_button',
            cols_size=12, align='center'
        )
        s.plt.activity_button(
            activity_name=activity_name, order=2, label='test_button',
            rows_size=2, cols_size=12, align='right'
        )

        for i in range(6):
            s.plt.activity_button(
                activity_name=activity_name, order=3+i, label='test_button',
                rows_size=2, cols_size=12-i*2, align='stretch', padding=f'0,{i},0,{i}'
            )

        s.plt.activity_button(
            activity_name=activity_name, order=9, label='test_button',
            cols_size=12, align='center'
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

        s.plt.set_modal(modal_name='Activity called')
        s.plt.html(html=form_sent, order=0)
        s.plt.pop_out_of_modal()

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
            order=10, form_groups=form_groups,
            activity_name=activity_name,
            modal='Activity called',
        )
        if async_execution:
            s.activate_async_execution()

    def activity_doesnt_exist(self, _activity_name):
        with self.assertRaises(ActivityError):
            s.activities.delete_activity(name=_activity_name)

    def cant_create_activity(self, _activity_name):
        with self.assertRaises(CacheError):
            s.activities.create_activity(name=_activity_name)
