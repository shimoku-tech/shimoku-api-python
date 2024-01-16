from os import getenv
import unittest
from utils import initiate_shimoku

s = initiate_shimoku()

business_id: str = getenv('BUSINESS_ID')
s.set_workspace(uuid=business_id)


class TestRoles(unittest.TestCase):

    def test_business_roles(self):

        role = s.workspaces.get_role(uuid=business_id, role_name='test_role')
        if role:
            s.workspaces.delete_role(uuid=business_id, role_id=role['id'])

        previous_roles_size = len(s.workspaces.get_roles(uuid=business_id))
        role = s.workspaces.create_role(uuid=business_id, role_name='test_role')
        assert role['role'] == 'test_role'
        assert role['permission'] == 'READ'
        assert role['resource'] == 'BUSINESS_INFO'
        assert role['target'] == 'GROUP'

        roles = s.workspaces.get_roles(uuid=business_id)

        assert len(roles) == previous_roles_size + 1

        s.workspaces.delete_role(uuid=business_id, role_id=role['id'])

        assert len(s.workspaces.get_roles(uuid=business_id)) == previous_roles_size

        s.workspaces.create_role(uuid=business_id, role_name='test_role', permission='WRITE',
                                 resource='DATA', target='USER')

        role = [role_ for role_ in s.workspaces.get_roles(uuid=business_id) if role_['role'] == 'test_role'][0]

        assert role['permission'] == 'WRITE'
        assert role['resource'] == 'DATA'
        assert role['target'] == 'USER'

        assert len(s.workspaces.get_roles(uuid=business_id)) == previous_roles_size + 1

        s.workspaces.delete_role(uuid=business_id, role_id=role['id'])

    def test_dashboard_roles(self):
        dashboard_name = 'roles_dashboard'
        dashboard = s.boards.get_board(name=dashboard_name)
        if not dashboard:
            dashboard = s.boards.create_board(name=dashboard_name)

        role = s.boards.get_role(name=dashboard_name, role_name='test_role')
        if role:
            s.boards.delete_role(name=dashboard_name, role_id=role['id'])

        role = s.boards.create_role(name=dashboard_name, role_name='test_role')
        assert role['role'] == 'test_role'
        assert role['permission'] == 'READ'
        assert role['resource'] == 'BUSINESS_INFO'
        assert role['target'] == 'GROUP'

        roles = s.boards.get_roles(name=dashboard_name)

        assert len(roles) == 1
        assert roles[0]['role'] == 'test_role'

        s.boards.delete_role(name=dashboard_name, role_id=role['id'])

        assert len(s.boards.get_roles(name=dashboard_name)) == 0

        s.boards.create_role(name=dashboard_name, role_name='test_role', permission='WRITE',
                             resource='DATA', target='USER')

        role = s.boards.get_roles(name=dashboard_name)[0]

        assert role['role'] == 'test_role'
        assert role['permission'] == 'WRITE'
        assert role['resource'] == 'DATA'
        assert role['target'] == 'USER'

        assert len(s.boards.get_roles(name=dashboard_name)) == 1

        s.boards.delete_board(uuid=dashboard['id'])

    def test_app_roles(self):
        app = s.menu_paths.get_menu_path(name='roles_app')

        role = s.menu_paths.get_role(uuid=app['id'], role_name='test_role')
        if role:
            s.menu_paths.delete_role(uuid=app['id'], role_id=role['id'])

        role = s.menu_paths.create_role(uuid=app['id'], role_name='test_role')
        assert role['role'] == 'test_role'
        assert role['permission'] == 'READ'
        assert role['resource'] == 'BUSINESS_INFO'
        assert role['target'] == 'GROUP'

        roles = s.menu_paths.get_roles(uuid=app['id'])

        assert len(roles) == 1
        assert roles[0]['role'] == 'test_role'

        s.menu_paths.delete_role(uuid=app['id'], role_id=role['id'])

        assert len(s.menu_paths.get_roles(uuid=app['id'])) == 0

        s.menu_paths.create_role(uuid=app['id'], role_name='test_role', permission='WRITE', resource='DATA', target='USER')

        role = s.menu_paths.get_roles(uuid=app['id'])[0]

        assert role['role'] == 'test_role'
        assert role['permission'] == 'WRITE'
        assert role['resource'] == 'DATA'
        assert role['target'] == 'USER'

        assert len(s.menu_paths.get_roles(uuid=app['id'])) == 1

        s.menu_paths.delete_menu_path(uuid=app['id'])
