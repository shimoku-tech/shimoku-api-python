""""""
from os import getenv
import inspect

import shimoku_api_python as shimoku


api_key: str = getenv('API_TOKEN')
universe_id: str = getenv('UNIVERSE_ID')
business_id: str = getenv('BUSINESS_ID')
environment: str = getenv('ENVIRONMENT')
verbosity: str = getenv('VERBOSITY')


s = shimoku.Client(
    access_token=api_key,
    universe_id=universe_id,
    environment=environment,
    verbosity=verbosity
)
s.set_workspace(uuid=business_id)

s.activate_async_execution()

components = [f for _, f in s.html_components.__dict__.items() if callable(f)]

parameters = dict(
    background_url="https://images.unsplash.com/photo-1553356084-58ef4a67b2a7?ixlib=rb-4.0.3&ixid=MnwxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8&auto=format&fit=crop&w=774&q=80",
    background="https://images.unsplash.com/photo-1553356084-58ef4a67b2a7?ixlib=rb-4.0.3&ixid=MnwxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8&auto=format&fit=crop&w=774&q=80",
    image="https://images.unsplash.com/photo-1553356084-58ef4a67b2a7?ixlib=rb-4.0.3&ixid=MnwxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8&auto=format&fit=crop&w=774&q=80",
    image_option='animated',
    title="Lorem ipsum",
    subtitle="Lorem ipsum dolor sit amet",
    href="https://shimoku.com",
    text='Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore ' \
           'et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut ' \
           'aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum ' \
           'dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia ' \
           'deserunt mollit anim id est laborum.',
    main_text='Lorem ipsum',
    internal_text='Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore ' \
              'et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut ' \
              'aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum ' \
              'dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia ' \
              'deserunt mollit anim id est laborum.',
    note='Lorem ipsum',
    button_panel='Lorem ipsum',
    button_text="Lorem ipsum",
    symbol_name='insights',
    h1="Lorem ipsum",
    line="Lorem ipsum",
    modal_title="Lorem ipsum",
    background_color='var(--color-primary)',
)

for component_function in components:
    function_signature = inspect.signature(component_function)
    call_parameters = {parameter[0]: parameter[1]
                       for parameter in parameters.items() if parameter[0] in function_signature.parameters}
    print(component_function)
    print(function_signature.parameters)
    #If the parameters dont exist in the function signature, skip it
    if not call_parameters:
        continue
    print(f'passed {component_function.__name__}')
    html = component_function(**call_parameters)
    s.set_menu_path(f"Components test", f"{component_function.__name__}")
    s.plt.html(html=html, order=0)

s.run()
