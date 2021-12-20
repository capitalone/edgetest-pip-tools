"""Test the hook through the CLI."""

import platform
from pathlib import Path
from unittest.mock import PropertyMock, call, patch

import pytest
from click.testing import CliRunner
from edgetest.interface import cli
from edgetest.schema import EdgetestValidator, Schema
from edgetest.utils import parse_cfg

from edgetest_pip_tools.plugin import addoption

CFG = """
[edgetest.envs.myenv]
upgrade =
    myupgrade
command =
    pytest tests -m 'not integration'
"""

CFG_ART = """
[options]
install_requires =
    myupgrade

[edgetest.envs.myenv]
upgrade =
    myupgrade
command =
    pytest tests -m 'not integration'

[edgetest.pip_tools]
index_url = myindexurl
"""


CFG_EXTRAS = """
[edgetest.envs.myenv]
upgrade =
    myupgrade
command =
    pytest tests -m 'not integration'

[edgetest.pip_tools]
extras =
    complete
"""


PIP_LIST = """
[{"name": "myupgrade", "version": "0.2.0"}]
"""


TABLE_OUTPUT = """

============= =============== =================== =================
Environment   Passing tests   Upgraded packages   Package version
============= =============== =================== =================
myenv         True            myupgrade           0.2.0
============= =============== =================== =================
"""


@pytest.mark.parametrize("config", [CFG, CFG_ART, CFG_EXTRAS])
def test_addoption(config, tmpdir):
    """Test the addoption hook."""
    location = tmpdir.mkdir("mylocation")
    conf_loc = Path(str(location), "myconfig.ini")
    with open(conf_loc, "w") as outfile:
        outfile.write(config)

    schema = Schema()
    addoption(schema=schema)

    cfg = parse_cfg(filename=conf_loc)

    validator = EdgetestValidator(schema=schema.schema)

    assert validator.validate(cfg)


@patch("edgetest.lib.EnvBuilder", autospec=True)
@patch("edgetest.core.Popen", autospec=True)
@patch("edgetest.utils.Popen", autospec=True)
def test_update_reqs(mock_popen, mock_cpopen, mock_builder):
    """Test calling ``pip-tools``."""
    mock_popen.return_value.communicate.return_value = (PIP_LIST, "error")
    type(mock_popen.return_value).returncode = PropertyMock(return_value=0)
    mock_cpopen.return_value.communicate.return_value = ("output", "error")
    type(mock_cpopen.return_value).returncode = PropertyMock(return_value=0)

    runner = CliRunner()

    with runner.isolated_filesystem() as loc:
        with open("setup.cfg", "w") as outfile:
            outfile.write(CFG_ART)

        result = runner.invoke(cli, ["--config=setup.cfg", "--export"])

    env_loc = Path(loc) / ".edgetest" / "myenv"
    if platform.system() == "Windows":
        py_loc = str(Path(env_loc)  / "Scripts" / "python")
    else:
        py_loc = str(Path(env_loc)  / "bin" / "python")

    assert result.exit_code == 0
    assert mock_popen.call_args_list == [
        call(
            (f"{str(py_loc)}", "-m", "pip", "install", "."),
            stdout=-1,
            universal_newlines=True,
        ),
        call(
            (
                f"{str(py_loc)}",
                "-m",
                "pip",
                "install",
                "myupgrade",
                "--upgrade",
            ),
            stdout=-1,
            universal_newlines=True,
        ),
        call(
            (f"{str(py_loc)}", "-m", "pip", "list", "--format", "json"),
            stdout=-1,
            universal_newlines=True,
        ),
        call(
            (f"{str(py_loc)}", "-m", "pip", "list", "--format", "json"),
            stdout=-1,
            universal_newlines=True,
        ),
        call(
            (
                f"{str(py_loc)}",
                "-m",
                "piptools",
                "compile",
                "-U",
                "--index-url=myindexurl",
                "--output-file=requirements.txt",
                "setup.cfg",
            ),
            stdout=-1,
            universal_newlines=True,
        ),
    ]
