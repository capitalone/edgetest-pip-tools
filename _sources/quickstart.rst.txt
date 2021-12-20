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
passes, this plugin will refresh `requirements.txt` using `pip-tools`. To use this plugin,
supply ``--export`` to your CLI call:

.. code-block:: console

    $ edgetest --config setup.cfg --export

If you want to specify a PyPI index, supply `index_url` in your configuration:

.. code-block:: ini

    [edgetest.pip_tools]
    index_url = ...

If you want to include extra installations in your `pip-tools` call add a newline-separated list of
extras:

.. code-block:: ini

    [edgetest.pip_tools]
    extras =
        complete

.. important::

    Extra installations are only available with PEP-517 compliant installations.
