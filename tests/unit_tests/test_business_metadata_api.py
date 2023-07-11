""""""
from os import getenv
from typing import Dict, List
from shimoku_api_python.exceptions import WorkspaceError, CacheError

import unittest

from tenacity import RetryError
from utils import initiate_shimoku

s = initiate_shimoku()

business_id: str = getenv('BUSINESS_ID')
mock: bool = getenv('MOCK') == 'TRUE'


class TestBusinesses(unittest.TestCase):

    def test_get_business(self):
        result = s.workspaces.get_workspace(uuid=business_id)
        assert result

    def test_get_fake_business(self):
        if not mock:
            with self.assertRaises(RetryError):
                s.workspaces.get_workspace(
                    uuid='this is a test',
                )

    def test_create_and_delete_business(self):
        if s.workspaces.get_workspace(name='auto-test'):
            s.workspaces.delete_workspace(name='auto-test')

        business: Dict = s.workspaces.create_workspace(name='auto-test')
        business_id_: str = business['id']

        assert len(business_id_) > 0

        business_from_db: Dict = (
            s.workspaces.get_workspace(
                uuid=business_id_,
            )
        )

        business_roles = s.workspaces.get_roles(name='auto-test')

        assert len(business_roles) == 4
        resources = ['DATA', 'DATA_EXECUTION', 'USER_MANAGEMENT', 'BUSINESS_INFO']
        for role in business_roles:
            assert role['role'].startswith('business_read_')
            assert role['permission'] == 'READ'
            assert role['resource'] in resources
            assert role['target'] == 'GROUP'
            resources.remove(role['resource'])

        assert {
            k: v
            for k, v in business_from_db.items()
            if k in [
                'id', 'name',
                'universe', '__typename',
            ]
        } == {
            k: v
            for k, v in business.items()
            if k in [
                'id', 'name',
                'universe', '__typename',
            ]
        }
        del business_from_db

        s.workspaces.delete_workspace(uuid=business_id_)

        if not mock:
            with self.assertRaises(RetryError):
                s.workspaces.get_workspace(
                    uuid=business_id_,
                )

    def test_theme_customization(self):
        s.workspaces.update_workspace(
            uuid=business_id,
            theme={},
        )
        business: Dict = s.workspaces.get_workspace(uuid=business_id)

        assert business['theme'] == {}

        theme = {
            "palette": {
                "primary": {
                    "main": "#0f530b",
                },
            },
            "typography": {
                "h1": {
                    "fontSize": "60px",
                },
            },
            "custom": {
                "radius": {
                    "xs": "0px",
                    "s": "0px",
                    "m": "0px",
                    "l": "0px",
                    "xl": "0px"
                },
                "logo": "https://flaxandkale.com/img/logo-flaxandkale-black.png",
            }
        }

        s.workspaces.update_workspace(uuid=business_id, theme=theme)

        business: Dict = s.workspaces.get_workspace(uuid=business_id)

        assert business['theme'] == theme

    def test_update_business(self):
        business_original: Dict = s.workspaces.get_workspace(uuid=business_id)

        business_name: str = business_original['name']
        new_business_name: str = f'{business_name}_changed'

        s.workspaces.update_workspace(
            uuid=business_id,
            new_name=new_business_name,
        )

        new_business: Dict = s.workspaces.get_workspace(uuid=business_id)

        business_changed: Dict = s.workspaces.get_workspace(name=new_business_name)
        assert {
            k: v
            for k, v in business_changed.items()
            if k in [
                'id', 'name',
                'universe', '__typename',
            ]
        } == {
            k: v
            for k, v in new_business.items()
            if k in [
                'id', 'name',
                'universe', '__typename',
            ]
        }
        assert new_business_name == business_changed['name']

        # Restore previous name
        s.workspaces.update_workspace(name=new_business_name, new_name=business_name)

        business_restored: Dict = s.workspaces.get_workspace(name=business_name)
        assert business_name == business_restored['name']

    def test_get_business_apps(self):
        s.set_workspace(uuid=business_id)
        how_many_apps = len(s.workspaces.get_workspace_menu_paths(uuid=business_id))
        s.menu_paths.get_menu_path(name='business_app_test')
        apps: List[Dict] = s.workspaces.get_workspace_menu_paths(uuid=business_id)
        assert len(apps) == how_many_apps + 1
        s.menu_paths.delete_menu_path(name='business_app_test')
        apps: List[Dict] = s.workspaces.get_workspace_menu_paths(uuid=business_id)
        assert len(apps) == how_many_apps

    def test_cant_create_business_with_similar_name(self):
        if s.workspaces.get_workspace(name='auto-test'):
            s.workspaces.delete_workspace(name='auto-test')

        s.workspaces.create_workspace(name='auto-test')

        class SimilarBusinessCase(unittest.TestCase):
            def test_create_similar(self):
                with self.assertRaises(WorkspaceError):
                    s.workspaces.create_workspace(
                        name='auto-TEST',
                    )

            def test_update_similar(self):
                with self.assertRaises(WorkspaceError):
                    s.workspaces.update_workspace(
                        name='auto-test',
                        new_name='auto-TEST',
                    )
        sbc = SimilarBusinessCase()
        sbc.test_create_similar()
        sbc.test_update_similar()
        s.workspaces.delete_workspace(name='auto-test')

    def test_cant_get_with_id_and_name(self):
        if s.workspaces.get_workspace(name='auto-test'):
            s.workspaces.delete_workspace(name='auto-test')

        wid = s.workspaces.create_workspace(name='auto-test')['id']

        with self.assertRaises(CacheError):
            s.set_workspace(uuid=wid, name='auto-test')
