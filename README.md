# pip-tools integration for edgetest

![python-3.7](https://img.shields.io/badge/python-3.7-green.svg)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/ambv/black)

[Full Documentation](https://capitalone.github.io/edgetest-pip-tools/)

Table Of Contents
-----------------

- [Install](#install)
- [Getting Started](#getting-started)
- [Options](#options)
- [Examples](#examples)
- [Contributing](#contributing)
- [License](#license)

Install
-------

Installation from PyPI:

```console
$ python -m pip install edgetest-pip-tools
```

Getting Started
---------------

This `edgetest` plugin runs after the test execution. If the last environment successfully
passes, this plugin will refresh `requirements.txt` using `pip-tools`. To use this plugin,
you must use the ``--export`` flag in your CLI call:

```console
$ edgetest --config setup.cfg --export
```

If you want to specify a PyPI index supply `index_url` in your configuration:

```ini
[edgetest.pip_tools]
index_url = ...
```

If you want to include extra installations in your `pip-tools` call (only available for PEP-517
compliant builds), add a newline-separated list of extras:

```ini
[edgetest.pip_tools]
extras =
    complete
```

Contributing
------------
