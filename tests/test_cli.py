"""CLI foundation tests."""

from typer.testing import CliRunner

from xma import __version__
from xma.cli import app

runner = CliRunner()


def test_help_lists_product_and_version_command() -> None:
    result = runner.invoke(app, ["--help"])

    assert result.exit_code == 0
    assert "Catalog and archive public audiovisual content from X" in result.stdout
    assert "version" in result.stdout


def test_no_arguments_displays_help() -> None:
    result = runner.invoke(app)

    assert result.exit_code == 0
    assert "Usage:" in result.stdout


def test_version_is_human_readable() -> None:
    result = runner.invoke(app, ["version"])

    assert result.exit_code == 0
    assert result.stdout.strip() == f"X Media Archiver {__version__}"


def test_short_version_is_machine_readable() -> None:
    result = runner.invoke(app, ["version", "--short"])

    assert result.exit_code == 0
    assert result.stdout.strip() == __version__
