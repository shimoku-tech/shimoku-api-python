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

### Step 1 - Install the library

```bash
pip install shimoku-api-python
```

### Step 2 - Configure the client

```python
from os import getenv
import shimoku_api_python as Shimoku

access_token = getenv('SHIMOKU_TOKEN')
universe_id: str = getenv('UNIVERSE_ID')
business_id: str = getenv('BUSINESS_ID')

s = Shimoku.Client(
    access_token=access_token,
    universe_id=universe_id,
    business_id=business_id,
)
```

### Step 3 - Create plots

```python
s.plt.set_dashboard('Custom Dashboard')

language_expressiveness = pd.read_html(
    'https://en.wikipedia.org/wiki/Comparison_of_programming_languages')[2]

s.plt.bar(
  menu_path='catalog/bar-example', order=0, 
  title='Language expressiveness',
  data=language_expressiveness, x='Language',
  y=['Statements ratio[48]', 'Lines ratio[49]'],
)
```

### Step 4 (Optional) - Productivity boost

Enable asynchronous execution:

```python
s = Shimoku.Client(
    access_token=access_token,
    universe_id=universe_id,
    business_id=business_id,
    verbosity='INFO',
    async_execution=True,
)
```

Don't forget to call `s.run()` at the end of your code to ensure all tasks are executed before the program terminates.

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
