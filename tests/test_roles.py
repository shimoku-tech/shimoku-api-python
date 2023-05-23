from os import getenv
import shimoku_api_python as shimoku
import unittest

api_key: str = getenv('API_TOKEN')
universe_id: str = getenv('UNIVERSE_ID')
business_id: str = getenv('BUSINESS_ID')
environment: str = getenv('ENVIRONMENT')
verbose: str = getenv('VERBOSITY')
async_execution: bool = False


s = shimoku.Client(
    access_token=api_key,
    universe_id=universe_id,
    environment=environment,
    verbosity=verbose,
    async_execution=async_execution,
)
s.set_business(uuid=business_id)


class TestRoles(unittest.TestCase):

    def test_business_roles(self):

        role = s.business.get_role(uuid=business_id, role_name='test_role')
        if role:
            s.business.delete_role(uuid=business_id, role_id=role['id'])

        role = s.business.create_role(uuid=business_id, role_name='test_role')
        assert role['role'] == 'test_role'
        assert role['permission'] == 'READ'
        assert role['resource'] == 'BUSINESS_INFO'
        assert role['target'] == 'GROUP'

        roles = s.business.get_roles(uuid=business_id)

        assert len(roles) == 1
        assert roles[0]['role'] == 'test_role'

        s.business.delete_role(uuid=business_id, role_id=role['id'])

        assert len(s.business.get_roles(uuid=business_id)) == 0

        s.business.create_role(uuid=business_id, role_name='test_role', permission='WRITE',
                               resource='DATA', target='USER')

        role = s.business.get_roles(uuid=business_id)[0]

        assert role['role'] == 'test_role'
        assert role['permission'] == 'WRITE'
        assert role['resource'] == 'DATA'
        assert role['target'] == 'USER'

        assert len(s.business.get_roles(uuid=business_id)) == 1

        s.business.delete_role(uuid=business_id, role_id=role['id'])

    def test_dashboard_roles(self):
        dashboard_name = 'roles_dashboard'
        dashboard = s.dashboard.get_dashboard(name=dashboard_name)
        if not dashboard:
            dashboard = s.dashboard.create_dashboard(name=dashboard_name)

        role = s.dashboard.get_role(name=dashboard_name, role_name='test_role')
        if role:
            s.dashboard.delete_role(name=dashboard_name, role_id=role['id'])

        role = s.dashboard.create_role(name=dashboard_name, role_name='test_role')
        assert role['role'] == 'test_role'
        assert role['permission'] == 'READ'
        assert role['resource'] == 'BUSINESS_INFO'
        assert role['target'] == 'GROUP'

        roles = s.dashboard.get_roles(name=dashboard_name)

        assert len(roles) == 1
        assert roles[0]['role'] == 'test_role'

        s.dashboard.delete_role(name=dashboard_name, role_id=role['id'])

        assert len(s.dashboard.get_roles(name=dashboard_name)) == 0

        s.dashboard.create_role(name=dashboard_name, role_name='test_role', permission='WRITE',
                                resource='DATA', target='USER')

        role = s.dashboard.get_roles(name=dashboard_name)[0]

        assert role['role'] == 'test_role'
        assert role['permission'] == 'WRITE'
        assert role['resource'] == 'DATA'
        assert role['target'] == 'USER'

        assert len(s.dashboard.get_roles(name=dashboard_name)) == 1

        s.dashboard.delete_dashboard(uuid=dashboard['id'])

    def test_app_roles(self):
        app = s.app.get_app(menu_path='roles_app')

        role = s.app.get_role(uuid=app['id'], role_name='test_role')
        if role:
            s.app.delete_role(uuid=app['id'], role_id=role['id'])

        role = s.app.create_role(uuid=app['id'], role_name='test_role')
        assert role['role'] == 'test_role'
        assert role['permission'] == 'READ'
        assert role['resource'] == 'BUSINESS_INFO'
        assert role['target'] == 'GROUP'

        roles = s.app.get_roles(uuid=app['id'])

        assert len(roles) == 1
        assert roles[0]['role'] == 'test_role'

        s.app.delete_role(uuid=app['id'], role_id=role['id'])

        assert len(s.app.get_roles(uuid=app['id'])) == 0

        s.app.create_role(uuid=app['id'], role_name='test_role', permission='WRITE', resource='DATA', target='USER')

        role = s.app.get_roles(uuid=app['id'])[0]

        assert role['role'] == 'test_role'
        assert role['permission'] == 'WRITE'
        assert role['resource'] == 'DATA'
        assert role['target'] == 'USER'

        assert len(s.app.get_roles(uuid=app['id'])) == 1

        s.app.delete_app(uuid=app['id'])
