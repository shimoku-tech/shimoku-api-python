# Shimoku Api Python

![License](https://img.shields.io/github/license/shimoku-tech/shimoku-api-python)
[![PyPI version](https://badge.fury.io/py/shimoku-api-python.svg)](https://badge.fury.io/py/shimoku-api-python)
[![Downloads](https://pepy.tech/badge/shimoku-api-python)](https://pepy.tech/project/shimoku-api-python)
[![Discord](https://img.shields.io/discord/1076588792024137879?color=%237289da&label=Discord)](https://discord.com/channels/1076588792024137879/1096371108665626676)
[![Medium](https://img.shields.io/badge/follow%20on-Medium-12100E.svg?style=flat&logo=medium)](https://medium.com/@shimoku)

Shimoku allows you to build Data Products in hours and create Predictive Analytics Products with Artificial Intelligence capabilities.

🌐 [Website](https://www.shimoku.com/) |
📚 [Documentation](https://docs.shimoku.com/) |
📊 [Shimoku App Templates](https://github.com/shimoku-tech/shimoku-app-templates) |

## Quickstart

## Setting Up Your Local Server

Begin your journey with Shimoku by setting up a local server. This process allows you to explore Shimoku's capabilities without needing to log in or create an account.

### Step 1 - Install the Library

To use Shimoku’s API first install our SDK library.

In your `Python +3.9` install it

```python
pip install shimoku-api-python
```

### Step 2 - Initialize the Shimoku SDK

Start by importing Shimoku and initializing the client. This step sets up a local server environment for your development and automatically opens a browser.

```python
import shimoku_api_python as Shimoku

# Client initialization with playground mode
s = Shimoku.Client()
```

![Playground preview](https://1111601832-files.gitbook.io/~/files/v0/b/gitbook-x-prod.appspot.com/o/spaces%2FUlHTfmIZY46Z1EDfyGMz%2Fuploads%2F3a2wED5DrnUeWO5ZEhrf%2FPlayground.png?alt=media&token=865c265d-c754-4a0a-a141-fca0d06197f4)

We recommend the following parameters for a better development experience:

```python
s = Shimoku.Client(
    async_execution=True,  # Grouped plotting
    verbosity='INFO',      # Insight in the execution
)
```

**_NOTE:_**
> If a local server session in a specific port is already active, the SDK will connect to the existing session. There is no need to reinitialize a new server, allowing for continuous work without interruption.

In case the default port (8000) is already in use, it is necessary to change it in the client initialization, for example, the port 8080 could be used:

```python
s = Shimoku.Client(
    local_port=8080
    async_execution=True,
    verbosity='INFO', 
)
```

**_NOTE:_**
>  It is not recommended to have more than one local server running, as the front-end application can only access one at a time (even in different tabs).

To terminate the server the following function has to be used, it will only close the server connected to the client-specified port:

```python
s = Shimoku.Client(
    local_port=8080
    async_execution=True,
    verbosity='INFO', 
)

# Close the server in the port 8080
s.terminate_local_server()
```

### Code Example

When changes are made locally using the s.run() command, the SDK provides immediate feedback to the front end. This live update system ensures developers can see the impact of their changes in real time:

```python
# Necessary for compatibility with cloud execution
s.set_workspace() 

# Set the group of the menu
s.set_board('Custom Board')

# Set the menu path 'catalog' with the sub-path 'bar-example'
s.set_menu_path('catalog', 'bar-example')

language_expressiveness = [
    {'Language': 'C', 'Statements ratio': 1.0, 'Lines ratio': 1.0},
    {'Language': 'C++', 'Statements ratio': 2.5, 'Lines ratio': 1.0},
    {'Language': 'Fortran', 'Statements ratio': 2.0, 'Lines ratio': 0.8},
    {'Language': 'Java', 'Statements ratio': 2.5, 'Lines ratio': 1.5},
    {'Language': 'Perl', 'Statements ratio': 6.0, 'Lines ratio': 6.0},
    {'Language': 'Smalltalk', 'Statements ratio': 6.0, 'Lines ratio': 6.25},
    {'Language': 'Python', 'Statements ratio': 6.0, 'Lines ratio': 6.5},
]

s.plt.bar(
    order=0, title='Language expressiveness',
    data=language_expressiveness, x='Language',
    y=['Statements ratio', 'Lines ratio'],
)

# Necessary for notifying the front-end even if not using async execution
s.run()

```

![First Shimoku App](https://1111601832-files.gitbook.io/~/files/v0/b/gitbook-x-prod.appspot.com/o/spaces%2FUlHTfmIZY46Z1EDfyGMz%2Fuploads%2FY8UtQtoFFIKSE61dJPZU%2FPlayground%20Real%20Time.png?alt=media&token=8a53150b-5e86-4f9f-807c-f55280edc69e)

## Deployment in Cloud

The deployment with the Shimoku platform is very straightforward, just set your credentials in the client initialization and execute the same code you've been developing:

```python
import shimoku_api_python as Shimoku

access_token: str = getenv('API_TOKEN')     # Environment variable
universe_id: str = getenv('UNIVERSE_ID')    # Environment variable
workspace_id: str = getenv('WORKSPACE_ID')  # Environment variable

s = Shimoku.Client(
    access_token=access_token,
    universe_id=universe_id,
    async_execution=True,
    verbosity='INFO'
)

s.set_workspace(workspace_id)

. . .
```

**_NOTE:_**
> If you don't have these credentials you will need to [create an account here](https://shimoku.io/sign-up), consult the [Shimoku Cloud](https://docs.shimoku.com/development/getting-started/shimoku-cloud) for further information.
> It is advisable to make sure that the contents of the playground can be replicated by the code before deploying.

## Sharing Your Insights: Embedding and Beyond

Shimoku's sharing functionality transforms the way you incorporate analytics into web platforms, enabling you to deliver personalized insights to your audience and add significant value to your product offerings with minimal development efforts.

## Creating a Shareable Board

```python
# Updates the specified board fields, if it exists
s.boards.update_board(
    name=your_board_name,
    is_public=True
)
```

And that's it!

Now, to access the link through the Front End, you must click on the chain of your board:

![Shareable Board](https://1111601832-files.gitbook.io/~/files/v0/b/gitbook-x-prod.appspot.com/o/spaces%2FUlHTfmIZY46Z1EDfyGMz%2Fuploads%2FCvd9lhKC7rgnRtJiZna2%2Fimage.png?alt=media&token=bb71cf34-9179-4e09-a339-8d4e77867511)

**_NOTE:_**
> You can read more about our Shared boards by reading this section: [Shared Links](https://docs.shimoku.com/development/building-ai-web-app/shared-links).

## Key Features and Advantages

The Shimoku Playground is an integral feature of the Shimoku platform, designed to facilitate local development.

- **Local Server Utilization**: Instead of connecting to the cloud-based Shimoku API, the Playground operates via a local server. This setup is initialized through the SDK, offering a more immediate and responsive development environment.
- **Consistent API Compatibility**: Code developed within the Playground is fully compatible with the Shimoku API. This ensures a smooth transition from local to cloud-based environments, allowing developers to switch between local and cloud deployments without needing to modify their code.
- **No Token Consumption**: The Playground runs on the developer's local machine, bypassing the need for token usage associated with cloud-based operations on the Shimoku platform. This is particularly beneficial for extensive testing and development, as it reduces the overhead costs typically incurred during the development process.

## Contributing

We welcome contributions to the Shimoku project! If you'd like to contribute, please follow these steps:

1. Fork the repository.
2. Create a new branch with a descriptive name, e.g. `feature/new-feature` or `bugfix/issue-123`.
3. Make your changes and commit them, following our code style guidelines.
4. Open a pull request against the main branch of the Shimoku repository.

Before submitting your pull request, please make sure your changes pass all tests and follow our coding conventions. We'll review your pull request and provide feedback as soon as possible.

## Contact

If you have any questions, suggestions, or issues, please feel free to reach out to us:

- [Discord](https://discord.gg/C87vWAug6q)
- Email: <contact@shimoku.com>

We're always happy to help and appreciate your feedback!

## License

Shimoku is licensed under the [MIT License](LICENSE). See the LICENSE file for more information.