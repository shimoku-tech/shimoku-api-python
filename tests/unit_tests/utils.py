from os import getenv
import shimoku_api_python as shimoku
from mock_classes import MockClient


def initiate_shimoku():
    api_key: str = getenv('API_TOKEN')
    universe_id: str = getenv('UNIVERSE_ID')
    environment: str = getenv('ENVIRONMENT')
    verbose: str = getenv('VERBOSITY')
    mock: bool = getenv('MOCK') == 'TRUE'
    async_execution: bool = getenv('ASYNC_EXECUTION') == 'TRUE'

    if not mock:
        s = shimoku.Client(
            access_token=api_key,
            universe_id=universe_id,
            environment=environment,
            verbosity=verbose,
            async_execution=async_execution,
        )
    else:
        s = MockClient(
            verbosity=verbose,
            async_execution=async_execution,
        )

    return s
