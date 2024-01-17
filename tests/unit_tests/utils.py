from os import getenv
import shimoku_api_python as shimoku
from mock_classes import MockClient


def initiate_shimoku():
    # return shimoku.Client(
    #     verbosity='INFO',
    #     async_execution=True,
    # )
    api_key: str = getenv('API_TOKEN')
    universe_id: str = getenv('UNIVERSE_ID')
    environment: str = getenv('ENVIRONMENT')
    verbose: str = getenv('VERBOSITY')
    mock: bool = getenv('MOCK') == 'TRUE'
    async_execution: bool = getenv('ASYNC_EXECUTION') == 'TRUE'
    playground: bool = getenv('PLAYGROUND') == 'TRUE'
    local_port: int = int(getenv('LOCAL_PORT'))

    if playground:
        s = shimoku.Client(
            environment=environment,
            verbosity=verbose,
            async_execution=async_execution,
            local_port=local_port,
            retry_attempts=1
        )
    elif mock:
        s = MockClient(
            verbosity=verbose,
            async_execution=async_execution,
        )
    else:
        s = shimoku.Client(
            access_token=api_key,
            universe_id=universe_id,
            environment=environment,
            verbosity=verbose,
            async_execution=async_execution,
            retry_attempts=1
        )

    return s
