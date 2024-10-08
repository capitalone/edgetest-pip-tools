Quick Start
===========

Install
-------

Installation from PyPI:

.. code-block:: console

    $ python -m pip install edgetest-pip-tools


Installation from conda-forge:

.. code:: console

    $ conda install -c conda-forge edgetest-pip-tools


Getting Started
---------------

This `edgetest` plugin runs after the test execution. If the last environment successfully
passes, this plugin will refresh `requirements.txt` using `uv pip compile`. To use this plugin,
supply ``--export`` to your CLI call:


.. tabs::

    .. tab:: .cfg

        .. code-block:: console

            $ edgetest --config setup.cfg --export

    .. tab:: .toml

        .. code-block:: console

            $ edgetest --config pyproject.toml --export

If you want to specify a PyPI index, supply `index_url` in your configuration:

.. tabs::

    .. tab:: .cfg

        .. code-block:: ini

            [edgetest.pip_tools]
            index_url = https://myindex.com

    .. tab:: .toml

        .. code-block:: toml

            [edgetest.pip_tools]
            index_url = "https://myindex.com"


If you want to include extra installations in your `uv pip compile` call add a newline-separated list of
extras:


.. tabs::

    .. tab:: .cfg

        .. code-block:: ini

            [edgetest.pip_tools]
            extras =
                complete
                another

    .. tab:: .toml

        .. code-block:: toml

            [edgetest.pip_tools]
            extras = "complete,another"


.. important::

    Extra installations are only available with PEP-517 compliant installations.
