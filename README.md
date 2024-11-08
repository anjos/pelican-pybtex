# Repository Coverage

[Full report](https://htmlpreview.github.io/?https://github.com/anjos/pelican-pybtex/blob/python-coverage-comment-action-data/htmlcov/index.html)

| Name                                       |    Stmts |     Miss |   Cover |   Missing |
|------------------------------------------- | -------: | -------: | ------: | --------: |
| src/pelican/plugins/pybtex/\_\_init\_\_.py |       17 |        0 |    100% |           |
| src/pelican/plugins/pybtex/generator.py    |       47 |        5 |     89% |51-55, 107-109 |
| src/pelican/plugins/pybtex/injector.py     |       61 |        5 |     92% |55, 74, 101-102, 114 |
| src/pelican/plugins/pybtex/signals.py      |        2 |        0 |    100% |           |
| src/pelican/plugins/pybtex/style.py        |       30 |        0 |    100% |           |
| src/pelican/plugins/pybtex/utils.py        |       56 |        6 |     89% |38, 79-80, 221-226 |
|                                  **TOTAL** |  **213** |   **16** | **92%** |           |


## Setup coverage badge

Below are examples of the badges you can use in your main branch `README` file.

### Direct image

[![Coverage badge](https://raw.githubusercontent.com/anjos/pelican-pybtex/python-coverage-comment-action-data/badge.svg)](https://htmlpreview.github.io/?https://github.com/anjos/pelican-pybtex/blob/python-coverage-comment-action-data/htmlcov/index.html)

This is the one to use if your repository is private or if you don't want to customize anything.

### [Shields.io](https://shields.io) Json Endpoint

[![Coverage badge](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/anjos/pelican-pybtex/python-coverage-comment-action-data/endpoint.json)](https://htmlpreview.github.io/?https://github.com/anjos/pelican-pybtex/blob/python-coverage-comment-action-data/htmlcov/index.html)

Using this one will allow you to [customize](https://shields.io/endpoint) the look of your badge.
It won't work with private repositories. It won't be refreshed more than once per five minutes.

### [Shields.io](https://shields.io) Dynamic Badge

[![Coverage badge](https://img.shields.io/badge/dynamic/json?color=brightgreen&label=coverage&query=%24.message&url=https%3A%2F%2Fraw.githubusercontent.com%2Fanjos%2Fpelican-pybtex%2Fpython-coverage-comment-action-data%2Fendpoint.json)](https://htmlpreview.github.io/?https://github.com/anjos/pelican-pybtex/blob/python-coverage-comment-action-data/htmlcov/index.html)

This one will always be the same color. It won't work for private repos. I'm not even sure why we included it.

## What is that?

This branch is part of the
[python-coverage-comment-action](https://github.com/marketplace/actions/python-coverage-comment)
GitHub Action. All the files in this branch are automatically generated and may be
overwritten at any moment.