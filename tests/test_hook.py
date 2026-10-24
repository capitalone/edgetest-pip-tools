"""Test the hook through the CLI."""

import platform
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import PropertyMock, call, patch

import click
import pytest
from click.testing import CliRunner
from edgetest.interface import cli
from edgetest.schema import EdgetestValidator, Schema
from edgetest.utils import parse_toml

from edgetest_pip_tools.plugin import addoption, get_reqfile, post_run_hook

TOML = """
[edgetest.envs.myenv]
upgrade = ["myupgrade"]
command = "pytest tests -m 'not integration'"
"""

TOML_ART = """
[project]
name = "toy_edgetest_toml"
version = "0.1.0"
description = "Fake description"
requires-python = ">=3.7"

dependencies = ["myupgrade"]

[edgetest.envs.myenv]
upgrade = ["myupgrade"]
command = "pytest tests -m 'not integration'"

[edgetest.pip_tools]
index_url = "myindexurl"
extras = "complete,another"
"""


TOML_EXTRAS = """
[edgetest.envs.myenv]
upgrade = ["myupgrade"]
command = "pytest tests -m 'not integration'"

[edgetest.pip_tools]
extras = "complete,another"
"""


PIP_LIST = """
[{"name": "myupgrade", "version": "0.2.0"}]
"""


def _normalize(calls):
    """Normalize captured ``Popen`` calls for comparison.

    ``edgetest`` >= 2026.10 always passes ``env=`` to ``Popen`` and resolves
    ``uv`` through ``find_uv_bin()``, so raw calls carry a full environment
    dict and an absolute executable path that vary per machine. Drop the
    ``env`` keyword and compare executables by name.
    """
    normalized = []
    for entry in calls:
        args, kwargs = entry
        kwargs = dict(kwargs)
        kwargs.pop("env", None)
        cmd = list(args[0])
        cmd[0] = Path(cmd[0]).name.removesuffix(".exe")
        normalized.append(call(tuple(cmd), *args[1:], **kwargs))
    return normalized


@pytest.mark.parametrize("config", [TOML, TOML_ART, TOML_EXTRAS])
def test_addoption_toml(config, tmpdir):
    """Test the addoption hook."""
    location = tmpdir.mkdir("mylocation")
    conf_loc = Path(str(location), "pyproject.toml")
    with open(conf_loc, "w") as outfile:
        outfile.write(config)

    schema = Schema()
    addoption(schema=schema)

    cfg = parse_toml(filename=conf_loc)

    validator = EdgetestValidator(schema=schema.schema)

    assert validator.validate(cfg)


@patch("edgetest.core.Popen", autospec=True)
@patch("edgetest.utils.Popen", autospec=True)
def test_update_reqs_toml(mock_popen, mock_cpopen):
    """Test calling ``pip-tools``."""
    mock_popen.return_value.communicate.return_value = (PIP_LIST, "error")
    type(mock_popen.return_value).returncode = PropertyMock(return_value=0)
    mock_cpopen.return_value.communicate.return_value = ("output", "error")
    type(mock_cpopen.return_value).returncode = PropertyMock(return_value=0)

    runner = CliRunner()

    with runner.isolated_filesystem() as loc:
        with open("pyproject.toml", "w") as outfile:
            outfile.write(TOML_ART)
        result = runner.invoke(cli, ["--config=pyproject.toml", "--export"])

    env_loc = Path(loc) / ".edgetest" / "myenv"
    if platform.system() == "Windows":
        py_loc = str(Path(env_loc) / "Scripts" / "python.exe")
    else:
        py_loc = str(Path(env_loc) / "bin" / "python")

    assert result.exit_code == 0
    assert _normalize(mock_popen.call_args_list) == [
        call(
            ("uv", "venv", f"{env_loc!s}"),
            stdout=-1,
            stderr=-1,
            universal_newlines=True,
        ),
        call(
            ("uv", "sync", "--inexact", f"--python={py_loc!s}"),
            stdout=-1,
            stderr=-1,
            universal_newlines=True,
        ),
        call(
            (
                "uv",
                "pip",
                "install",
                f"--python={py_loc!s}",
                "myupgrade",
                "--upgrade",
            ),
            stdout=-1,
            stderr=-1,
            universal_newlines=True,
        ),
        call(
            ("uv", "pip", "list", f"--python={py_loc!s}", "--format", "json"),
            stdout=-1,
            stderr=-1,
            universal_newlines=True,
        ),
        call(
            ("uv", "pip", "list", f"--python={py_loc!s}", "--format", "json"),
            stdout=-1,
            stderr=-1,
            universal_newlines=True,
        ),
        call(
            (
                "uv",
                "pip",
                "compile",
                "-U",
                "--extra=complete,another",
                "--index-url=myindexurl",
                "--output-file=requirements.txt",
                "pyproject.toml",
            ),
            stdout=-1,
            stderr=-1,
            universal_newlines=True,
        ),
    ]


def _ctx(config, requirements, export):
    ctx = click.Context(click.Command("edgetest"))
    ctx.params = {
        "config": config,
        "requirements": requirements,
        "export": export,
    }
    return ctx


def test_get_reqfile_setup_cfg_with_install_requires(tmpdir):
    cfg = Path(tmpdir, "setup.cfg")
    cfg.write_text("[options]\ninstall_requires =\n    myupgrade\n")

    assert get_reqfile(ctx=_ctx(str(cfg), "requirements.txt", True)) == cfg


def test_get_reqfile_setup_cfg_without_install_requires(tmpdir):
    cfg = Path(tmpdir, "setup.cfg")
    cfg.write_text("[metadata]\nname = toy\n")

    reqfile = get_reqfile(ctx=_ctx(str(cfg), "reqs.in", True))
    assert reqfile == Path("reqs.in")


def test_get_reqfile_pyproject_without_dependencies(tmpdir):
    conf = Path(tmpdir, "pyproject.toml")
    conf.write_text('[project]\nname = "toy"\nversion = "0.1.0"\n')

    reqfile = get_reqfile(ctx=_ctx(str(conf), "reqs.in", True))
    assert reqfile == Path("reqs.in")


def test_get_reqfile_other_config(tmpdir):
    reqfile = get_reqfile(ctx=_ctx("tox.ini", "reqs.in", True))
    assert reqfile == Path("reqs.in")


@patch("edgetest_pip_tools.plugin._run_command")
def test_post_run_hook_skips_without_export(mock_run):
    with _ctx("pyproject.toml", "requirements.txt", export=False):
        post_run_hook(testers=[], conf={})

    mock_run.assert_not_called()


@patch("edgetest_pip_tools.plugin._run_command")
def test_post_run_hook_survives_compile_error(mock_run):
    mock_run.side_effect = RuntimeError

    with _ctx("pyproject.toml", "requirements.txt", export=True):
        post_run_hook(
            testers=[SimpleNamespace(status=True)],
            conf={"pip_tools": {"extras": ["complete"], "index_url": "myindexurl"}},
        )

    mock_run.assert_called_once()


@patch("edgetest_pip_tools.plugin._run_command")
def test_post_run_hook_skips_when_tests_fail(mock_run):
    with _ctx("pyproject.toml", "requirements.txt", export=True):
        post_run_hook(testers=[SimpleNamespace(status=False)], conf={})

    mock_run.assert_not_called()
