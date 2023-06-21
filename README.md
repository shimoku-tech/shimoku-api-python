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

## About Shimoku

Shimoku enables you to build Data Products in just hours and allows you to create Predictive Analytics Products with Artificial Intelligence capabilities. In the software and automation era, data sharing is essential for businesses to thrive. Shimoku provides responsive progressive web apps that enable seamless data sharing between clients and providers.

Companies are more interested in predicting the future of their KPIs and trends rather than dwelling on past events. With Shimoku, you can build a Data App like Google Analytics in just hours without the need for a back-end, front-end, or DevOps. Additionally, you can integrate predictive suites into your Data App within minutes, transforming it into an AI App. Shimoku empowers you to deliver AI Apps that a single junior coder can build, iterate, and maintain.

### Introduction

Creating Data Apps usually requires a full-stack team of Data and IT specialists. Shimoku simplifies this process for Data professionals by allowing them to create Data Apps faster without the need for IT expertise. Shimoku reduces the workload of IT teams, which are often the bottleneck in digital businesses while creating new products and value for your clients.

By using Shimoku, a typical flow such as:

![Schema without Shimoku](https://1111601832-files.gitbook.io/~/files/v0/b/gitbook-x-prod.appspot.com/o/spaces%2FUlHTfmIZY46Z1EDfyGMz%2Fuploads%2FVVRucS06NScH1ZrKBcZZ%2Fschema-old-team.png?alt=media&token=7105e7b4-ac2b-430d-8ad4-a653f29b3716)

Is transformed into:

![Hence, an entire IT full-stack team is replaced by Shimoku.](https://1111601832-files.gitbook.io/~/files/v0/b/gitbook-x-prod.appspot.com/o/spaces%2FUlHTfmIZY46Z1EDfyGMz%2Fuploads%2F0SertLANqgV3ZoOlq1VA%2Fschema-shimoku-breakout.png?alt=media&token=360d0c11-ebee-4e0d-9a7f-32c2a68f5928)

## Quickstart

### Step 1 - Create an account

| 1 | 2 |
| --- | --- |
| **Go** to [shimoku.io](https://shimoku.io/sign-up) to **create an account** | **Review** your inbox and **confirm** account |
| ![Image 1](https://1111601832-files.gitbook.io/~/files/v0/b/gitbook-x-prod.appspot.com/o/spaces%2FUlHTfmIZY46Z1EDfyGMz%2Fuploads%2Fac4QIR03uC5NyMQImZ15%2Fimage.png?alt=media&token=b0c1ff9d-cbb4-4d1c-94f1-a59f18d9452c) | ![Image 2](https://1111601832-files.gitbook.io/~/files/v0/b/gitbook-x-prod.appspot.com/o/spaces%2FUlHTfmIZY46Z1EDfyGMz%2Fuploads%2FEYAYtVOmKPMJWXaeIPrj%2Fimage.png?alt=media&token=80b1e962-97cb-48bd-bca4-5767d0dc9f23) |

| 3 | 4 |
| --- | --- |
| Click on "**Return to Sign In section"** and sign in with your credentials | Click your **Profile button** on the top right and go to **"Settings"**. Inside **"Information for developers"** click on "**Create"** to generate your API Token and save this information, the **"Universe ID"** and the **"Business ID".** |
| ![Image 3](https://1111601832-files.gitbook.io/~/files/v0/b/gitbook-x-prod.appspot.com/o/spaces%2FUlHTfmIZY46Z1EDfyGMz%2Fuploads%2FyI0DKtYpBCW98QiBdL2O%2Fimage.png?alt=media&token=4fe0bc0f-e73c-4c30-bb43-25dce3b7d380) | ![Image 4](https://1111601832-files.gitbook.io/~/files/v0/b/gitbook-x-prod.appspot.com/o/spaces%2FUlHTfmIZY46Z1EDfyGMz%2Fuploads%2FlyWlkp41bohT78JKpRaZ%2Fimage.png?alt=media&token=1932af00-da7f-4828-ab83-49ee23dd55fb) |

### Step 2 - Install the Library

To use Shimoku’s API first install our SDK library.

See it from Github at:

[https://github.com/shimoku-tech/shimoku-api-python](https://github.com/shimoku-tech/shimoku-api-python)

And in your `Python +3.9` install it

```python
pip install shimoku-api-python
```

**_NOTE:_**

If you want to install versions prior to v.0.13.3 (this one included), you'll need to install the following requirements first:
```
pandas==1.5.2
requests==2.28.1
datetime==4.9
json5==0.9.10
shimoku-components-catalog==0.2
```

### Step 3 - Start Client, Plotting and Menu Handling

Go ahead and copy-paste to see 🪄

```python
from os import getenv
import shimoku_api_python as Shimoku

access_token = getenv('SHIMOKU_TOKEN')
universe_id: str = getenv('UNIVERSE_ID')
workspace_id: str = getenv('WORKSPACE_ID')

s = Shimoku.Client(
    access_token=access_token,
    universe_id=universe_id,
)
s.set_workspace(uuid=workspace_id)

s.set_board('Custom Board')

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

```

Once you execute this piece of code you can see the following plot in your shimoku.io page:

![First Shimoku App](https://1111601832-files.gitbook.io/~/files/v0/b/gitbook-x-prod.appspot.com/o/spaces%2FUlHTfmIZY46Z1EDfyGMz%2Fuploads%2FmCPi73lrkbroOqpLDNLI%2Fimatge.png?alt=media&token=58bd4a30-a316-4237-9319-ab9fc5552ed1)

### Step 4 - Board

As can be seen in the previous image the first element in the menu is called 'Custom Board', this element is a board. The boards are necessary for the contents of an app to be seen, if an app is not included in a dashboard it will not appear in the page. For this reason the SDK always attaches the apps to a dashboard when creating content, ideally the user should define which name to use for the dashboard, but when it is not specified it will use the name 'Default Name'.

The method to specify the board's name that the SDK should use is:

```python
s.set_board(name: str)
```

This will ensure that all the apps used after that point are included in dashboard_name.

**_NOTE:_**

Multiple Dashboards Issue

There is a possible issue that can arise from executing code multiple times with different dashboard names, as it can be seen in the result two dashboards have been created with the same app attached.

In case this wasn't the expected result, it can be solved very easily using the method:

```python
s.boards.force_delete_board(name: str, uuid: str)
```

This will delete a specified dashboard, but first it will delete all of it's links to it's apps, so it will always be able to delete an existing dashboard without having to touch the app. In this case the method should be used like this:

```python
s.boards.force_delete_board(name='Default Name')
```

Then there will only exist the 'Custom Dashboard' linking to the 'catalog' app.

![Multiple Dashboards](https://1111601832-files.gitbook.io/~/files/v0/b/gitbook-x-prod.appspot.com/o/spaces%2FUlHTfmIZY46Z1EDfyGMz%2Fuploads%2FFsixEerSY9eLJr6zK4ni%2Fimatge.png?alt=media&token=b27eb7f7-565d-4e79-8df5-cae57ab456fd)

### Step 5 - Productivity boost

#### Verbosity

There is now the option to monitor the SDK flow of execution, with three levels of verbosity. This will help to know where the error occurred, so it will make bugfixing a lot easier, It also outputs how much time the function call has taken to quickly profile code. To enable it you just have to set the parameter verbosity from the client to INFO or DEBUG.

```python
s = Shimoku.Client(
    access_token=access_token,
    universe_id=universe_id,
    verbosity='INFO',
)
```

The INFO keyword will be the most useful for visualizing the execution while DEBUG is made so it outputs as much information as possible.

You can also set it to WARNING but this is the default behavior and will have no effect, it will output only warnings and errors.

The logging level of the Shimoku SDK can be configured dynamically during execution by calling the configure_logging function with the desired verbosity level (either 'DEBUG', 'INFO', or 'WARNING') and an optional channel to write the log output to. This allows for fine-grained control over the logging behavior and output, making it easier to debug and profile the SDK's execution.

#### Asynchronous execution

Asynchronous execution means that code execution doesn't need to stop for requests, freeing up time to make more requests. To enable it, simply set the async_execution parameter to True when creating the client object:

```python
s = Shimoku.Client(
    access_token=access_token,
    universe_id=universe_id,
    business_id=business_id,
    verbosity='INFO',
    async_execution=True,
)
```

By default, execution is set to sequential. You can toggle between sequential and asynchronous execution using the following functions:

```python
s.activate_async_execution()
s.activate_sequential_execution()
```

When asynchronous execution is enabled, tasks are added to a task pool and executed once a strictly sequential task is reached. A function has been added to allow users to trigger the execution of tasks, which is s.run().

**_NOTE:_**
Be sure to call s.run() at the end of your code to ensure all tasks are executed before the program terminates.

```python
from os import getenv
import shimoku_api_python as Shimoku

access_token = getenv('SHIMOKU_TOKEN')
universe_id: str = getenv('UNIVERSE_ID')
workspace_id: str = getenv('WORKSPACE_ID')

s = Shimoku.Client(
    access_token=access_token,
    universe_id=universe_id,
    verbosity='INFO',
    async_execution=True,
)
s.set_workspace(workspace_id)

s.set_board('Custom Dashboard')

s.set_menu_path('catalog', 'bar-example')

language_expressiveness = pd.read_html(
    'https://en.wikipedia.org/wiki/Comparison_of_programming_languages')[2]

s.plt.bar(
    order=0, title='Language expressiveness',
    data=language_expressiveness, x='Language',
    y=['Statements ratio[48]', 'Lines ratio[49]'],
)

s.run()
```

## Contributing

We welcome contributions to the Shimoku project! If you'd like to contribute, please follow these steps:

1. Fork the repository.
2. Create a new branch with a descriptive name, e.g. `feature/new-feature` or `bugfix/issue-123`.
3. Make your changes and commit them, following our code style guidelines.
4. Open a pull request against the main branch of the Shimoku repository.

Before submitting your pull request, please make sure your changes pass all tests and follow our coding conventions. We'll review your pull request and provide feedback as soon as possible.

## Contact

If you have any questions, suggestions, or issues, please feel free to reach out to us:

- [Discord](https://discord.com/channels/1076588792024137879/1096371108665626676)
- Email: contact@shimoku.com

We're always happy to help and appreciate your feedback!

## License

Shimoku is licensed under the [MIT License](LICENSE). See the LICENSE file for more information.