from os import getenv
import shimoku_api_python as shimoku
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
menu_path = 'test-activities'
activity_name = 'test_activity'


class MyTestCase(unittest.TestCase):
    def activity_doesnt_exist(self, _menu_path, _activity_name):
        with self.assertRaises(RuntimeError):
            s.activity.get_activity(menu_path=_menu_path, activity_name=_activity_name)


def test_create_delete_get_activities():
    """
    Makes various calls to the activity metadata API to create, delete and get activities in different ways.
    """

    new_activity_name = 'new_'+activity_name
    n_activities_before = len(s.activity.get_activities(menu_path=menu_path))

    s.activity.create_activity(menu_path=menu_path, activity_name=new_activity_name)
    activity = s.activity.get_activity(menu_path=menu_path, activity_name=new_activity_name)

    assert activity['name'] == 'new_'+activity_name
    assert activity['runs'] == []

    n_activities_mid = len(s.activity.get_activities(menu_path=menu_path))
    assert n_activities_mid == n_activities_before + 1

    s.activity.set_business(business_id)

    n_activities_mid = len(s.activity.get_activities(menu_path=menu_path))
    assert n_activities_mid == n_activities_before + 1

    s.activity.delete_activity(menu_path=menu_path, activity_name=new_activity_name)

    n_activities_after = len(s.activity.get_activities(menu_path=menu_path))

    assert n_activities_before == n_activities_after

    t = MyTestCase()
    t.activity_doesnt_exist(menu_path, new_activity_name)


def test_create_get_runs():
    """
    Makes various calls to the activity metadata API to create, and get runs.
    """
    new_activity_name = 'new_'+activity_name
    activity = s.activity.create_activity(menu_path=menu_path, activity_name=new_activity_name)

    assert activity['name'] == new_activity_name
    assert activity['runs'] == []

    run1 = s.activity.create_run(menu_path=menu_path, activity_name=new_activity_name)
    run2 = s.activity.create_run(menu_path=menu_path, activity_name=new_activity_name)
    run3 = s.activity.create_run(menu_path=menu_path, activity_name=new_activity_name)

    # Test default how_many_runs, which is 1, and that the run is the most recent one
    activity = s.activity.get_activity(menu_path=menu_path, activity_name=new_activity_name)

    assert activity['name'] == new_activity_name
    assert len(activity['runs']) == 1
    assert activity['runs'][0]['id'] == run3['id']

    # Test how_many_runs=3, the order of the runs is the same as the order they were created
    activity = s.activity.get_activity(menu_path=menu_path, activity_name=new_activity_name, how_many_runs=3)

    assert activity['name'] == new_activity_name
    assert len(activity['runs']) == 3
    assert run1['id'] in activity['runs'][0]['id']
    assert run2['id'] in activity['runs'][1]['id']
    assert run3['id'] in activity['runs'][2]['id']

    # delete the activity and test that it doesn't exist
    s.activity.delete_activity(menu_path=menu_path, activity_name=new_activity_name)

    t = MyTestCase()
    t.activity_doesnt_exist(menu_path, new_activity_name)


def test_execute_activity():
    """
    Executes an activity and tests that the activity and run are created. The activity must have a webhook linked for
    it to work.
    """




test_create_delete_get_activities()
test_create_get_runs()
