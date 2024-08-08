# pip-tools integration for edgetest

![PyPI - Python Version](https://img.shields.io/pypi/pyversions/edgetest-pip-tools)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![PyPI version](https://badge.fury.io/py/edgetest-pip-tools.svg)](https://badge.fury.io/py/edgetest-pip-tools)
[![Anaconda-Server Badge](https://anaconda.org/conda-forge/edgetest-pip-tools/badges/version.svg)](https://anaconda.org/conda-forge/edgetest-pip-tools)


[Full Documentation](https://capitalone.github.io/edgetest-pip-tools/)

Table Of Contents
-----------------

- [Install](#install)
- [Getting Started](#getting-started)
- [Contributing](#contributing)
- [License](#license)

Install
-------

Installation from PyPI:

```console
$ python -m pip install edgetest-pip-tools
```


Installation from conda-forge:

```console
$ conda install -c conda-forge edgetest-pip-tools
```


Getting Started
---------------

This `edgetest` plugin runs after the test execution. If the last environment successfully
passes, this plugin will refresh `requirements.txt` using `uv pip compile`. To use this plugin,
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

See our [developer documentation](https://capitalone.github.io/edgetest-pip-tools/developer.html).

We welcome and appreciate your contributions! Before we can accept any contributions, we ask that you please be sure to
sign the [Contributor License Agreement (CLA)](https://cla-assistant.io/capitalone/edgetest-pip-tools)

This project adheres to the [Open Source Code of Conduct](https://developer.capitalone.com/resources/code-of-conduct/).
By participating, you are expected to honor this code.

License
-------

Apache-2.0
