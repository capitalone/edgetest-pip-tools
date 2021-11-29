"""Plugin for refreshing a locked requirements file."""

from configparser import ConfigParser
from pathlib import Path
from typing import Dict, List

import click
import pluggy
from edgetest.logger import get_logger
from edgetest.schema import Schema
from edgetest.utils import _run_command

LOG = get_logger(__name__)

hookimpl = pluggy.HookimplMarker("edgetest")


@hookimpl
def addoption(schema: Schema):
    """Add configuration options for pip-tools.

    Parameters
    ----------
    schema : Schema
        The schema class.
    """
    schema.add_globaloption(
        "pip_tools",
        {
            "type": "dict",
            "schema": {
                "extras": {
                    "type": "list",
                    "coerce": "listify",
                    "schema": {"type": "string"},
                },
                "index_url": {"type": "string"},
            },
        },
    )


def get_reqfile(ctx: click.Context) -> Path:
    """Get the requirements file to supply to ``pip-tools``.

    Parameters
    ----------
    ctx : click.Context
        The context for the CLI call.

    Returns
    -------
    Path
        Path to the requirements file.
    """
    if Path(ctx.params["config"]).name == "setup.cfg":
        # Check for the install_requires
        parser = ConfigParser()
        parser.read(Path(ctx.params["config"]))
        if "options" in parser and parser.get("options", "install_requires"):
            reqfile = Path(ctx.params["config"])
        else:
            reqfile = Path(ctx.params["requirements"])
    else:
        reqfile = Path(ctx.params["requirements"])

    return reqfile


@hookimpl(tryfirst=True)
def post_run_hook(testers: List, conf: Dict):
    """Refresh a locked requirements file based on the test output."""
    ctx = click.get_current_context()
    if not ctx.params["export"]:
        LOG.info("Skipping ``pip-tools`` as the requirements have not been updated.")
    elif testers[-1].status:
        reqfile = get_reqfile(ctx=ctx)
        try:
            options = []
            if conf.get("pip_tools", {}).get("extras"):
                options += [f"--extra={extra}" for extra in conf["pip_tools"]["extras"]]
            if conf.get("pip_tools", {}).get("index_url"):
                options.append(f"--index-url={conf['pip_tools']['index_url']}")

            _run_command(
                testers[-1].python_path,
                "-m",
                "piptools",
                "compile",
                "-U",
                *options,
                "--output-file=requirements.txt",
                str(reqfile),
            )
        except RuntimeError:
            LOG.info("Unable to update the locked requirements file")
    else:
        LOG.info("Skipping ``pip-tools`` refresh as the tests didn't pass.")
