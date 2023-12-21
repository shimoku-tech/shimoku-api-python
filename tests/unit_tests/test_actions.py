from shimoku.actions.execute_action import execute_action
from shimoku.exceptions import ActionError
import unittest


class TestActions(unittest.TestCase):

    def test_action(self):
        action_code = """
from shimoku import Client
import shimoku

class UsesClient:

    def __init__(self):
        print('This should work')

    def use_s(self, shimoku_client: Client):
        shimoku_client.set_workspace()
        shimoku_client.set_menu_path('Pyodide test')
        shimoku_client.plt.gauge_indicator(
            order=2,
            value=len(shimoku_client.menu_paths.get_menu_path_components(name='test-free-echarts')),
            description='Trying to get the number of components',
            title='Pyodide test',
        )

def deep_no_use_s(shimoku_client: Client):
    pass

def no_use_s(shimoku_client: Client):
    deep_no_use_s(shimoku_client)

def deep_deep_use_s():
    shimoku_client.set_workspace()
    shimoku_client.set_menu_path('Pyodide test')
    shimoku_client.plt.gauge_indicator(
        order=2,
        value=len(shimoku_client.menu_paths.get_menu_path_components(name='test-free-echarts')),
        description='Trying to get the number of components',
        title='Pyodide test',
    )
         
def use_s(shimoku_client: Client):
    def deep_use_s():
        deep_deep_use_s()
    deep_use_s()

def action(shimoku_client: Client):
    shimoku_client._async_pool.ACTIONS_TEST = True
    print('This should work')
    no_use_s(shimoku_client)
    use_s(shimoku_client)

    uses_shimoku_client = UsesClient()
    uses_shimoku_client.use_s(shimoku_client)

    shimoku_client.run()
        """

        execute_action(action_code)

        codes_with_errors = [
            """
from shimoku import Client 

# error, needs to be an 'action' function   
""",
            """
# error, needs to import Client
def action(shimoku_client: Client):
    pass
""",
            """
from shimoku import Client as shimo  # error

def action(shimoku_client: shimo):
    pass
""",
            """
from shimoku import Client
import asyncio  # error

def action(shimoku_client: Client):
    pass
""",
            """
from shimoku import Client
from asyncio import run  # error

def action(shimoku_client: Client):
    pass
""",
            """
from shimoku import Client

shimo = Client()  # error

def action(shimoku_client: Client):
    pass
""",
            """
from shimoku import Client

shimoku_client = 6  # error

def action(shimoku_client: Client):
    pass
""",
            """
from shimoku import Client

class UsesClient:
    def action(shimoku_client: Client):  # error
        pass
""",
            """
from shimoku import Client

def non_action():
    def action(shimoku_client: Client):  # error
        pass
""",
            """
from shimoku import Client

def action(shimoku_client: Client):
    pass

def action(shimoku_client: Client):  # error
    pass
""",
            """
from shimoku import Client

def action(shimoku_client: Client, other_param: int):  # error
    pass
""",
            """
from shimoku import Client

def action():
    pass
""",
            """
from shimoku import Client

def action(shimo: Client):  # error
    pass
""",
            """
from shimoku import Client

def action(shimoku_client: int):  # error
    pass
""",
            """
from shimoku import Client

def action(shimoku_client):
    pass    
""",
            """
from shimoku import Client

def use_s(non_annotated_param): # error
    pass

def action(shimoku_client: Client):
    use_s(shimoku_client)
""",
            """
from shimoku import Client

def use_s(shimo: Client): # error
    pass
""",
            """
from shimoku import Client

def use_s(shimoku_client: Optional[Client] = None): # error
    pass

def action(shimoku_client: Client):
    use_s()
""",
            """
from shimoku import Client

def use_s(shimoku_client: int):
    pass
""",
            """
from shimoku import Client

async def use_s(shimoku_client: Client):  # error
    pass

def action(shimoku_client: Client):
    use_s(shimoku_client)
""",
            """
from shimoku import Client

def use_s(shimoku_client: Client):
    return shimoku_client  # error

def action(shimoku_client: Client):
    use_s(shimoku_client)
""",
            """
from shimoku import Client

def use_s(other_param: int):
    print(other_param)

def action(shimoku_client: Client):
    use_s(shimoku_client)  # error
""",
            """
from shimoku import Client

def use_s(other_param: int):
    pass

def action(shimoku_client: Client):
    use_s(other_param=shimoku_client)  # error
""",
            """
from shimoku import Client

class UsesClient:

    s = Client()  # error
    
    def use_s(self):
        pass

def action(shimoku_client: Client):
    pass
""",
            """
from shimoku import Client

class UsesClient:
    
    def assign_s(shimoku_client: Client):
        clients_dict = {}
        clients_dict['s'] = shimoku_client  # error

def action(shimoku_client: Client):
    uses_shimoku_client = UsesClient()
    uses_shimoku_client.assign_s(shimoku_client)
    
""",
            ]
        for code_with_errors in codes_with_errors:
            print()
            with self.assertRaises(ActionError):
                execute_action(code_with_errors, True)
