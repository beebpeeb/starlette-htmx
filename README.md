# Starlette + htmx

A small Python web application which uses [starlette][] and [htmx][]
to demonstrate an approach to [HTML over the Wire][html-over-the-wire].

Data validation is provided by [pydantic][].

HTML templating is provided by [jinja2][].

## Pre-requisites

This application requires Python 3.10 or higher.

It is recommended to use [pyenv][] to manage Python installations.

The official [Visual Studio Code Python plugin][vscode-plugin] is very good.

Enable [pylint][], [mypy][], [black][] and [bandit][] in your editor
if you want to take advantage of formatting, linting and type checking support.

More info can be found [here][vscode-info].

## Install

```
$ python3 -m venv .venv
$ source .venv/bin/activate
(.venv) $ pip3 install -r requirements.txt
```

## Run

```
(.venv) $ python3 main.py
```

Open [localhost:8080](http://localhost:8080/) in your web browser to see the running app.

## Test

There are currently no tests.



[bandit]: https://pypi.org/project/bandit/
[black]: https://pypi.org/project/black/
[html-over-the-wire]: https://dev.to/rajasegar/html-over-the-wire-is-the-future-of-web-development-542c
[htmx]: https://htmx.org/
[jinja2]: https://pypi.org/project/Jinja2/
[mypy]: https://pypi.org/project/mypy/
[pydantic]: https://pydantic-docs.helpmanual.io/
[pyenv]: https://github.com/pyenv/pyenv
[pylint]: https://pypi.org/project/pylint/
[starlette]: https://pypi.org/project/starlette/
[vscode-info]: https://code.visualstudio.com/docs/languages/python
[vscode-plugin]: https://marketplace.visualstudio.com/items?itemName=ms-python.python
